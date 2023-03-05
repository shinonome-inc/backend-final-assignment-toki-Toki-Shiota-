from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, View

from .forms import TweetForm
from .models import Like, Tweet


class HomeView(LoginRequiredMixin, ListView):
    # 全ユーザーのツイート表示
    model = Tweet
    template_name = "tweets/home.html"
    ordering = "-created_at"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        liked_list = (
            Like.objects.select_related("tweet").filter(user=self.request.user).values_list("tweet", flat=True)
        )
        context["liked_list"] = liked_list
        return context


class TweetCreateView(LoginRequiredMixin, CreateView):
    # 作成機能
    model = Tweet
    template_name = "tweets/create.html"
    form_class = TweetForm
    success_url = reverse_lazy("tweets:home")

    def form_valid(self, form):
        # 投稿ユーザーをリクエストユーザーと紐づけ
        form.instance.user = self.request.user
        return super().form_valid(form)


class TweetDetailView(LoginRequiredMixin, DetailView):
    # 詳細機能
    model = Tweet
    template_name = "tweets/detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["like_count"] = Like.objects.filter(tweet=self.object).count()
        return context


class TweetDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Tweet
    template_name = "tweets/delete.html"
    success_url = reverse_lazy("tweets:home")

    def test_func(self, **kwargs):
        # アクセスできるユーザーを制限
        tweet = self.get_object()
        return tweet.user == self.request.user


class LikeView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        tweet_id = self.kwargs["pk"]
        tweet = get_object_or_404(Tweet, pk=tweet_id)
        user = self.request.user
        Like.objects.get_or_create(tweet=tweet, user=user)
        is_liked = True
        like_url = reverse("tweets:like", kwargs={"pk": tweet_id})
        unlike_url = reverse("tweets:unlike", kwargs={"pk": tweet_id})
        like_count = tweet.like_tweet.count()
        context = {
            "like_count": like_count,
            "tweet_id": tweet_id,
            "is_liked": is_liked,
            "like_url": like_url,
            "unlike_url": unlike_url,
        }
        return JsonResponse(context)


class UnlikeView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        tweet_id = self.kwargs["pk"]
        tweet = get_object_or_404(Tweet, pk=tweet_id)
        user = self.request.user
        if like := Like.objects.filter(user=user, tweet=tweet):
            like.delete()
        is_liked = False
        like_url = reverse("tweets:like", kwargs={"pk": tweet_id})
        unlike_url = reverse("tweets:unlike", kwargs={"pk": tweet_id})
        like_count = tweet.like_tweet.count()
        context = {
            "like_count": like_count,
            "tweet_id": tweet_id,
            "is_liked": is_liked,
            "like_url": like_url,
            "unlike_url": unlike_url,
        }
        return JsonResponse(context)
