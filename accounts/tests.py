from django.conf import settings
from django.contrib.auth import SESSION_KEY, get_user_model
from django.test import TestCase
from django.urls import reverse

from tweets.models import Tweet

from .models import FriendShip

User = get_user_model()


class TestSignUpView(TestCase):
    def setUp(self):
        self.url = reverse("accounts:signup")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/signup.html")

    def test_success_post(self):
        valid_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }

        response = self.client.post(self.url, valid_data)

        self.assertRedirects(
            response,
            reverse(settings.LOGIN_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
        )
        self.assertTrue(
            User.objects.filter(
                username=valid_data["username"],
                email=valid_data["email"],
            ).exists()
        )
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_empty_form(self):
        invalid_data = {
            "username": "",
            "email": "",
            "password1": "",
            "password2": "",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            User.objects.filter(
                username=invalid_data["username"],
                email=invalid_data["email"],
            ).exists()
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["username"], ["このフィールドは必須です。"])
        self.assertEqual(form.errors["email"], ["このフィールドは必須です。"])
        self.assertEqual(form.errors["password1"], ["このフィールドは必須です。"])
        self.assertEqual(form.errors["password2"], ["このフィールドは必須です。"])

    def test_failure_post_with_empty_username(self):
        invalid_data = {
            "username": "",
            "email": "test@test.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            User.objects.filter(
                username=invalid_data["username"],
            ).exists()
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["username"], ["このフィールドは必須です。"])

    def test_failure_post_with_empty_email(self):
        invalid_data = {
            "username": "testuser",
            "email": "",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            User.objects.filter(
                email=invalid_data["email"],
            ).exists()
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["email"], ["このフィールドは必須です。"])

    def test_failure_post_with_empty_password(self):
        invalid_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "",
            "password2": "",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            User.objects.filter(
                password=invalid_data["password2"],
            ).exists()
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["password2"], ["このフィールドは必須です。"])

    def test_failure_post_with_duplicated_user(self):
        duplicated_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "testpassword",
            "password2": "testpassword",
        }

        User.objects.create_user(
            username="testuser",
            email="duplicated_user_test@example.com",
            password="testpassword",
        )
        response = self.client.post(self.url, duplicated_data)
        form = response.context["form"]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.all().count(), 1)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["username"], ["同じユーザー名が既に登録済みです。"])

    def test_failure_post_with_invalid_email(self):
        invalid_data = {
            "username": "testuser",
            "email": "test",
            "password1": "testpassword",
            "password2": "testpassword",
        }
        response = self.client.post(self.url, invalid_data)
        form = response.context["form"]

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            User.objects.filter(
                email=invalid_data["email"],
            ).exists()
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["email"], ["有効なメールアドレスを入力してください。"])

    def test_failure_post_with_too_short_password(self):
        short_password_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "short",
            "password2": "short",
        }
        response = self.client.post(self.url, short_password_data)
        form = response.context["form"]
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            User.objects.filter(
                password=short_password_data["password2"],
            ).exists()
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["password2"], ["このパスワードは短すぎます。最低 8 文字以上必要です。"])

    def test_failure_post_with_password_similar_to_username(self):
        password_similar_to_username_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "testuser",
            "password2": "testuser",
        }
        response = self.client.post(self.url, password_similar_to_username_data)
        form = response.context["form"]
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            User.objects.filter(
                password=password_similar_to_username_data["password2"],
            ).exists()
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["password2"], ["このパスワードは ユーザー名 と似すぎています。"])

    def test_failure_post_with_only_numbers_password(self):
        only_numbers_password_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "123456789",
            "password2": "123456789",
        }
        response = self.client.post(self.url, only_numbers_password_data)
        form = response.context["form"]
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            User.objects.filter(
                password=only_numbers_password_data["password2"],
            ).exists()
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["password2"], ["このパスワードは一般的すぎます。", "このパスワードは数字しか使われていません。"]
        )

    def test_failure_post_with_mismatch_password(self):
        only_numbers_password_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password1": "testpassword",
            "password2": "testppassword",
        }
        response = self.client.post(self.url, only_numbers_password_data)
        form = response.context["form"]
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            User.objects.filter(
                password=only_numbers_password_data["password2"],
            ).exists()
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["password2"], ["確認用パスワードが一致しません。"])


class TestLoginView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="testemail@example.com",
            password="testpassword",
        )
        self.url = reverse("accounts:login")

    def test_success_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_success_post(self):
        valid_data = {
            "username": "testuser",
            "password": "testpassword",
        }

        response = self.client.post(self.url, valid_data)

        self.assertRedirects(
            response,
            reverse(settings.LOGIN_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
        )
        self.assertFalse(
            User.objects.filter(
                username=valid_data["username"],
                email=valid_data["password"],
            ).exists()
        )
        self.assertIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_not_exists_user(self):
        not_exists_user_data = {
            "username": "nottestuser",
            "password": "testpassword",
        }
        response = self.client.post(self.url, not_exists_user_data)
        form = response.context["form"]
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            User.objects.filter(
                username=not_exists_user_data["username"],
                password=not_exists_user_data["password"],
            ).exists()
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["__all__"],
            ["正しいユーザー名とパスワードを入力してください。どちらのフィールドも大文字と小文字は区別されます。"],
        )
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_failure_post_with_empty_password(self):
        empty_password_data = {
            "username": "testuser",
            "password": "",
        }
        response = self.client.post(self.url, empty_password_data)
        form = response.context["form"]
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            User.objects.filter(
                password=empty_password_data["password"],
            ).exists()
        )
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["password"], ["このフィールドは必須です。"])
        self.assertNotIn(SESSION_KEY, self.client.session)


class TestLogoutView(TestCase):
    def setUp(self):
        self.user = {
            "username": "testuser",
            "password": "testpassword",
        }
        self.client.login(username="testuser", password="testpassword")

    def test_success_get(self):

        response = self.client.get(reverse("accounts:logout"))

        self.assertRedirects(
            response,
            reverse(settings.LOGOUT_REDIRECT_URL),
            status_code=302,
            target_status_code=200,
        )
        self.assertFalse(
            User.objects.filter(
                username=self.user["username"],
                email=self.user["password"],
            ).exists()
        )
        self.assertNotIn(SESSION_KEY, self.client.session)


class TestUserProfileView(TestCase):
    def test_success_get(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
        )
        self.user2 = User.objects.create_user(
            username="testuser2",
            password="testpassword2",
        )
        self.client.login(username="testuser", password="testpassword")
        Tweet.objects.create(user=self.user, content="test")
        FriendShip.objects.create(following=self.user2, follower=self.user)
        response = self.client.get(
            reverse("accounts:user_profile", kwargs={"username": self.user.username})
        )
        self.assertQuerysetEqual(
            response.context["tweet_list"],
            Tweet.objects.filter(user=self.user),
        )
        self.assertEquals(
            response.context["following_count"],
            FriendShip.objects.filter(follower=self.user).exists(),
        )
        self.assertEquals(
            response.context["follower_count"],
            FriendShip.objects.filter(following=self.user).exists(),
        )


class TestUserProfileEditView(TestCase):
    def test_success_get(self):
        pass

    def test_success_post(self):
        pass

    def test_failure_post_with_not_exists_user(self):
        pass

    def test_failure_post_with_incorrect_user(self):
        pass


class TestFollowView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="testuser1",
            password="testpassword1",
        )
        self.user2 = User.objects.create_user(
            username="testuser2",
            password="testpassword2",
        )
        self.client.login(username="testuser1", password="testpassword1")

    def test_success_post(self):
        response = self.client.post(
            reverse("accounts:follow", kwargs={"username": self.user2.username})
        )
        self.assertTrue(
            FriendShip.objects.filter(
                following=self.user2, follower=self.user1
            ).exists()
        )
        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )

    def test_failure_post_with_not_exist_user(self):
        response = self.client.post(
            reverse("accounts:follow", kwargs={"username": "empty"})
        )
        self.assertEqual(response.status_code, 404)
        self.assertFalse(FriendShip.objects.count(), 0)

    def test_failure_post_with_self(self):
        response = self.client.post(
            reverse("accounts:follow", kwargs={"username": self.user1.username})
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(FriendShip.objects.count(), 0)


class TestUnfollowView(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="testuser1",
            password="testpassword1",
        )
        self.user2 = User.objects.create_user(
            username="testuser2",
            password="testpassword2",
        )
        self.client.login(username="testuser1", password="testpassword1")
        FriendShip.objects.create(following=self.user2, follower=self.user1)

    def test_success_post(self):
        response = self.client.post(
            reverse("accounts:unfollow", kwargs={"username": self.user2.username})
        )
        self.assertFalse(
            FriendShip.objects.filter(
                following=self.user2, follower=self.user1
            ).exists()
        )
        self.assertRedirects(
            response,
            reverse("tweets:home"),
            status_code=302,
            target_status_code=200,
        )

    def test_failure_post_with_not_exist_tweet(self):
        response = self.client.post(
            reverse("accounts:unfollow", kwargs={"username": "empty"})
        )
        self.assertEqual(response.status_code, 404)
        self.assertTrue(FriendShip.objects.count(), 1)

    def test_failure_post_with_incorrect_user(self):
        response = self.client.post(
            reverse("accounts:unfollow", kwargs={"username": self.user1.username})
        )
        self.assertEqual(response.status_code, 400)
        self.assertTrue(FriendShip.objects.count(), 1)


class TestFollowingListView(TestCase):
    def test_success_get(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
        )
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(
            reverse("accounts:following_list", kwargs={"username": self.user.username})
        )
        self.assertEqual(response.status_code, 200)


class TestFollowerListView(TestCase):
    def test_success_get(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
        )
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(
            reverse("accounts:follower_list", kwargs={"username": self.user.username})
        )
        self.assertEqual(response.status_code, 200)
