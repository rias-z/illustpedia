from django.contrib import admin
from .models import IPUser
from .models import Artist


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


class ArtistAdmin(admin.ModelAdmin):
    fieldsets = [
        ('artist_id', {'fields': ['artist_id']}),
        ('artist_name', {'fields': ['artist_name']}),
        ('tags', {'fields': ['tags']}),
    ]
admin.site.register(Artist, ArtistAdmin)