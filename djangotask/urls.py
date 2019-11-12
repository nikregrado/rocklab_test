"""djangotask URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.contrib.auth import views as auth_views
from accounts import views as accounts_views
from board_app import views as views
from django.urls import path, re_path, include
from django.contrib import admin
from django.contrib.flatpages import views as views_flatpage
# from django.conf.urls.static import static
# from djangotask import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view, name='home'),
    path('create/<str:page>', views.create_board, name='create_board'),
    path('<int:pk>/update/<str:page>/',
         views.board_update, name='board_update'),
    path('<int:pk>/delete/<str:page>/',
         views.board_delete, name='board_delete'),
    path('boards/<int:pk>/', views.TopicListView.as_view(), name='board_topics'),
    path('boards/<int:pk>/new/', views.new_topic, name='new_topic'),
    path('boards/<int:pk>/topics/<int:topic_pk>/',
         views.PostListView.as_view(), name='topic_posts'),
    path('boards/<int:pk>/topics/<int:topic_pk>/reply/',
         views.reply_topic, name='reply_topic'),
    path('boards/<int:pk>/topics/<int:topic_pk>/posts/<int:post_pk>/edit/',
         views.PostUpdateView.as_view(), name='edit_post'),
    path('signup/', accounts_views.signup, name='signup'),
    path('signup/reader/', accounts_views.ReaderSignUpView.as_view(),
         name='signup_as_reader'),
    path('signup/blogger/', accounts_views.BloggerSignUpView.as_view(),
         name='signup_as_blogger'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('reset/',
         auth_views.PasswordResetView.as_view(
             template_name='password_reset.html',
             email_template_name='password_reset_email.html',
             subject_template_name='password_reset_subject.txt'
         ),
         name='password_reset'),
    path('reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='password_reset_done.html'),
         name='password_reset_done'),
    re_path(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            auth_views.PasswordResetConfirmView.as_view(
                template_name='password_reset_confirm.html'),
            name='password_reset_confirm'),
    path('reset/complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='password_reset_complete.html'),
         name='password_reset_complete'),
    path('settings/account/',
         accounts_views.UserUpdateView.as_view(), name='my_account'),
    path('putin/', views.put_in_boards, name='putin'),
    path('privacy/', views_flatpage.flatpage,
         {'url': '/privacy/'}, name='about'),
    path('terms/', views_flatpage.flatpage,
         {'url': '/terms/'}, name='license'),
    # static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
]
