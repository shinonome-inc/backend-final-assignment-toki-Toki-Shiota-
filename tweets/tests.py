from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from tweets.models import Like, Tweet

User = get_user_model()


class TestHomeView(TestCase):
    def test_success_get(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username="testuser", password="testpassword")
        Tweet.objects.create(user=self.user, content="test")
        response = self.client.get(reverse("tweets:home"))
        self.assertQuerysetEqual(response.context["tweet_list"], Tweet.objects.all(), ordered=False)


class TestTweetCreateView(TestCase):
    def setUp(self):
        self.url = reverse("tweets:create")
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.login(username="testuser", password="testpassword")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_success_post(self):
        additional_data = {"content": "test"}
        response = self.client.post(self.url, additional_data)
        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertTrue(Tweet.objects.filter(content=additional_data["content"]).exists())

    def test_failure_post_with_empty_content(self):
        additional_data = {"content": ""}
        response = self.client.post(self.url, additional_data)
        form = response.context["form"]
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Tweet.objects.filter(content=additional_data["content"]).exists())
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["content"], ["このフィールドは必須です。"])

    def test_failure_post_with_too_long_content(self):
        additional_data = {"content": "t" * 1000}
        response = self.client.post(self.url, additional_data)
        form = response.context["form"]
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Tweet.objects.filter(content=additional_data["content"]).exists())
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["content"], ["この値は 200 文字以下でなければなりません( 1000 文字になっています)。"])


class TestTweetDetailView(TestCase):
    def test_success_get(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.tweet = Tweet.objects.create(user=self.user, content="test")
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(reverse("tweets:detail", kwargs={"pk": self.tweet.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["tweet"],
            self.tweet,
        )


class TestTweetDeleteView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="testuser1", password="testpassword")
        self.user2 = User.objects.create_user(username="testuser2", password="testpassword")
        self.objects1 = Tweet.objects.create(user=self.user1, content="test1")
        self.objects2 = Tweet.objects.create(user=self.user2, content="test2")
        self.client.login(username="testuser1", password="testpassword")
        self.url = reverse("tweets:delete", kwargs={"pk": self.objects1.pk})

    def test_success_post(self):
        response = self.client.post(self.url)
        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )
        self.assertFalse(Tweet.objects.filter(content="test1").exists())

    def test_failure_post_with_not_exist_tweet(self):
        response = self.client.post(reverse("tweets:delete", kwargs={"pk": 1000}))
        self.assertEqual(response.status_code, 404)

    def test_failure_post_with_incorrect_user(self):
        response = self.client.post(reverse("tweets:delete", kwargs={"pk": self.objects2.pk}))
        self.assertEqual(response.status_code, 403)


class TestFavoriteView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
        )
        self.client.login(username="testuser", password="testpassword")
        self.data = Tweet.objects.create(user=self.user, content="testtweet")
        self.url = reverse("tweets:like", kwargs={"pk": self.data.pk})

    def test_success_post(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Like.objects.count(), 1)

    def test_failure_post_with_not_exist_tweet(self):
        response = self.client.post(reverse("tweets:like", kwargs={"pk": "1000"}))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Like.objects.count(), 0)

    def test_failure_post_with_favorited_tweet(self):
        Like.objects.create(tweet=self.data, user=self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Like.objects.count(), 1)


class TestUnfavoriteView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
        )
        self.client.login(username="testuser", password="testpassword")
        self.data = Tweet.objects.create(user=self.user, content="testtweet")
        Like.objects.create(tweet=self.data, user=self.user)
        self.url = reverse("tweets:unlike", kwargs={"pk": self.data.pk})

    def test_success_post(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Like.objects.count(), 0)

    def test_failure_post_with_not_exist_tweet(self):
        response = self.client.post(reverse("tweets:unlike", kwargs={"pk": "1000"}))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Like.objects.count(), 1)

    def test_failure_post_with_unfavorited_tweet(self):
        Like.objects.filter(tweet=self.data, user=self.user).delete()
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
