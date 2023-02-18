from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView

from .forms import TweetForm
from .models import Tweet


class HomeView(LoginRequiredMixin, ListView):
    # 全ユーザーのツイート表示
    model = Tweet
    template_name = "tweets/home.html"
    ordering = "-created_at"


class TweetCreateView(LoginRequiredMixin, CreateView):
    # 作成機能
    model = Tweet
    template_name = "tweets/create.html"
    # form_class = TweetForm
    fields = ["content"]
    success_url = reverse_lazy("tweets:home")

    def form_valid(self, form):
        # 投稿ユーザーをリクエストユーザーと紐づけ
        form.instance.user = self.request.user
        return super().form_valid(form)


class TweetDetailView(LoginRequiredMixin, DetailView):
    # 詳細機能
    model = Tweet
    template_name = "tweets/detail.html"


class TweetDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Tweet
    template_name = "tweets/delete.html"
    success_url = reverse_lazy("tweets:home")

    def test_func(self, **kwargs):
        # アクセスできるユーザーを制限
        tweet = self.get_object()
        return tweet.user == self.request.user
