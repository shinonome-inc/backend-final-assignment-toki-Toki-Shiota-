from django.contrib.auth import get_user_model

# setting.pyで定めたユーザーモデルを呼び出す。
from django.contrib.auth.forms import UserCreationForm

# UserCreationFormは自動でpasswordを2回入力しないと登録できない機能が備わっている。


CustomUser = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser  # 直接model = get_user_model()と書かない
        fields = ("username", "email")


# password1, password2というフィールドはUserCreationFormで設定されているため書かなくていいらしい。
# usernameとemailは空欄ではいけないのでfiledにセットする。
