from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.posts.models import Post, PostCategory, PostComment
from apps.users.models import User as UserModel  # 타입 힌트용

User = get_user_model()


class PostCommentViewTest(APITestCase):
    # [1] 클래스 변수 타입 미리 선언 (mypy 에러 해결 핵심!)
    user: UserModel
    other_user: UserModel
    category: PostCategory
    post: Post
    comment: PostComment

    create_url: str
    list_url: str
    detail_url: str
    update_url: str
    delete_url: str
    nickname_url: str

    @classmethod
    def setUpTestData(cls) -> None:  # [2] 반환 타입 명시
        # 1. 유저 생성
        cls.user = User.objects.create_user(
            email="test@test.com", password="password123", nickname="작성자", birthday="2000-01-01"
        )

        cls.other_user = User.objects.create_user(
            email="hacker@test.com", password="password123", nickname="해커", birthday="2000-01-01"
        )

        # 2. 데이터 생성
        cls.category = PostCategory.objects.create(name="자유게시판")
        cls.post = Post.objects.create(author=cls.user, category=cls.category, title="테스트 게시글", content="내용")

        cls.comment = PostComment.objects.create(post=cls.post, author=cls.user, content="원본 댓글입니다.")

        # 3. URL 설정 (posts: 네임스페이스)
        cls.create_url = reverse("posts:post-comment-create", kwargs={"post_id": cls.post.id})
        cls.list_url = reverse("posts:post-comment-list", kwargs={"post_id": cls.post.id})
        cls.detail_url = reverse(
            "posts:post-comment-detail", kwargs={"post_id": cls.post.id, "comment_id": cls.comment.id}
        )
        cls.update_url = reverse(
            "posts:post-comment-update", kwargs={"post_id": cls.post.id, "comment_id": cls.comment.id}
        )
        cls.delete_url = reverse(
            "posts:post-comment-delete", kwargs={"post_id": cls.post.id, "comment_id": cls.comment.id}
        )

    def setUp(self) -> None:  # [2] 반환 타입 명시
        self.client.force_authenticate(user=self.user)

    # ----------------------------------------------------------------
    # 각 테스트 함수에도 -> None 추가
    # ----------------------------------------------------------------

    def test_create_comment_success(self) -> None:
        """로그인한 유저는 댓글을 작성할 수 있다 (201)"""
        data = {"content": "새로운 댓글"}
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_comment_unauthorized(self) -> None:
        """로그인하지 않으면 작성 불가 (403)"""
        self.client.logout()
        response = self.client.post(self.create_url, {"content": "댓글"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_comment_empty(self) -> None:
        """내용이 없으면 작성 불가 (400)"""
        response = self.client.post(self.create_url, {"content": ""})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_comments_success(self) -> None:
        """댓글 목록 조회 성공 (200)"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(response.data["count"], 1)

    def test_detail_comment_success(self) -> None:
        """댓글 상세 조회 성공 (200)"""
        self.client.logout()
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["content"], "원본 댓글입니다.")

    def test_detail_comment_not_found(self) -> None:
        """없는 댓글 조회 시 404"""
        wrong_url = reverse("posts:post-comment-detail", kwargs={"post_id": self.post.id, "comment_id": 9999})
        response = self.client.get(wrong_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_comment_success(self) -> None:
        """작성자는 본인 댓글을 수정할 수 있다 (200)"""
        data = {"content": "수정된 댓글"}
        response = self.client.put(self.update_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["content"], "수정된 댓글")

        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, "수정된 댓글")

    def test_update_comment_forbidden(self) -> None:
        """다른 유저는 남의 댓글을 수정할 수 없다 (403)"""
        self.client.force_authenticate(user=self.other_user)
        data = {"content": "해킹된 댓글"}
        response = self.client.put(self.update_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_comment_success(self) -> None:
        """작성자는 본인 댓글을 삭제할 수 있다 (200)"""
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(PostComment.objects.filter(id=self.comment.id).exists())

    def test_delete_comment_forbidden(self) -> None:
        """다른 유저는 남의 댓글을 삭제할 수 없다 (403)"""
        self.client.force_authenticate(user=self.other_user)
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)