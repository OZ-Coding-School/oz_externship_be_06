from django.test import TestCase
from rest_framework import status
from datetime import date
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

class CustomJwtAuthTests(TestCase):
    client: APIClient

    def setUp(self) -> None:
        self.client = APIClient()
        self.withdrawal_url = "/api/v1/accounts/withdrawal/"

        User = get_user_model()
        self.email = "withdrawal_test@example.com"
        self.password = "Testpass123!"
        self.user = User.objects.create_user(
            email=self.email,
            password=self.password,
            birthday=date(2000, 1, 1),
            phone_number="01012345678",
            name="테스터",
            nickname="tester",
            gender="male",
        )

        self.user.is_active = False
        self.user.save()

        access = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def test_inactive_user_cannot_access_me(self):
        me_url = "/api/v1/accounts/me/"
        response = self.client.get(me_url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)