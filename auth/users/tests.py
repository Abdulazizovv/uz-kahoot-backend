from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from apps.botapp.models import BotUser


User = get_user_model()


class TelegramVerifyOTPTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("telegram-verify-otp")

    def test_verify_otp_legacy_telegram_subject(self):
        bot_user = BotUser.objects.create(user_id="123")
        user = User.objects.create_user(phone_number="+998901234567", password=None)
        user.bot_user = bot_user
        user.save(update_fields=["bot_user"])

        with patch("auth.users.views.otp_manager.verify_otp_by_code", return_value="123"):
            resp = self.client.post(self.url, data={"otp": "12345"}, format="json")

        assert resp.status_code == 200
        assert "access" in resp.data
        assert resp.data["user"]["phone_number"] == "+998901234567"

    def test_verify_otp_user_uuid_subject(self):
        user = User.objects.create_user(phone_number="+998911112233", password=None)
        subject_id = f"user:{user.id}"

        with patch("auth.users.views.otp_manager.verify_otp_by_code", return_value=subject_id):
            resp = self.client.post(self.url, data={"otp": "12345"}, format="json")

        assert resp.status_code == 200
        assert resp.data["user"]["id"] == str(user.id)

    def test_verify_otp_user_uuid_subject_user_missing(self):
        with patch("auth.users.views.otp_manager.verify_otp_by_code", return_value="user:00000000-0000-0000-0000-000000000000"):
            resp = self.client.post(self.url, data={"otp": "12345"}, format="json")

        assert resp.status_code == 404
