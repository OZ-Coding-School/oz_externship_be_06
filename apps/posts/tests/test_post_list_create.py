from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.posts.constants.post_const import PostErrorMessage, PostSuccessMessage
from apps.posts.models import Post, PostCategory
from apps.users.models import User

class PostListCreateTest(APITestCase):
    """
    Django 내장 APITestCase를 사용하여 추가 설치 없이 동작하는 테스트 클래스입니다.
    """
    user: User
    category_1: PostCategory
    category_2: PostCategory
    url: str

    @classmethod
    def setUpTestData(cls) -> None:
        """
        테스트 실행 전 전체 클래스에서 공통으로 사용할 데이터를 생성합니다.
        """
        # 테스트 유저 생성
        cls.user = User.objects.create_user(
            email="senior@ozcoding.com",
            password="securepassword123",
            nickname="시니어개발자",
            name="김개발",
            phone_number="010-1234-5678",
            gender="MALE",
            birthday="1990-01-01"
        )

        # 테스트 카테고리 생성
        cls.category_1 = PostCategory.objects.create(name="자유게시판", status=True)
        cls.category_2 = PostCategory.objects.create(name="공지사항", status=True)

        # 대량의 테스트 게시글 생성 (페이지네이션 및 필터링 테스트용)
        posts = []
        for i in range(15):
            category = cls.category_1 if i < 10 else cls.category_2
            posts.append(Post(
                author=cls.user,
                title=f"테스트 제목 {i}",
                content=f"테스트 내용입니다. {i}",
                category=category
            ))
        Post.objects.bulk_create(posts)

        # API URL (urls.py의 namespace:name 확인 필요)
        cls.url = reverse('posts:post-list-create')

    def test_get_posts_list_pagination_success(self) -> None:
        """게시글 목록 조회의 페이지네이션 구조를 검증합니다."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)  # 페이지네이션 결과 키 확인
        self.assertEqual(len(response.data["results"]), 10)  # 기본 페이지 사이즈 확인

    def test_get_posts_filtering_by_category(self) -> None:
        """카테고리 ID를 통한 필터링 기능이 정확한지 검증합니다."""
        response = self.client.get(self.url, {'category_id': self.category_2.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # category_2에 해당하는 게시글은 5개 생성됨
        self.assertEqual(response.data["count"], 5)

    def test_create_post_authenticated_success(self) -> None:
        """인증된 유저가 게시글을 정상적으로 생성하는지 검증합니다."""
        self.client.force_authenticate(user=self.user)
        data = {
            "title": "실무형 게시글",
            "content": "내용입니다.",
            "category_id": self.category_1.id
        }
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["detail"], PostSuccessMessage.POST_CREATE_SUCCESS)

    def test_create_post_unauthorized_fail(self) -> None:
        """비로그인 유저의 게시글 작성이 차단되는지 검증합니다."""
        self.client.logout()
        data = {"title": "실패예정", "content": "내용", "category_id": self.category_1.id}
        response = self.client.post(self.url, data)

        # PostListCreateView에서 정의한 커스텀 익셉션 또는 401 반환 확인
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)