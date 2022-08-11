from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from import_export.admin import ImportMixin
from .models import SubscribedUser, User
from .resources import SubscribedUserResource, UserResource


class SubscribedUserAdmin(ImportMixin, admin.ModelAdmin):
    resource_class = SubscribedUserResource


class MyUserAdmin(ImportMixin, UserAdmin, admin.ModelAdmin):
    resource_class = UserResource


admin.site.register(User, MyUserAdmin)
admin.site.register(SubscribedUser, SubscribedUserAdmin)
