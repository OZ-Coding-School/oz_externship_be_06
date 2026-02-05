from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.posts.constants.comment_const import CommentErrorMessage
from apps.posts.models.post import Post
from apps.posts.models.post_category import PostCategory
from apps.posts.models.post_comment import PostComment


class PostCommentDetailAPITestCase(APITestCase):
    """
    댓글 상세 조회 API 테스트
    - 정상 조회
    - 댓글 미존재 시 예외
    """

    COMMENT_NOT_FOUND_MSG = CommentErrorMessage.COMMENT_NOT_FOUND

    def setUp(self) -> None:
        User = get_user_model()
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpass",
            nickname="testuser",
            phone_number="010-1234-5678",
            gender="MALE",
            birthday="2000-01-01",
        )
        self.category = PostCategory.objects.create(name="test category")
        self.post = Post.objects.create(
            author=self.user,
            title="test post",
            content="test content",
            category=self.category,
        )
        self.client.force_authenticate(user=self.user)

    def test_comment_detail_success(self) -> None:
        """
        정상적으로 댓글 상세 조회가 되는 경우
        """
        url = reverse("posts:post-comment-rud", args=[self.post.id, 1])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("id", response.data)
        self.assertIn("content", response.data)
        self.assertEqual(response.data["id"], 1)

    def test_comment_detail_not_found(self) -> None:
        """
        존재하지 않는 댓글 조회 시 404 반환
        """
        url = reverse("posts:post-comment-rud", args=[self.post.id, 999999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertIn("error_detail", response.data)
        self.assertEqual(response.data["error_detail"], self.COMMENT_NOT_FOUND_MSG)


class PostCommentCreateAPITestCase(APITestCase):
    """
    댓글 생성 API 테스트
    - 성공, 인증 실패, validation 실패, 미존재 게시글
    """

    def setUp(self) -> None:
        User = get_user_model()
        self.user = User.objects.create_user(
            email="createuser@example.com",
            password="testpass",
            nickname="createuser",
            phone_number="010-5555-6666",
            gender="MALE",
            birthday="1985-02-02",
        )
        self.category = PostCategory.objects.create(name="create category")
        self.post = Post.objects.create(
            author=self.user,
            title="create post",
            content="create content",
            category=self.category,
        )
        self.create_url = reverse("posts:post-comment-create", args=[self.post.id])

    def test_comment_create_success(self) -> None:
        """
        댓글 생성 성공
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.create_url, {"content": "new comment"}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertIn("detail", response.data)

    def test_comment_create_unauthenticated(self) -> None:
        """
        인증되지 않은 사용자가 댓글 생성 시도 시 401 반환
        """
        response = self.client.post(self.create_url, {"content": "new comment"}, format="json")
        self.assertEqual(response.status_code, 401)
        self.assertIn("error_detail", response.data)
        self.assertEqual(response.data["error_detail"], CommentErrorMessage.UNAUTHORIZED)

    def test_comment_create_validation_error(self) -> None:
        """
        댓글 내용이 비어 있을 때 400 반환
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.create_url, {"content": "   "}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("error_detail", response.data)
        self.assertIn("content", response.data["error_detail"])

    def test_comment_create_post_not_found(self) -> None:
        """
        존재하지 않는 게시글에 댓글 생성 시도 시 404 반환
        """
        self.client.force_authenticate(user=self.user)
        url = reverse("posts:post-comment-create", args=[999999])
        response = self.client.post(url, {"content": "new comment"}, format="json")
        self.assertEqual(response.status_code, 404)
        self.assertIn("error_detail", response.data)
        self.assertEqual(response.data["error_detail"], CommentErrorMessage.COMMENT_NOT_FOUND)

    def test_comment_create_with_invalid_post_id(self) -> None:
        """
        post_id가 None, 0, 음수 등 비정상 값일 때 404 반환
        """
        self.client.force_authenticate(user=self.user)
        for invalid_id in [None, 0, -1]:
            url = reverse("posts:post-comment-create", args=[invalid_id if invalid_id is not None else 0])
            response = self.client.post(url, {"content": "new comment"}, format="json")
            self.assertEqual(response.status_code, 404)
            self.assertIn("error_detail", response.data)


class PostCommentUpdateAPITestCase(APITestCase):
    """
    댓글 수정 API 테스트
    - 성공, 인증 실패, 미존재, 권한 실패, validation 실패 케이스 포함
    """

    def setUp(self) -> None:
        User = get_user_model()
        self.user = User.objects.create_user(
            email="updateuser@example.com",
            password="testpass",
            nickname="updateuser",
            phone_number="010-1111-2222",
            gender="MALE",
            birthday="1990-01-01",
        )
        self.other_user = User.objects.create_user(
            email="otheruser@example.com",
            password="testpass",
            nickname="otheruser",
            phone_number="010-3333-4444",
            gender="FEMALE",
            birthday="1995-05-05",
        )
        self.category = PostCategory.objects.create(name="update category")
        self.post = Post.objects.create(
            author=self.user,
            title="update post",
            content="update content",
            category=self.category,
        )
        self.comment = PostComment.objects.create(
            author=self.user,
            post=self.post,
            content="original comment",
        )
        self.url = reverse("posts:post-comment-update", args=[self.comment.id])

    def test_update_comment_success(self) -> None:
        """
        댓글 수정 성공 케이스
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.url, {"content": "updated comment"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["content"], "updated comment")
        self.assertEqual(response.data["id"], self.comment.id)

    def test_update_comment_unauthenticated(self) -> None:
        """
        인증되지 않은 사용자가 수정 시도할 때 401 반환
        """
        response = self.client.put(self.url, {"content": "updated comment"}, format="json")
        self.assertEqual(response.status_code, 401)
        self.assertIn("error_detail", response.data)
        self.assertEqual(response.data["error_detail"], CommentErrorMessage.UNAUTHORIZED)

    def test_update_comment_not_found(self) -> None:
        """
        존재하지 않는 댓글 수정 시도 시 404 반환
        """
        self.client.force_authenticate(user=self.user)
        url = reverse("posts:post-comment-update", args=[999999])
        response = self.client.put(url, {"content": "updated comment"}, format="json")
        self.assertEqual(response.status_code, 404)
        self.assertIn("error_detail", response.data)
        self.assertEqual(response.data["error_detail"], CommentErrorMessage.COMMENT_NOT_FOUND)

    def test_update_comment_forbidden(self) -> None:
        """
        작성자가 아닌 사용자가 댓글 수정 시도 시 403 반환
        """
        self.client.force_authenticate(user=self.other_user)
        response = self.client.put(self.url, {"content": "updated comment"}, format="json")
        self.assertEqual(response.status_code, 403)
        self.assertIn("error_detail", response.data)
        self.assertEqual(response.data["error_detail"], CommentErrorMessage.FORBIDDEN)

    def test_update_comment_validation_error(self) -> None:
        """
        댓글 내용이 비어 있을 때 400 반환
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.url, {"content": "   "}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("error_detail", response.data)
        self.assertIn("content", response.data["error_detail"])

    def test_update_comment_with_invalid_comment_id(self) -> None:
        """
        comment_id가 None, 0, 음수 등 비정상 값일 때 404 반환
        """
        self.client.force_authenticate(user=self.user)
        for invalid_id in [None, 0, -1]:
            url = reverse("posts:post-comment-update", args=[invalid_id if invalid_id is not None else 0])
            response = self.client.put(url, {"content": "updated comment"}, format="json")
            self.assertEqual(response.status_code, 404)
            self.assertIn("error_detail", response.data)


class PostCommentDeleteAPITestCase(APITestCase):
    """
    댓글 삭제 API 테스트
    - 성공, 인증 실패, 권한 실패, 미존재 댓글
    """

    def setUp(self) -> None:
        User = get_user_model()
        self.user = User.objects.create_user(
            email="deleteuser@example.com",
            password="testpass",
            nickname="deleteuser",
            phone_number="010-7777-8888",
            gender="MALE",
            birthday="1988-08-08",
        )
        self.other_user = User.objects.create_user(
            email="otheruser3@example.com",
            password="testpass",
            nickname="otheruser3",
            phone_number="010-9999-0000",
            gender="FEMALE",
            birthday="1993-03-03",
        )
        self.category = PostCategory.objects.create(name="delete category")
        self.post = Post.objects.create(
            author=self.user,
            title="delete post",
            content="delete content",
            category=self.category,
        )
        self.comment = PostComment.objects.create(
            author=self.user,
            post=self.post,
            content="delete comment",
        )
        self.delete_url = reverse("posts:post-comment-delete", args=[self.comment.id])

    def test_comment_delete_success(self) -> None:
        """
        댓글 삭제 성공
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("detail", response.data)

    def test_comment_delete_unauthenticated(self) -> None:
        """
        인증되지 않은 사용자가 댓글 삭제 시도 시 401 반환
        """
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, 401)
        self.assertIn("error_detail", response.data)
        self.assertEqual(response.data["error_detail"], CommentErrorMessage.UNAUTHORIZED)

    def test_comment_delete_forbidden(self) -> None:
        """
        작성자가 아닌 사용자가 댓글 삭제 시도 시 403 반환
        """
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, 403)
        self.assertIn("error_detail", response.data)
        self.assertEqual(response.data["error_detail"], CommentErrorMessage.FORBIDDEN)

    def test_comment_delete_not_found(self) -> None:
        """
        존재하지 않는 댓글 삭제 시도 시 404 반환
        """
        self.client.force_authenticate(user=self.user)
        url = reverse("posts:post-comment-delete", args=[999999])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)
        self.assertIn("error_detail", response.data)
        self.assertEqual(response.data["error_detail"], CommentErrorMessage.COMMENT_NOT_FOUND)

    def test_delete_comment_with_invalid_comment_id(self) -> None:
        """
        comment_id가 None, 0, 음수 등 비정상 값일 때 404 반환
        """
        self.client.force_authenticate(user=self.user)
        for invalid_id in [None, 0, -1]:
            url = reverse("posts:post-comment-delete", args=[invalid_id if invalid_id is not None else 0])

            response = self.client.delete(url)
            self.assertEqual(response.status_code, 404)
            self.assertIn("error_detail", response.data)


# === 랜덤 닉네임 API 테스트 ===
class PostCommentRandomNicknameAPITestCase(APITestCase):
    def setUp(self) -> None:
        self.nickname_url = reverse("posts:comment-random-nickname")

    def test_random_nickname_api(self) -> None:
        """랜덤 닉네임 API 200, 응답 키 확인"""
        response = self.client.get(self.nickname_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("nickname", response.data)
