from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from accounts.models import UserProfile as User
from django.urls import reverse_lazy, reverse
from django.views.generic import UpdateView, ListView
from django.utils.decorators import method_decorator
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.utils import timezone
from django.db.models import Count
from django.core.paginator import Paginator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import render_to_string
import humanize
import datetime
import json
from board_app.forms import (
    NewTopicForm, PostForm, UpdateTopicForm, BoardForm
)
from board_app.models import (
    Board, Topic, Post
)
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash


# Create your views here.


def home_view(request):
    board_list = Board.objects.all()
    page = request.GET.get('page', 1)
    print(type(page))
    paginator = Paginator(board_list, 5)
    print(paginator)
    try:
        boards = paginator.page(page)
    except PageNotAnInteger:
        boards = paginator.page(1)
    except EmptyPage:
        boards = paginator.page(paginator.num_pages)

    return render(request, 'home_page.html', {'boards': boards, 'page': page})


def save_board_form(request, form, template_name, page, message):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, message)
            data['form_is_valid'] = True
            boards = Board.objects.all()
            paginator = Paginator(boards, 5)
            try:
                boards = paginator.page(page)
            except PageNotAnInteger:
                boards = paginator.page(1)
            except EmptyPage:
                boards = paginator.page(paginator.num_pages)
            data['html_board_list'] = render_to_string('includes/partial_list.html', {
                'boards': boards,
                'page': page
            })

        else:
            data['form_is_valid'] = False
    context = {'form': form, 'page': page}
    data['html_form'] = render_to_string(
        template_name, context, request=request)
    return JsonResponse(data)


def create_board(request, page):
    message = 'board created'
    if request.method == 'POST':
        form = BoardForm(request.POST)
    else:
        form = BoardForm()
    return save_board_form(request, form, 'includes/partial_create.html', page, message)


def board_update(request, pk, page):
    board = get_object_or_404(Board, pk=pk)
    message = 'board updated'
    if request.method == 'POST':
        form = BoardForm(request.POST, instance=board)

    else:
        form = BoardForm(instance=board)
    return save_board_form(request, form, 'includes/partial_update.html', page, message)


def board_delete(request, pk, page):
    board = get_object_or_404(Board, pk=pk)
    data = dict()

    if request.method == 'POST':
        messages.success(request, 'board deleted')
        board.delete()
        data['form_is_valid'] = True
        boards = Board.objects.all()
        paginator = Paginator(boards, 5)
        try:
            boards = paginator.page(page)
        except PageNotAnInteger:
            boards = paginator.page(1)
        except EmptyPage:
            boards = paginator.page(paginator.num_pages)
        data['html_board_list'] = render_to_string('includes/partial_list.html', {
            'boards': boards,
            'page': page
        })
    else:
        context = {'board': board, 'page': page}
        data['html_form'] = render_to_string(
            'includes/partial_delete.html', context, request=request)

    return JsonResponse(data)


class TopicListView(ListView):
    model = Topic
    context_object_name = 'topics'
    template_name = 'topics.html'
    paginate_by = 15

    def get_context_data(self, **kwargs):
        kwargs['board'] = self.board
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.board = get_object_or_404(Board, pk=self.kwargs.get('pk'))
        queryset = self.board.topics.order_by(
            '-last_updated').annotate(replies=Count('posts') - 1)
        return queryset


@login_required
def new_topic(request, pk):
    print('ffffffffff')
    board = get_object_or_404(Board, pk=pk)
    form = NewTopicForm(request.POST)
    if form.is_valid():
        topic = form.save(commit=False)
        topic.board = board
        topic.starter = request.user  # <- here
        topic.save()
        Post.objects.create(
            message=form.cleaned_data.get('message'),
            topic=topic,
            created_by=request.user  # <- and here
        )
        return redirect('topic_posts', pk=pk, topic_pk=topic.pk)  # <- here
    return render(request, 'new_topic.html', {'board': board, 'form': form})


def update_topic(request, pk, topic_pk):
    print("\n\n\nQQ\n\n\n")

    data = dict()
    if request.method == 'POST':
        form = UpdateTopicForm(request.POST)
        if form.is_valid():
            topic = get_object_or_404(Topic, pk=topic_pk)
            topic.subject = form.cleaned_data['subject']
            topic.last_updated = timezone.now()
            topic.save()
            data['form_is_valid'] = True
            data['board_pk'] = pk
            data['topic_pk'] = topic_pk
            data['naturaldelta'] = humanize.naturaldelta(
                datetime.datetime.now())
        else:
            data['form_is_valid'] = False

    context = {
        'form': form,
        'board_pk': pk,
        'topic_pk': topic_pk
    }

    data['html_form'] = render_to_string(
        template_name='includes/partial_create.html',
        context=context,
        request=request,
    )
    return JsonResponse(data)


def delete_topic(request, pk, topic_pk):
    Topic.objects.filter(pk=topic_pk).delete()
    return JsonResponse({})


class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'topic_posts.html'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        session_key = 'viewed_topic_{}'.format(self.topic.pk)  # <-- here
        if not self.request.session.get(session_key, False):
            self.topic.views += 1
            self.topic.save()
            self.request.session[session_key] = True  # <-- until here

        kwargs['topic'] = self.topic
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.topic = get_object_or_404(Topic, board__pk=self.kwargs.get(
            'pk'), pk=self.kwargs.get('topic_pk'))
        queryset = self.topic.posts.order_by('created_at')
        return queryset


@login_required
def reply_topic(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    form = PostForm(request.POST)
    if form.is_valid():
        post = form.save(commit=False)
        post.topic = topic
        post.created_by = request.user
        post.save()

        topic.last_updated = timezone.now()
        topic.save()

        topic_url = reverse('topic_posts', kwargs={
                            'pk': pk, 'topic_pk': topic_pk})
        topic_post_url = '{url}?page={page}#{id}'.format(
            url=topic_url,
            id=post.pk,
            page=topic.get_page_count()
        )
        return redirect(topic_post_url)
    return render(request, 'reply_topic.html', {'topic': topic, 'form': form})


@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    fields = ('message',)
    template_name = 'edit_post.html'
    pk_url_kwarg = 'post_pk'
    context_object_name = 'post'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()
        return redirect('topic_posts', pk=post.topic.board.pk, topic_pk=post.topic.pk)


def put_in_boards(request):
    try:
        from_ = (Board.objects.order_by('-pk')[0].id + 1)
    except:
        from_ = 1
    plus_ = 10
    for i in range(from_, from_ + plus_):
        board = Board.objects.create(
            name='Board #{0}'.format(i),
            description='Description #{0}'.format(i)
        )
        for j in range(from_, from_ + plus_):
            topic = Topic.objects.create(
                subject='Subject #{0}'.format(j),
                starter=request.user,
                board=board,
                views=0
            )
            for k in range(from_, from_ + plus_):
                Post.objects.create(
                    message='Message #{0}'.format(j),
                    topic=topic,
                    created_by=request.user
                )
    return HttpResponse('Completed')
