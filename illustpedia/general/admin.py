from django.contrib import admin
from .models import IPUser


class UserAdmin(admin.ModelAdmin):
    fieldsets = [
        ('username', {'fields': ['username']}),
        ('nickname', {'fields': ['nickname']}),
        ('email', {'fields': ['email']}),
        ('password', {'fields': ['password']}),
        ('is_active', {'fields': ['is_active']}),
        ('is_staff', {'fields': ['is_staff']}),
    ]

admin.site.register(IPUser, UserAdmin)