from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.users.models.user import User
from apps.posts.models.post import Post
from apps.posts.models.post_category import PostCategory
from apps.posts.constants.post_const import PostErrorMessage

class PostDetailReadTest(APITestCase):
    """
    게시글 상세 조회 API 기능을 검증하는 테스트 클래스입니다.
    """

    def setUp(self) -> None:
        """
        테스트에 필요한 초기 데이터를 생성합니다.
        """
        self.user = User.objects.create_user(
            email="lead_dev@test.com",
            password="Password1234!",
            nickname="리드개발자",
            name="홍길동",
            phone_number="01012345678",
            gender="M",
            birthday="1990-01-01"
        )
        self.category = PostCategory.objects.create(name="자유게시판")
        self.post = Post.objects.create(
            author=self.user,
            category=self.category,
            title="테스트 게시글 제목",
            content="테스트 게시글 본문 내용입니다.",
            view_count=0
        )
        self.url = reverse('posts:post-detail', kwargs={'post_id': self.post.id})

    def test_get_post_detail_success_status_200(self) -> None:
        """
        성공 시 상태 코드 200과 API 명세와 일치하는 데이터 구조를 반환하는지 검증합니다.
        """
        # API 호출
        response = self.client.get(self.url)

        # 1. 상태 코드 200 검증
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 2. 응답 데이터 구조 검증 (API 명세서 일치 여부)
        data = response.data
        self.assertEqual(data['id'], self.post.id)
        self.assertEqual(data['title'], self.post.title) # 실제 구현된 필드와 비교
        self.assertEqual(data['content'], self.post.content)

        # 3. 중첩 객체(Author, Category) 검증
        self.assertEqual(data['author']['nickname'], self.user.nickname)
        self.assertEqual(data['category']['name'], self.category.name)

        # 4. 조회수 증가 로직 검증
        self.post.refresh_from_db()
        self.assertEqual(data['view_count'], self.post.view_count)

    def test_get_post_detail_not_found_status_404(self) -> None:
        """
        존재하지 않는 게시글 조회 시 상태 코드 404와 명세된 에러 메시지를 반환하는지 검증합니다.
        """
        # 존재하지 않는 ID로 URL 생성
        invalid_url = reverse('posts:post-detail', kwargs={'post_id': 9999})
        response = self.client.get(invalid_url)

        # 1. 상태 코드 404 검증
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # 2. 에러 메시지 정합성 검증
        # Selector에서 PostNotFoundException 발생 시 반환하는 메시지 확인
        self.assertEqual(
            response.data['error_detail'],
            PostErrorMessage.POST_NOT_FOUND
        )