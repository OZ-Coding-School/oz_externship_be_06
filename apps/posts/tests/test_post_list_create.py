from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from apps.posts.models import Post, PostCategory
from apps.users.models import User
from apps.posts.constants.post_const import PostSuccessMessage, PostErrorMessage
from unittest.mock import patch

class PostListCreateTest(APITestCase):
    @classmethod
    def setUpTestData(cls):
        """테스트 데이터 준비 (전체 테스트에서 한 번만 생성)"""
        cls.user = User.objects.create_user(
            email="senior@google.com",
            password="securepassword123",
            nickname="시니어개발자",
            name="김구글",
            phone_number="010-1111-2222",
            gender="MALE",
            birthday="1990-01-01"
        )
        cls.category_1 = PostCategory.objects.create(name="자유게시판")
        cls.category_2 = PostCategory.objects.create(name="Q&A게시판")

        # 목록 조회를 위한 대량 데이터 생성 (페이지네이션 테스트용)
        posts = []
        for i in range(15):
            category = cls.category_1 if i < 10 else cls.category_2
            posts.append(Post(
                author=cls.user,
                title=f"테스트 제목 {i}",
                content=f"테스트 내용입니다. {i} " * 10,  # 50자 이상으로 content_preview 테스트
                category=category
            ))
        Post.objects.bulk_create(posts)

        cls.url = reverse('post-list-create') # urls.py의 name 확인 필요

    # --- [GET] 게시글 목록 조회 테스트 ---

    def test_get_posts_list_200_pagination_structure(self):
        """GET 200: 명세서의 Pagination 구조(count, next, previous, results) 확인"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 1. 메타데이터 확인
        self.assertEqual(response.data["count"], 15)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)

        # 2. 결과 리스트 구조 확인
        results = response.data["results"]
        self.assertEqual(len(results), 10)  # page_size=10 가정

        # 3. 개별 객체 필드 확인 (author 중첩 구조 포함)
        first_post = results[0]
        self.assertIn("author", first_post)
        self.assertEqual(first_post["author"]["nickname"], self.user.nickname)
        self.assertIn("content_preview", first_post)
        self.assertIn("category_id", first_post)

    def test_get_posts_filtering_by_category(self):
        """GET 200: category_id 필터링이 정상 동작하는지 확인"""
        response = self.client.get(self.url, {'category_id': self.category_2.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # category_2 게시글은 5개 생성했음
        self.assertEqual(response.data["count"], 5)
        for post in response.data["results"]:
            self.assertEqual(post["category_id"], self.category_2.id)

    # --- [POST] 게시글 생성 테스트 ---

    def test_create_post_201_success(self):
        """POST 201: 성공적인 게시글 생성 및 응답 메시지 확인"""
        self.client.force_authenticate(user=self.user)
        data = {
            "title": "구글식 클린 코드",
            "content": "가독성이 가장 중요합니다.",
            "category_id": self.category_1.id
        }
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["detail"], PostSuccessMessage.POST_CREATE_SUCCESS)
        self.assertTrue("pk" in response.data)

    def test_create_post_400_validation_error(self):
        """POST 400: 필수 필드 누락 시 명세서의 error_detail 구조 확인"""
        self.client.force_authenticate(user=self.user)
        data = {"content": "제목이 없어요."} # title 누락
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # 명세서: {"error_detail": {"title": ["..."]}}
        self.assertIn("error_detail", response.data)
        self.assertIn("title", response.data["error_detail"])

    def test_create_post_401_unauthorized(self):
        """POST 401: 비로그인 유저의 작성 시도 시 커스텀 예외 메시지 확인"""
        self.client.logout() # 인증 해제
        data = {"title": "비밀글", "content": "쉿", "category_id": self.category_1.id}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data["error_detail"], PostErrorMessage.UNAUTHORIZED)

    @patch('apps.posts.services.post_services.PostService.create_post')
    def test_create_post_500_server_error(self, mock_create):
        """POST 500: 예기치 못한 서버 오류 시 공통 에러 메시지 확인"""
        self.client.force_authenticate(user=self.user)
        mock_create.side_effect = Exception("DB Connection Error")

        data = {"title": "오류 테스트", "content": "오류", "category_id": self.category_1.id}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data["error_detail"], PostErrorMessage.SERVER_ERROR)