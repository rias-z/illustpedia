from django.contrib import admin
from .models import IPUser, Artist, Illust
# from .models import Tag


class UserAdmin(admin.ModelAdmin):
    fieldsets = [
        ('username', {'fields': ['username']}),
        ('nickname', {'fields': ['nickname']}),
        ('email', {'fields': ['email']}),
        ('password', {'fields': ['password']}),
        ('is_active', {'fields': ['is_active']}),
        ('is_staff', {'fields': ['is_staff']}),
        ('fav_artist', {'fields': ['fav_artist']}),
    ]
admin.site.register(IPUser, UserAdmin)


class ArtistAdmin(admin.ModelAdmin):
    fieldsets = [
        ('artist_id', {'fields': ['artist_id']}),
        ('artist_name', {'fields': ['artist_name']}),
        ('tags', {'fields': ['tags']}),
        ('thumbnail', {'fields': ['thumbnail']}),
    ]
admin.site.register(Artist, ArtistAdmin)


class IllustAdmin(admin.ModelAdmin):
    fieldsets = [
        ('tags', {'fields': ['tags']}),
        ('image', {'fields': ['image']}),
    ]
admin.site.register(Illust, IllustAdmin)
