from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.posts.constants.post_const import PostLikeMessage
from apps.posts.models.post import Post
from apps.posts.models.post_category import PostCategory
from apps.posts.models.post_likes import PostLike
from apps.users.models.user import User


class PostLikeAPITest(APITestCase):
    """
    게시글 좋아요 등록(POST) 및 취소(DELETE) API 기능을 검증하는 테스트 클래스입니다.
    """

    def setUp(self) -> None:
        """
        테스트에 필요한 초기 데이터를 생성합니다.
        """
        self.user = User.objects.create_user(
            email="test_user@test.com",
            password="Password1234!",
            nickname="테스터",
            name="홍길동",
            phone_number="01012345678",
            gender="M",
            birthday="1995-01-01",
        )
        self.category = PostCategory.objects.create(name="커뮤니티")
        self.post = Post.objects.create(
            author=self.user,
            category=self.category,
            title="좋아요 테스트용 게시글",
            content="본문 내용",
        )
        # URL 설정: posts:post-like-registration (명세에 따른 name)
        self.url = reverse("posts:post-like", kwargs={"post_id": self.post.id})

        # 유저 인증 처리
        self.client.force_authenticate(user=self.user)

    def test_post_like_registration_success_status_201(self) -> None:
        """
        [POST] 좋아요 등록 성공 시 상태 코드 201과 명세된 메시지 및 데이터를 반환하는지 검증합니다.
        """
        # API 호출
        response = self.client.post(self.url)

        # 1. 상태 코드 201 검증
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 2. 응답 데이터 메시지 검증 (상수 활용)
        self.assertEqual(response.data["detail"], PostLikeMessage.LIKE_REGISTER)

        # 3. 데이터베이스 상태 검증
        like_exists = PostLike.objects.filter(user=self.user, post=self.post, is_liked=True).exists()
        self.assertTrue(like_exists)

    def test_post_like_idempotency_check(self) -> None:
        """
        [POST] 이미 좋아요를 누른 상태에서 다시 등록 요청 시, 중복 생성되지 않고 201을 유지하는지 검증합니다.
        """
        # 첫 번째 등록
        self.client.post(self.url)

        # 두 번째 등록 (중복 요청)
        response = self.client.post(self.url)

        # 멱등성 검증: 에러가 발생하지 않고 성공 응답 유지
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PostLike.objects.filter(user=self.user, post=self.post).count(), 1)
        self.assertTrue(PostLike.objects.get(user=self.user, post=self.post).is_liked)

    def test_post_like_cancel_success_status_200(self) -> None:
        """
        [DELETE] 좋아요 취소 성공 시 상태 코드 200과 취소 메시지를 반환하는지 검증합니다.
        """
        # 먼저 좋아요 데이터가 있는 상태를 만듦
        PostLike.objects.create(user=self.user, post=self.post, is_liked=True)

        # API 호출 (DELETE 메서드)
        response = self.client.delete(self.url)

        # 1. 상태 코드 200 검증
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 2. 메시지 검증
        self.assertEqual(response.data["detail"], PostLikeMessage.LIKE_CANCEL)

        # 3. 데이터베이스 필드 변경 검증 (물리 삭제가 아닌 상태값 변경)
        like = PostLike.objects.get(user=self.user, post=self.post)
        self.assertFalse(like.is_liked)

    def test_post_like_unauthorized_user_status_401(self) -> None:
        """
        인증되지 않은 유저가 접근 시 상태 코드 401을 반환하는지 검증합니다.
        """
        self.client.logout()
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_like_not_found_status_404(self) -> None:
        """
        존재하지 않는 게시글에 대해 좋아요 요청 시 상태 코드 404를 반환하는지 검증합니다.
        """
        invalid_url = reverse("posts:post-like", kwargs={"post_id": 9999})
        response = self.client.post(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
