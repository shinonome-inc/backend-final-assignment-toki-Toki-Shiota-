from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField()


"""
    AbstractUserはemailというフィールドは実装されているが、
    blank=true(無くてもよい)とされているのでこれをblank=false
    にする必要がある。
    email = models.EmailField()
    引数にはデフォルトでfalseになるためblank=falseを入れる必要はない。
    modelができたらsetting.pyのAUTH_USER_MODELを変更する。(アプリ名.モデル名)
    その後、
    >python manage.py makemigrations
    （migrateファイルを作成）
    >python manage.py migrate
    （データベースに適応）
"""


class FriendShip(models.Model):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="follower", on_delete=models.CASCADE
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="following", on_delete=models.CASCADE
    )
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "following"], name="unique_constraint"
            )
        ]

    def __str__(self):
        return "{} : {}".format(self.follower.username, self.following.username)
