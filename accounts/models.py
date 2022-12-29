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
