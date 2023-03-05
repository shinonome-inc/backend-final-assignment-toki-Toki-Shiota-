from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, View

from tweets.models import Like, Tweet

from .forms import CustomUserCreationForm, LoginForm
from .models import FriendShip

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
    pass


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
        context["tweet_list"] = Tweet.objects.select_related("user").filter(user=user)
        context["is_following"] = FriendShip.objects.filter(following=user, follower=self.request.user).exists()
        context["following_count"] = FriendShip.objects.filter(follower=user).count()
        context["follower_count"] = FriendShip.objects.filter(following=user).count()
        liked_list = Like.objects.select_related("tweet").filter(user=self.request.user).values_list("tweet")
        context["like_count"] = liked_list
        return context


class FollowView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        follower = self.request.user
        following = get_object_or_404(User, username=self.kwargs["username"])

        if follower == following:
            return HttpResponseBadRequest("自分自身をフォローすることはできません")
        if FriendShip.objects.filter(follower=follower, following=following).exists():
            messages.warning(request, f"あなたはすでに { following.username } をフォローしています。")
            return redirect("tweets:home")
        FriendShip.objects.create(follower=follower, following=following)
        messages.info(request, f"{ following.username } をフォローしました。")
        return redirect("tweets:home")


class UnFollowView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        follower = self.request.user
        following = get_object_or_404(User, username=self.kwargs["username"])

        if follower == following:
            return HttpResponseBadRequest("無効な操作です。")

        friend = FriendShip.objects.filter(following=following, follower=follower)
        friend.delete()
        messages.info(request, f"{following.username} のフォローを解除しました。")
        return redirect("tweets:home")


class FollowingListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "accounts/following_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs["username"])
        context["following_list"] = FriendShip.objects.select_related("following").filter(follower=user)
        return context


class FollowerListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "accounts/follower_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(User, username=self.kwargs["username"])
        context["follower_list"] = FriendShip.objects.select_related("follower").filter(following=user)
        return context
