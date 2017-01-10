from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)
from taggit.managers import TaggableManager


# 管理者ユーザモデル
class AuthUserManager(BaseUserManager):
    def create_user(self, username, email, password):
        if not username:
            return ValueError('Users must have an username')
        if not email:
            return ValueError('Users must have an email')

        user = self.model(username=username, email=email, password=password)
        user.set_password(password)
        user.is_active = True
        user.is_superuser = False
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password):
        user = self.create_user(username=username, email=email, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)


# 作者モデル
class Artist(models.Model):
    artist_id = models.IntegerField("作者ID", unique=True)
    artist_name = models.CharField("作者の名前", max_length=30)
    thumbnail = models.ImageField("サムネイル", upload_to='thumbnail/')

    tags = TaggableManager()

    def __str__(self):
        return self.artist_name


# ユーザモデル
class IPUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField("ユーザID", unique=True, max_length=30)
    nickname = models.CharField("ニックネーム", max_length=30)
    email = models.EmailField(unique=True)
    fav_artist = models.ManyToManyField(Artist)

    date_joined = models.DateTimeField(auto_now_add=True)
    is_staff = models.BooleanField(default=False, null=False)
    is_active = models.BooleanField(default=True, null=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    objects = AuthUserManager()

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        return True


# イラストモデル
class Illust(models.Model):
    image = models.ImageField("イラスト画像", upload_to='illust/')
    tags = TaggableManager()

