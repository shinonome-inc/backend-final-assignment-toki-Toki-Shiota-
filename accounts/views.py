from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

from .forms import CustomUserCreationForm


class SignUpView(CreateView):
    template_name = "accounts/signup.html"  # SignUpViewを表示するhtmlファイル名
    form_class = CustomUserCreationForm  # forms.pyで記載したクラスを適応する。
    success_url = reverse_lazy("tweets:home")  # ユーザーが登録ボタンを押したときにどこにリダイレクトするか（表示するか）

    def form_valid(self, form):
        response = super().form_valid(form)  # formのバリデーションがTureだったときのみ呼ばれるメッソド
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")
        user = authenticate(self.request, username=username, password=password)
        login(self.request, user)
        return response


"""
template_nameに代入したhtmlファイルがそのViewで表示されるhtmlファイル
となる。
success_urlの時は、必ずreverse_lazy()関数を使う。
→reverse_lazyで遅延評価することによって、urls.pyが読み込まれた後
に評価でき、URLの逆引きが出来る。
"""
