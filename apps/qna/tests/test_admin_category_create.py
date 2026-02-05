import json
from typing import Any

from django.contrib.auth import get_user_model
from django.db import connection
from django.test import Client, TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from apps.qna.constants import ErrorMessages
from apps.qna.models import QuestionCategory

User = get_user_model()


class AdminCategoryCreateAPITest(TestCase):
    """
    어드민 카테고리 등록 API (POST) 테스트
    - 성공 케이스
        - 대분류 카테고리 등록
        - 중분류 카테고리 등록
        - 소분류 카테고리 등록
    - 실패 케이스
        - 401 Unauthorized: 로그인하지 않은 유저
        - 403 Forbidden: 스태프/관리자가 아닌 유저 (수강생, 일반유저)
        - 400 Bad Request: 필수 입력값 누락, depth/parent_id 조합 오류, 부모 계층 불일치
        - 404 Not Found: 존재하지 않는 부모 카테고리
        - 409 Conflict: 동일한 이름의 카테고리 중복
    - 성능 테스트 (쿼리 수 검증)
    """

    def setUp(self) -> None:
        self.client = Client()
        self.url = reverse("admin-qna-category-create")

        # 카테고리 계층 생성 (대분류 → 중분류 → 소분류)
        self.cat_large = QuestionCategory.objects.create(name="백엔드")
        self.cat_medium = QuestionCategory.objects.create(name="웹프레임워크", parent=self.cat_large)
        self.cat_small = QuestionCategory.objects.create(name="Django", parent=self.cat_medium)

        # 스태프 유저 (관리자)
        self.admin_user = User.objects.create_user(
            email="admin@ozcoding.com",
            password="password123",
            name="관리자",
            nickname="관리자",
            role="ADMIN",
            gender="MALE",
            birthday="1990-01-01",
            is_active=True,
        )

        # 스태프 유저 (조교)
        self.ta_user = User.objects.create_user(
            email="ta@ozcoding.com",
            password="password123",
            name="조교",
            nickname="조교",
            role="TA",
            gender="MALE",
            birthday="1991-01-01",
            is_active=True,
        )

        # 수강생 유저 (권한 없음)
        self.student_user = User.objects.create_user(
            email="student@ozcoding.com",
            password="password123",
            name="수강생",
            nickname="수강생",
            role="STUDENT",
            gender="MALE",
            birthday="1995-01-01",
            is_active=True,
        )

        # 일반 유저 (권한 없음)
        self.general_user = User.objects.create_user(
            email="general@ozcoding.com",
            password="password123",
            name="일반유저",
            nickname="일반유저",
            role="USER",
            gender="MALE",
            birthday="1995-05-05",
            is_active=True,
        )

    def _get_auth_header(self, user: Any) -> dict[str, Any]:
        """유저 객체를 받아 JWT 액세스 토큰을 생성, HTTP_AUTHORIZATION 헤더 딕셔너리를 반환"""
        refresh = RefreshToken.for_user(user)
        return {"HTTP_AUTHORIZATION": f"Bearer {str(refresh.access_token)}"}

    # ==========================================================================
    # 성공 케이스
    # ==========================================================================

    def test_create_large_category_success(self) -> None:
        """[성공] 관리자가 대분류 카테고리 등록"""
        auth_header = self._get_auth_header(self.admin_user)
        data = {"depth": 0, "name": "프론트엔드", "parent_id": None}

        response = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json", secure=False, **auth_header
        )
        res_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res_data["name"], "프론트엔드")
        self.assertEqual(res_data["category_type"], "large")
        self.assertIsNone(res_data["parent_id"])
        self.assertIn("category_id", res_data)
        self.assertIn("created_at", res_data)
        self.assertTrue(QuestionCategory.objects.filter(id=res_data["category_id"]).exists())

    def test_create_medium_category_success(self) -> None:
        """[성공] 조교가 중분류 카테고리 등록"""
        auth_header = self._get_auth_header(self.ta_user)
        data = {"depth": 1, "name": "프로그래밍 언어", "parent_id": self.cat_large.id}

        response = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json", secure=False, **auth_header
        )
        res_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res_data["name"], "프로그래밍 언어")
        self.assertEqual(res_data["category_type"], "medium")
        self.assertEqual(res_data["parent_id"], self.cat_large.id)

    def test_create_small_category_success(self) -> None:
        """[성공] 관리자가 소분류 카테고리 등록"""
        auth_header = self._get_auth_header(self.admin_user)
        data = {"depth": 2, "name": "FastAPI", "parent_id": self.cat_medium.id}

        response = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json", secure=False, **auth_header
        )
        res_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res_data["name"], "FastAPI")
        self.assertEqual(res_data["category_type"], "small")
        self.assertEqual(res_data["parent_id"], self.cat_medium.id)

    def test_create_category_without_parent_id_field(self) -> None:
        """[성공] 대분류 등록 시 parent_id 필드 자체를 생략해도 정상 동작"""
        auth_header = self._get_auth_header(self.admin_user)
        data = {"depth": 0, "name": "데브옵스"}

        response = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json", secure=False, **auth_header
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(response.json()["parent_id"])

    # ==========================================================================
    # 실패 케이스 - 401 Unauthorized
    # ==========================================================================

    def test_create_category_unauthorized(self) -> None:
        """[실패] 로그인하지 않은 경우 401 에러 반환"""
        data = {"depth": 0, "name": "테스트", "parent_id": None}

        response = self.client.post(self.url, data=json.dumps(data), content_type="application/json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()["error_detail"], ErrorMessages.UNAUTHORIZED_ADMIN_CATEGORY_CREATE.value)

    # ==========================================================================
    # 실패 케이스 - 403 Forbidden
    # ==========================================================================

    def test_create_category_forbidden_student(self) -> None:
        """[실패] 수강생 권한으로 요청 시 403 에러 반환"""
        auth_header = self._get_auth_header(self.student_user)
        data = {"depth": 0, "name": "테스트", "parent_id": None}

        response = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json", secure=False, **auth_header
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["error_detail"], ErrorMessages.FORBIDDEN_ADMIN_CATEGORY_CREATE.value)

    def test_create_category_forbidden_general_user(self) -> None:
        """[실패] 일반 유저 권한으로 요청 시 403 에러 반환"""
        auth_header = self._get_auth_header(self.general_user)
        data = {"depth": 0, "name": "테스트", "parent_id": None}

        response = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json", secure=False, **auth_header
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["error_detail"], ErrorMessages.FORBIDDEN_ADMIN_CATEGORY_CREATE.value)

    # ==========================================================================
    # 실패 케이스 - 400 Bad Request (입력값 누락)
    # ==========================================================================

    def test_create_category_missing_depth(self) -> None:
        """[실패] 필수 필드 depth 누락 시 400 에러 반환"""
        auth_header = self._get_auth_header(self.admin_user)
        data = {"name": "테스트", "parent_id": None}

        response = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json", secure=False, **auth_header
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["error_detail"], ErrorMessages.INVALID_ADMIN_CATEGORY_CREATE.value)

    def test_create_category_missing_name(self) -> None:
        """[실패] 필수 필드 name 누락 시 400 에러 반환"""
        auth_header = self._get_auth_header(self.admin_user)
        data = {"depth": 0, "parent_id": None}

        response = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json", secure=False, **auth_header
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["error_detail"], ErrorMessages.INVALID_ADMIN_CATEGORY_CREATE.value)

    def test_create_category_invalid_depth(self) -> None:
        """[실패] 유효하지 않은 depth 값(3) 전송 시 400 에러 반환"""
        auth_header = self._get_auth_header(self.admin_user)
        data = {"depth": 3, "name": "테스트", "parent_id": None}

        response = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json", secure=False, **auth_header
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ==========================================================================
    # 실패 케이스 - 400 Bad Request (depth/parent_id 조합 오류 - 시리얼라이저 검증)
    # ==========================================================================

    def test_create_large_category_with_parent_id(self) -> None:
        """[실패] 대분류(depth=0)인데 parent_id를 지정한 경우 400 에러 반환"""
        auth_header = self._get_auth_header(self.admin_user)
        data = {"depth": 0, "name": "테스트", "parent_id": self.cat_large.id}

        response = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json", secure=False, **auth_header
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_medium_category_without_parent_id(self) -> None:
        """[실패] 중분류(depth=1)인데 parent_id가 없는 경우 400 에러 반환"""
        auth_header = self._get_auth_header(self.admin_user)
        data = {"depth": 1, "name": "테스트", "parent_id": None}

        response = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json", secure=False, **auth_header
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_small_category_without_parent_id(self) -> None:
        """[실패] 소분류(depth=2)인데 parent_id가 없는 경우 400 에러 반환"""
        auth_header = self._get_auth_header(self.admin_user)
        data = {"depth": 2, "name": "테스트", "parent_id": None}

        response = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json", secure=False, **auth_header
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ==========================================================================
    # 실패 케이스 - 400 Bad Request (부모 계층 불일치 - 서비스 검증)
    # ==========================================================================

    def test_create_medium_category_with_medium_parent(self) -> None:
        """[실패] 중분류(depth=1) 등록 시 부모가 중분류(depth=1)인 경우 400 에러 반환"""
        auth_header = self._get_auth_header(self.admin_user)
        data = {"depth": 1, "name": "테스트", "parent_id": self.cat_medium.id}

        response = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json", secure=False, **auth_header
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_small_category_with_large_parent(self) -> None:
        """[실패] 소분류(depth=2) 등록 시 부모가 대분류(depth=0)인 경우 400 에러 반환"""
        auth_header = self._get_auth_header(self.admin_user)
        data = {"depth": 2, "name": "테스트", "parent_id": self.cat_large.id}

        response = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json", secure=False, **auth_header
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ==========================================================================
    # 실패 케이스 - 404 Not Found
    # ==========================================================================

    def test_create_category_parent_not_found(self) -> None:
        """[실패] 존재하지 않는 부모 카테고리 ID로 요청 시 404 에러 반환"""
        auth_header = self._get_auth_header(self.admin_user)
        data = {"depth": 1, "name": "테스트", "parent_id": 99999}

        response = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json", secure=False, **auth_header
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["error_detail"], ErrorMessages.NOT_FOUND_ADMIN_CATEGORY_PARENT.value)

    # ==========================================================================
    # 실패 케이스 - 409 Conflict
    # ==========================================================================

    def test_create_category_duplicate_name_same_parent(self) -> None:
        """[실패] 같은 부모 하위에 동일한 이름의 카테고리가 존재하는 경우 409 에러 반환"""
        auth_header = self._get_auth_header(self.admin_user)
        data = {"depth": 1, "name": "웹프레임워크", "parent_id": self.cat_large.id}

        response = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json", secure=False, **auth_header
        )

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.json()["error_detail"], ErrorMessages.ALREADY_EXISTS_ADMIN_CATEGORY_NAME.value)

    def test_create_category_duplicate_name_different_parent_success(self) -> None:
        """[성공] 다른 부모 하위에 같은 이름의 카테고리는 등록 가능"""
        # 새 대분류 생성
        new_large = QuestionCategory.objects.create(name="프론트엔드")

        auth_header = self._get_auth_header(self.admin_user)
        data = {"depth": 1, "name": "웹프레임워크", "parent_id": new_large.id}

        response = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json", secure=False, **auth_header
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["name"], "웹프레임워크")

    def test_create_category_duplicate_name_at_root(self) -> None:
        """[실패] 대분류에서 동일한 이름의 카테고리가 존재하는 경우 409 에러 반환"""
        auth_header = self._get_auth_header(self.admin_user)
        data = {"depth": 0, "name": "백엔드", "parent_id": None}

        response = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json", secure=False, **auth_header
        )

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    # ==========================================================================
    # 응답 데이터 구조 검증
    # ==========================================================================

    def test_response_data_structure(self) -> None:
        """[성공] 응답 데이터에 명세서에 정의된 모든 필드가 포함되어 있는지 확인"""
        auth_header = self._get_auth_header(self.admin_user)
        data = {"depth": 0, "name": "데이터사이언스", "parent_id": None}

        response = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json", secure=False, **auth_header
        )
        res_data = response.json()

        expected_fields = {"category_id", "name", "category_type", "parent_id", "created_at"}
        self.assertEqual(set(res_data.keys()), expected_fields)

    def test_response_created_at_format(self) -> None:
        """[성공] created_at 필드가 'YYYY-MM-DD HH:MM:SS' 형식인지 확인"""
        auth_header = self._get_auth_header(self.admin_user)
        data = {"depth": 0, "name": "디자인", "parent_id": None}

        response = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json", secure=False, **auth_header
        )
        res_data = response.json()

        # 'YYYY-MM-DD HH:MM:SS' 형식 검증 (19자)
        self.assertEqual(len(res_data["created_at"]), 19)
        self.assertEqual(res_data["created_at"][4], "-")
        self.assertEqual(res_data["created_at"][10], " ")

    # ==========================================================================
    # DB 정합성 검증
    # ==========================================================================

    def test_category_saved_with_correct_parent(self) -> None:
        """[성공] 생성된 카테고리의 parent FK가 DB에 올바르게 저장되었는지 확인"""
        auth_header = self._get_auth_header(self.admin_user)
        data = {"depth": 1, "name": "OS", "parent_id": self.cat_large.id}

        response = self.client.post(
            self.url, data=json.dumps(data), content_type="application/json", secure=False, **auth_header
        )
        res_data = response.json()

        category = QuestionCategory.objects.get(id=res_data["category_id"])
        self.assertEqual(category.parent_id, self.cat_large.id)
        self.assertEqual(category.name, "OS")
        self.assertEqual(category.depth, 1)

    # ==========================================================================
    # 성능 테스트
    # ==========================================================================

    def test_create_category_performance(self) -> None:
        """[성능] 카테고리 등록 시 발생하는 쿼리 수 검증"""
        auth_header = self._get_auth_header(self.admin_user)
        data = {"depth": 1, "name": "라이브러리", "parent_id": self.cat_large.id}

        # Query Expectation:
        # 1. Auth check (User)
        # 2. Permission check (Role)
        # 3. Parent category lookup (GET)
        # 4. Parent depth calculation (parent chain)
        # 5. Duplicate name check (EXISTS)
        # 6. Create category (INSERT)
        # 7. SAVEPOINT / RELEASE (atomic)

        with CaptureQueriesContext(connection) as context:
            self.client.post(
                self.url, data=json.dumps(data), content_type="application/json", secure=False, **auth_header
            )

        self.assertLessEqual(len(context), 8, f"Expected 8 or fewer queries, but got {len(context)}")
