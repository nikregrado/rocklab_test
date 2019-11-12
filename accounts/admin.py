from django.contrib import admin
from accounts.models import (
    Hobby, Interest, UserProfile as User, Reader, Blogger
)

# Register your models here.


admin.site.register(Hobby)
admin.site.register(Interest)
admin.site.register(User)
admin.site.register(Reader)
admin.site.register(Blogger)
