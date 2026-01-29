from datetime import date, timedelta
from typing import Any

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from apps.courses.models import Cohort, CohortStudent, Course
from apps.courses.models.learning_coachs import LearningCoach
from apps.courses.models.operation_managers import OperationManager
from apps.courses.models.training_assistants import TrainingAssistant
from apps.users.models import User


class AdminAccountRoleUpdateAPITest(TestCase):
    """어드민 권한 변경 API 테스트."""

    def setUp(self) -> None:
        self.client = APIClient()

        # 과정 생성
        self.course = Course.objects.create(
            name="백엔드 부트캠프",
            tag="BE",
            description="백엔드 과정",
            thumbnail_img_url="https://example.com/be.png",
        )
        self.course2 = Course.objects.create(
            name="프론트엔드 부트캠프",
            tag="FE",
            description="프론트엔드 과정",
            thumbnail_img_url="https://example.com/fe.png",
        )

        # 기수 생성
        self.cohort = Cohort.objects.create(
            course=self.course,
            number=1,
            max_student=30,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=180),
            status=Cohort.StatusChoices.IN_PROGRESS,
        )

        # 관리자 유저
        self.admin_user = User.objects.create_user(
            email="admin@example.com",
            password="password123",
            name="관리자",
            nickname="관리자",
            phone_number="01011111111",
            gender=User.Gender.MALE,
            birthday=date(1990, 1, 1),
            role=User.Role.ADMIN,
        is_active=True,
        )

        # 일반 유저 (권한 변경 대상)
        self.target_user = User.objects.create_user(
            email="target@example.com",
            password="password123",
            name="대상유저",
            nickname="대상유저",
            phone_number="01022222222",
            gender=User.Gender.MALE,
            birthday=date(2000, 1, 1),
            role=User.Role.USER,
        is_active=True,
        )

        # 조교 유저 (권한 변경 불가 테스트용)
        self.ta_user = User.objects.create_user(
            email="ta@example.com",
            password="password123",
            name="조교",
            nickname="조교",
            phone_number="01033333333",
            gender=User.Gender.FEMALE,
            birthday=date(1995, 5, 5),
            role=User.Role.TA,
        is_active=True,
        )

    def _get_url(self, account_id: int) -> str:
        return f"/api/v1/admin/accounts/{account_id}/role/"

    def _auth_headers(self, user: User) -> Any:
        token = AccessToken.for_user(user)
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    def test_change_role_to_admin(self) -> None:
        """일반 유저를 관리자로 변경할 수 있다."""
        response = self.client.patch(
            self._get_url(self.target_user.id),
            data={"role": "ADMIN"},
            content_type="application/json",
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["detail"], "권한이 변경되었습니다.")

        self.target_user.refresh_from_db()
        self.assertEqual(self.target_user.role, User.Role.ADMIN)

    def test_change_role_to_ta_with_cohort(self) -> None:
        """조교로 변경 시 기수를 함께 지정할 수 있다."""
        response = self.client.patch(
            self._get_url(self.target_user.id),
            data={"role": "TA", "cohort_id": self.cohort.id},
            content_type="application/json",
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.target_user.refresh_from_db()
        self.assertEqual(self.target_user.role, User.Role.TA)
        self.assertTrue(TrainingAssistant.objects.filter(user=self.target_user, cohort=self.cohort).exists())

    def test_change_role_to_ta_without_cohort_fails(self) -> None:
        """조교로 변경 시 기수가 없으면 실패한다."""
        response = self.client.patch(
            self._get_url(self.target_user.id),
            data={"role": "TA"},
            content_type="application/json",
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("cohort_id", response.json()["error_detail"])

    def test_change_role_to_student_with_cohort(self) -> None:
        """수강생으로 변경 시 기수를 함께 지정할 수 있다."""
        response = self.client.patch(
            self._get_url(self.target_user.id),
            data={"role": "STUDENT", "cohort_id": self.cohort.id},
            content_type="application/json",
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.target_user.refresh_from_db()
        self.assertEqual(self.target_user.role, User.Role.STUDENT)
        self.assertTrue(CohortStudent.objects.filter(user=self.target_user, cohort=self.cohort).exists())

    def test_change_role_to_lc_with_courses(self) -> None:
        """러닝코치로 변경 시 담당 과정을 지정할 수 있다."""
        response = self.client.patch(
            self._get_url(self.target_user.id),
            data={"role": "LC", "assigned_courses": [self.course.id, self.course2.id]},
            content_type="application/json",
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.target_user.refresh_from_db()
        self.assertEqual(self.target_user.role, User.Role.LC)
        self.assertEqual(LearningCoach.objects.filter(user=self.target_user).count(), 2)

    def test_change_role_to_lc_without_courses_fails(self) -> None:
        """러닝코치로 변경 시 담당 과정이 없으면 실패한다."""
        response = self.client.patch(
            self._get_url(self.target_user.id),
            data={"role": "LC"},
            content_type="application/json",
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("assigned_courses", response.json()["error_detail"])

    def test_change_role_to_om_with_courses(self) -> None:
        """운영매니저로 변경 시 담당 과정을 지정할 수 있다."""
        response = self.client.patch(
            self._get_url(self.target_user.id),
            data={"role": "OM", "assigned_courses": [self.course.id]},
            content_type="application/json",
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.target_user.refresh_from_db()
        self.assertEqual(self.target_user.role, User.Role.OM)
        self.assertEqual(OperationManager.objects.filter(user=self.target_user).count(), 1)

    def test_old_role_relations_are_cleared(self) -> None:
        """권한 변경 시 기존 역할 관련 데이터가 삭제된다."""
        # 먼저 조교로 변경
        self.client.patch(
            self._get_url(self.target_user.id),
            data={"role": "TA", "cohort_id": self.cohort.id},
            content_type="application/json",
            **self._auth_headers(self.admin_user),
        )
        self.assertTrue(TrainingAssistant.objects.filter(user=self.target_user).exists())

        # 일반 유저로 변경
        response = self.client.patch(
            self._get_url(self.target_user.id),
            data={"role": "USER"},
            content_type="application/json",
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(TrainingAssistant.objects.filter(user=self.target_user).exists())

    def test_non_admin_cannot_change_role(self) -> None:
        """관리자가 아닌 유저는 권한을 변경할 수 없다."""
        response = self.client.patch(
            self._get_url(self.target_user.id),
            data={"role": "ADMIN"},
            content_type="application/json",
            **self._auth_headers(self.ta_user),
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["detail"], "권한이 없습니다.")

    def test_returns_401_when_unauthenticated(self) -> None:
        """인증되지 않은 사용자는 401을 받는다."""
        response = self.client.patch(
            self._get_url(self.target_user.id),
            data={"role": "ADMIN"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_returns_404_when_user_not_found(self) -> None:
        """존재하지 않는 회원의 권한 변경 시 404를 받는다."""
        response = self.client.patch(
            self._get_url(99999),
            data={"role": "ADMIN"},
            content_type="application/json",
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["error_detail"], "사용자 정보를 찾을 수 없습니다.")

    def test_invalid_role_returns_400(self) -> None:
        """유효하지 않은 권한으로 변경 시 400을 받는다."""
        response = self.client.patch(
            self._get_url(self.target_user.id),
            data={"role": "INVALID_ROLE"},
            content_type="application/json",
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("role", response.json()["error_detail"])
