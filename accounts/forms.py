from django.contrib.auth import get_user_model

# setting.pyで定めたユーザーモデルを呼び出す。
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

# UserCreationFormは自動でpasswordを2回入力しないと登録できない機能が備わっている。


CustomUser = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser  # 直接model = get_user_model()と書かない
        fields = ("username", "email")


# password1, password2というフィールドはUserCreationFormで設定されているため書かなくていいらしい。
# usernameとemailは空欄ではいけないのでfiledにセットする。


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # super()を使って継承元から__init__メソッドを呼び出す。
        # 親クラスのメソッドを子クラスのLoginViewでも使いつつ、新たにパラメータやメソッドを追加するため。
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"  # ※１
            field.widget.attrs["placeholder"] = field.label  # ※２
            # Widget：form-controlクラスやプレースホルダーといったフォームの見た目を整えるもの。
            # AuthenticationFormで定義されているユーザ、パスワードの項目に適用する。


# ※１：全てのフォームの部品のclass属性に「form-control」を指定（bootstrapのフォームデザインを利用するため）
# ※２：全てのフォームの部品にpaceholderを定義して、入力フォームにフォーム名が表示されるように指定。
