from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.posts.exceptions.comment_exceptions import CommentForbiddenException
from apps.posts.models.post import Post
from apps.posts.models.post_category import PostCategory
from apps.posts.models.post_comment import PostComment
from apps.posts.serializers.comment_serializers import PostCommentUpdateSerializer
from apps.posts.services.comment.comment_create_services import create_comment
from apps.posts.services.comment.comment_delete_services import delete_comment
from apps.posts.services.comment.comment_nickname_services import (
    generate_comment_nickname,
)
from apps.posts.services.comment.comment_update_services import update_comment

User = get_user_model()


class CommentServiceTests(TestCase):
    def setUp(self) -> None:
        # 테스트용 유저, 카테고리, 게시글, 댓글을 생성합니다.
        self.user = User.objects.create_user(email="test@example.com", password="testpass", nickname="user")
        self.other_user = User.objects.create_user(email="other@example.com", password="testpass", nickname="other")
        self.category = PostCategory.objects.create(name="cat")
        self.post = Post.objects.create(author=self.user, title="t", content="c", category=self.category)
        self.comment = PostComment.objects.create(post=self.post, author=self.user, content="cc")

    def test_create_comment(self) -> None:
        # 댓글 생성 서비스 정상 동작
        comment = create_comment(self.user, self.post, "서비스 댓글")
        self.assertEqual(comment.content, "서비스 댓글")
        self.assertEqual(comment.author, self.user)
        self.assertEqual(comment.post, self.post)

    def test_create_comment_with_none_post(self) -> None:
        # post가 None일 때 예외 발생 (TypeError 등)
        with self.assertRaises(Exception):
            create_comment(self.user, None, "내용")  # type: ignore[arg-type]

    def test_create_comment_with_none_author(self) -> None:
        # author가 None일 때 예외 발생 (TypeError 등)
        with self.assertRaises(Exception):
            create_comment(None, self.post, "내용")

    def test_update_comment_not_author(self) -> None:
        # 댓글 수정 서비스에서 작성자가 아닌 경우 예외 발생
        with self.assertRaises(CommentForbiddenException):
            update_comment(self.other_user, self.comment, "수정")

    def test_update_comment_with_none_comment(self) -> None:
        # comment가 None일 때 예외 발생 (AttributeError 등)
        with self.assertRaises(Exception):
            update_comment(self.user, None, "수정")  # type: ignore[arg-type]

    def test_update_comment_success(self) -> None:
        # 작성자가 본인 댓글을 정상적으로 수정할 수 있는지 테스트
        comment = PostComment.objects.create(post=self.post, author=self.user, content="수정 전")
        updated = update_comment(self.user, comment, "수정 후")
        self.assertEqual(updated.content, "수정 후")
        # DB 반영 확인
        comment.refresh_from_db()
        self.assertEqual(comment.content, "수정 후")

    def test_delete_comment_not_author(self) -> None:
        # 댓글 삭제 서비스에서 작성자가 아닌 경우 예외 발생
        with self.assertRaises(CommentForbiddenException):
            delete_comment(self.other_user, self.comment)

    def test_delete_comment_with_none_comment(self) -> None:
        # comment가 None일 때 예외 발생 (AttributeError 등)
        with self.assertRaises(Exception):
            delete_comment(self.user, None)  # type: ignore[arg-type]

    def test_delete_comment_success(self) -> None:
        # 작성자가 본인 댓글을 정상적으로 삭제할 수 있는지 테스트
        comment = PostComment.objects.create(post=self.post, author=self.user, content="삭제 테스트")
        delete_comment(self.user, comment)
        # 실제로 DB에서 삭제되었는지 확인
        with self.assertRaises(PostComment.DoesNotExist):
            PostComment.objects.get(id=comment.id)

    def test_nickname_randomness(self) -> None:
        # 닉네임 생성 서비스가 다양한 결과를 반환하는지 테스트
        results = set(generate_comment_nickname() for _ in range(20))
        self.assertGreaterEqual(len(results), 5)

    def test_post_comment_update_serializer_not_author(self) -> None:
        # 댓글 수정 시 작성자가 아닌 경우 PermissionDenied 발생 테스트
        from rest_framework.exceptions import PermissionDenied

        serializer = PostCommentUpdateSerializer(
            self.comment,
            data={"content": "updated"},
            context={"request": type("obj", (), {"user": self.other_user, "is_authenticated": True})()},
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
        with self.assertRaises(PermissionDenied):
            serializer.save()
