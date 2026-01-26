from datetime import date
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


class ProfileImageAPITests(TestCase):
    client: APIClient

    def setUp(self) -> None:
        self.client = APIClient()
        self.url = "/api/v1/accounts/me/profile-image/"

        User = get_user_model()
        self.user = User.objects.create_user(
            email="profile_test@example.com",
            password="Testpass123!",
            birthday=date(2000, 1, 1),
            phone_number="01012345678",
            name="테스터",
            nickname="tester",
            gender="MALE",
        )

        access = str(RefreshToken.for_user(self.user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def _create_test_image(self, format: str = "JPEG") -> BytesIO:
        image = Image.new("RGB", (100, 100), color="red")
        buffer = BytesIO()
        image.save(buffer, format=format)
        buffer.seek(0)
        return buffer

    def test_profile_image_upload_success_200(self) -> None:
        image_buffer = self._create_test_image()
        image_file = SimpleUploadedFile(
            "test.jpg",
            image_buffer.read(),
            content_type="image/jpeg",
        )

        res = self.client.patch(
            self.url,
            {"image": image_file},
            format="multipart",
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertIn("detail", data)

    def test_profile_image_upload_png_success_200(self) -> None:
        image_buffer = self._create_test_image(format="PNG")
        image_file = SimpleUploadedFile(
            "test.png",
            image_buffer.read(),
            content_type="image/png",
        )

        res = self.client.patch(
            self.url,
            {"image": image_file},
            format="multipart",
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_profile_image_invalid_type_400(self) -> None:
        fake_gif = SimpleUploadedFile(
            "test.gif",
            b"GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;",
            content_type="image/gif",
        )

        res = self.client.patch(
            self.url,
            {"image": fake_gif},
            format="multipart",
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        data = res.json()
        self.assertIn("error_detail", data)

    def test_profile_image_unauthenticated_401(self) -> None:
        self.client.credentials()

        image_buffer = self._create_test_image()
        image_file = SimpleUploadedFile(
            "test.jpg",
            image_buffer.read(),
            content_type="image/jpeg",
        )

        res = self.client.patch(
            self.url,
            {"image": image_file},
            format="multipart",
        )

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
