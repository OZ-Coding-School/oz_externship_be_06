from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.posts.services.comment.comment_nickname_services import (
    generate_comment_nickname,
)



class PostCommentNicknameServiceTests(TestCase):
    """댓글 닉네임 생성 서비스 테스트"""

    def test_nickname_format(self) -> None:
        """생성된 닉네임이 형식에 맞는지 확인 (형용사+동물)"""
        nickname = generate_comment_nickname()
        self.assertIn(" ", nickname)
        adj, animal = nickname.split()
        self.assertTrue(adj)
        self.assertTrue(animal)

    def test_nickname_randomness(self) -> None:
        """여러 번 생성 시 닉네임 다양성 확인"""
        results = set(generate_comment_nickname() for _ in range(20))
        self.assertGreaterEqual(len(results), 5)


class PostCommentRandomNicknameAPITestCase(APITestCase):
    def setUp(self) -> None:
        """랜덤 닉네임 API URL 준비"""
        self.nickname_url = reverse("posts:comment-random-nickname")

    def test_random_nickname_api(self) -> None:
        """랜덤 닉네임 API 200 응답 및 닉네임 키 포함"""
        response = self.client.get(self.nickname_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("nickname", response.data)
