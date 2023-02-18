from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView

from tweets.models import Tweet

from .forms import CustomUserCreationForm, LoginForm

User = get_user_model()


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


class LoginView(auth_views.LoginView):
    form_class = LoginForm
    template_name = "accounts/login.html"


"""
form_classにform.pyで定義したLoginFormを指定することで、ログイン処理時に
LoginFormで定義したフォームデザインが適用される。
"""


class LogoutView(auth_views.LogoutView):
    template_name = "accounts/login.html"


"""
注意:複数のクラスを継承するときは必ずLoginRequiredMixinを一番初めに継承する。

template_nameはログアウト後に表示する画面。

今回のコードはdjango標準のLoginView, LogoutViewクラスを利用したときのみ使える。

"""


class UserProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "accounts/user_profile.html"
    slug_field = "username"
    slug_url_kwarg = "username"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        # username = self.kwargs["username"]
        context["tweet_list"] = Tweet.objects.select_related("user").filter(user=user)
        # print(context)
        return context
