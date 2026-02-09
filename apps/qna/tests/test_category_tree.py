import json

from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from apps.qna.docs.api_response_examples import SuccessResponseExamples
from apps.qna.models import QuestionCategory


class CategoryTreeAPITest(TestCase):
    """
    카테고리 계층 구조 조회 API (GET) 테스트
    - 성공 케이스 (권한 있는 유저)
        - 실제 DB의 계층 구조 데이터 정합성 검증
        - 재귀적 트리 구조(Nesting)의 유효성 검증
    """

    cat_be: QuestionCategory
    cat_fe: QuestionCategory
    cat_django: QuestionCategory
    cat_orm: QuestionCategory
    url: str

    @classmethod
    def setUpTestData(cls) -> None:
        """테스트 데이터 생성"""
        # 대분류
        cls.cat_be = QuestionCategory.objects.create(name="백엔드")
        cls.cat_fe = QuestionCategory.objects.create(name="프론트엔드")

        # 중분류 (백엔드 하위)
        cls.cat_django = QuestionCategory.objects.create(name="Django", parent=cls.cat_be)

        # 소분류 (Django 하위)
        cls.cat_orm = QuestionCategory.objects.create(name="ORM", parent=cls.cat_django)

        # [요청 반영] urls에서 지정하신 name으로 수정
        cls.url = reverse("question-category-list")

    def test_get_category_tree_success(self) -> None:
        """[성공] 실제 DB 데이터를 기반으로 전체 트리 구조를 반환하는지 확인"""
        response = self.client.get(self.url)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("categories", data)
        self.assertEqual(len(data["categories"]), 2)

    def test_category_tree_recursive_nesting(self) -> None:
        """[성공] 데이터가 대 > 중 > 소 순서로 재귀적으로 중첩되어 있는지 확인"""
        response = self.client.get(self.url)
        data = response.json()

        # '백엔드' 카테고리 확인
        backend = next(c for c in data["categories"] if c["name"] == "백엔드")
        self.assertEqual(backend["depth"], 0)

        # 중분류 확인 (Django)
        django = backend["subcategories"][0]
        self.assertEqual(django["name"], "Django")
        self.assertEqual(django["depth"], 1)

        # 소분류 확인 (ORM)
        orm = django["subcategories"][0]
        self.assertEqual(orm["name"], "ORM")
        self.assertEqual(orm["depth"], 2)
        self.assertEqual(orm["subcategories"], [])

    def test_get_category_tree_empty(self) -> None:
        """[성공] 데이터가 없을 경우 빈 리스트 반환 확인"""
        QuestionCategory.objects.all().delete()
        response = self.client.get(self.url)
        self.assertEqual(response.json()["categories"], [])
