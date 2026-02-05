from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.posts.permissions.comment_permissions import IsCommentAuthorOrReadOnly

User = get_user_model()


class CommentPermissionTests(TestCase):
    def setUp(self) -> None:
        """테스트용 유저 생성"""
        self.user = User.objects.create_user(
            email="test@example.com",
            password="testpass",
            nickname="user",
            phone_number="010-0000-0000",
            gender="MALE",
            birthday="1990-01-01",
        )

    def test_safe_methods(self) -> None:
        """SAFE_METHODS(GET 등)에서는 항상 True 반환"""

        class DummyRequest:
            method = "GET"

        class DummyObj:
            author = self.user

        perm = IsCommentAuthorOrReadOnly()
        request = DummyRequest()
        obj = DummyObj()
        self.assertTrue(perm.has_object_permission(request, None, obj))

    def test_not_author(self) -> None:
        """작성자가 아닌 경우 PUT/DELETE 등에서는 False 반환"""

        class DummyRequest:
            method = "PUT"

        class DummyObj:
            author = None

        perm = IsCommentAuthorOrReadOnly()
        request = DummyRequest()
        obj = DummyObj()
        self.assertFalse(perm.has_object_permission(request, None, obj))

    def test_author(self) -> None:
        """작성자인 경우 PUT/DELETE 등에서는 True 반환"""

        class DummyRequest:
            method = "DELETE"

        class DummyObj:
            author = self.user

        perm = IsCommentAuthorOrReadOnly()
        request = DummyRequest()
        obj = DummyObj()
        self.assertTrue(perm.has_object_permission(request, None, obj))
