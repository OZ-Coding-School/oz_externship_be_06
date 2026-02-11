from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.qna.models import Answer, QuestionCategory
from apps.qna.tests.factories import create_admin_user, create_student_user
from apps.users.models import User


class AdminCategoryListAPITest(APITestCase):
    """
    어드민 카테고리 목록 조회 API (GET) 테스트
    - 성공 케이스
        - 카테고리 전체 목록 조회
        - 필터링 조회 (category_type: 대분류/중분류/소분류)
        - 검색 조회 (search_keyword)
        - 페이지네이션 동작 확인
    - 실패 케이스
        - 401 Unauthorized: 로그인하지 않은 유저
        - 403 Forbidden: 스태프/관리자가 아닌 유저 (수강생, 일반유저)
    """

    admin_user: User
    student_user: User
    cat_large_1: QuestionCategory
    cat_large_2: QuestionCategory
    cat_medium_1: QuestionCategory
    cat_medium_2: QuestionCategory
    cat_small_1: QuestionCategory
    cat_small_2: QuestionCategory
    lc_answer: Answer
    om_answer: Answer
    url: str

    @classmethod
    def setUpTestData(cls) -> None:
        # 테스트용 유저
        cls.admin_user = create_admin_user()
        cls.student_user = create_student_user()

        # 카테고리 데이터 생성
        # 대분류 2개
        cls.cat_large_1 = QuestionCategory.objects.create(name="백엔드")
        cls.cat_large_2 = QuestionCategory.objects.create(name="프론트엔드")

        # 중분류 (백엔드 하위)
        cls.cat_medium_1 = QuestionCategory.objects.create(name="웹프레임워크", parent=cls.cat_large_1)
        cls.cat_medium_2 = QuestionCategory.objects.create(name="데이터베이스", parent=cls.cat_large_1)

        # 소분류 (웹프레임워크 하위)
        cls.cat_small_1 = QuestionCategory.objects.create(name="Django", parent=cls.cat_medium_1)
        cls.cat_small_2 = QuestionCategory.objects.create(name="FastAPI", parent=cls.cat_medium_1)

        # URL
        cls.url = reverse("admin-qna-categories")

    # ==========================================================================
    # 성공 케이스
    # ==========================================================================
    def test_list_all_categories_success(self) -> None:
        """[200] 필터 없이 전체 목록 조회"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url)
        res_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 총 6개 (대:2, 중:2, 소:2)
        self.assertEqual(res_data["total_count"], 6)
        self.assertEqual(len(res_data["categories"]), 6)

        # 구조 확인
        first_category = res_data["categories"][0]
        self.assertIn("category_id", first_category)
        self.assertIn("name", first_category)
        self.assertIn("category_type", first_category)
        self.assertIn("parent_category", first_category)
        self.assertIn("child_categories", first_category)

    def test_filter_by_large_category(self) -> None:
        """[200] '대분류' 필터링 조회"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url, {"category_type": "대분류"})
        res_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 백엔드, 프론트엔드 -> 2개
        self.assertEqual(res_data["total_count"], 2)
        for cat in res_data["categories"]:
            self.assertEqual(cat["category_type"], "대분류")

    def test_filter_by_medium_category(self) -> None:
        """[200] '중분류' 필터링 조회"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url, {"category_type": "중분류"})
        res_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 웹프레임워크, 데이터베이스 -> 2개
        self.assertEqual(res_data["total_count"], 2)
        for cat in res_data["categories"]:
            self.assertEqual(cat["category_type"], "중분류")

    def test_filter_by_small_category(self) -> None:
        """[200] '소분류' 필터링 조회"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url, {"category_type": "소분류"})
        res_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Django, FastAPI -> 2개
        self.assertEqual(res_data["total_count"], 2)
        for cat in res_data["categories"]:
            self.assertEqual(cat["category_type"], "소분류")

    def test_search_by_keyword(self) -> None:
        """[200] 검색어(search_keyword)로 조회"""
        self.client.force_authenticate(user=self.admin_user)
        # "Django" 검색
        response = self.client.get(self.url, {"search_keyword": "Django"})
        res_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(res_data["total_count"], 1)
        self.assertEqual(res_data["categories"][0]["name"], "Django")

    # ==========================================================================
    # 성공 케이스 - 페이지네이션 동작 확인
    # ==========================================================================
    def test_pagination_first_page(self) -> None:
        """[200] 첫 번째 페이지 조회"""
        # 기본 page_size는 20이므로 20개 이상의 카테고리 생성
        for i in range(25):
            QuestionCategory.objects.create(name=f"Category_{i:02d}")

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url, {"page": "1"})
        res_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(res_data["page"], 1)
        self.assertEqual(res_data["size"], 10)
        self.assertEqual(res_data["total_count"], 31)  # 기존 6개 + 추가 25개
        self.assertEqual(len(res_data["categories"]), 10)

    def test_pagination_second_page(self) -> None:
        """[200] 두 번째 페이지 조회"""
        # 기본 page_size 이상의 카테고리 생성
        for i in range(25):
            QuestionCategory.objects.create(name=f"Category_{i:02d}")

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url, {"page": "2"})
        res_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(res_data["page"], 2)
        self.assertEqual(res_data["size"], 10)
        self.assertEqual(res_data["total_count"], 31)
        self.assertEqual(len(res_data["categories"]), 10)  # 2번째 페이지는 남은 11개

    def test_pagination_custom_page_size(self) -> None:
        """[200] 커스텀 page_size로 조회"""
        for i in range(25):
            QuestionCategory.objects.create(name=f"Category_{i:02d}")

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url, {"page": "1", "size": "20"})
        res_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(res_data["page"], 1)
        self.assertEqual(res_data["size"], 20)
        self.assertEqual(res_data["total_count"], 31)
        self.assertEqual(len(res_data["categories"]), 20)

    # ==========================================================================
    # 성공 케이스 - 상속/계층 구조 응답 확인
    # ==========================================================================
    def test_response_hierarchy_info(self) -> None:
        """[200] 부모, 자식 카테고리 정보가 올바르게 내려오는지 확인"""
        self.client.force_authenticate(user=self.admin_user)

        # 소분류(Django) 조회 -> 부모가 '웹프레임워크'여야 함
        response = self.client.get(self.url, {"search_keyword": "Django"})
        django_cat = response.json()["categories"][0]
        self.assertEqual(django_cat["name"], "Django")
        self.assertEqual(django_cat["parent_category"], "웹프레임워크")
        self.assertEqual(django_cat["child_categories"], [])  # 소분류는 자식 없음

        # 중분류(웹프레임워크) 조회 -> 부모 '백엔드', 자식 ['Django', 'FastAPI']
        response = self.client.get(self.url, {"search_keyword": "웹프레임워크"})
        web_cat = response.json()["categories"][0]
        self.assertEqual(web_cat["name"], "웹프레임워크")
        self.assertEqual(web_cat["parent_category"], "백엔드")
        self.assertIn("Django", web_cat["child_categories"])
        self.assertIn("FastAPI", web_cat["child_categories"])

        # 대분류(백엔드) 조회 -> 부모 ''(빈문자열), 자식 ['웹프레임워크', '데이터베이스']
        response = self.client.get(self.url, {"search_keyword": "백엔드"})
        backend_cat = response.json()["categories"][0]
        self.assertEqual(backend_cat["name"], "백엔드")
        self.assertEqual(backend_cat["parent_category"], "")
        self.assertIn("웹프레임워크", backend_cat["child_categories"])
        self.assertIn("데이터베이스", backend_cat["child_categories"])

    # ==========================================================================
    # 실패 케이스
    # ==========================================================================
    def test_list_unauthorized(self) -> None:
        """[401] 로그인하지 않은 경우"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_forbidden(self) -> None:
        """[403] 수강생이 요청한 경우"""
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
