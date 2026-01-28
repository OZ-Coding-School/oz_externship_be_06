from datetime import date, timedelta

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from apps.courses.models import Cohort, CohortStudent, Course
from apps.courses.models.learning_coachs import LearningCoach
from apps.courses.models.operation_managers import OperationManager
from apps.courses.models.training_assistants import TrainingAssistant
from apps.users.models import User


class AdminAccountDetailAPITest(TestCase):
    """어드민 회원 정보 상세 조회 API 테스트."""

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
        self.cohort2 = Cohort.objects.create(
            course=self.course,
            number=2,
            max_student=30,
            start_date=date.today() + timedelta(days=200),
            end_date=date.today() + timedelta(days=380),
            status=Cohort.StatusChoices.PREPARING,
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
        )

        # 조교 유저
        self.ta_user = User.objects.create_user(
            email="ta@example.com",
            password="password123",
            name="조교",
            nickname="조교",
            phone_number="01022222222",
            gender=User.Gender.FEMALE,
            birthday=date(1995, 5, 5),
            role=User.Role.TA,
        )
        # 조교 담당 기수 연결
        TrainingAssistant.objects.create(user=self.ta_user, cohort=self.cohort)
        TrainingAssistant.objects.create(user=self.ta_user, cohort=self.cohort2)

        # 러닝코치 유저
        self.lc_user = User.objects.create_user(
            email="lc@example.com",
            password="password123",
            name="러닝코치",
            nickname="러닝코치",
            phone_number="01033333333",
            gender=User.Gender.MALE,
            birthday=date(1992, 3, 3),
            role=User.Role.LC,
        )
        # 러닝코치 담당 과정 연결
        LearningCoach.objects.create(user=self.lc_user, course=self.course)

        # 운영매니저 유저
        self.om_user = User.objects.create_user(
            email="om@example.com",
            password="password123",
            name="운영매니저",
            nickname="운영매니저",
            phone_number="01044444444",
            gender=User.Gender.FEMALE,
            birthday=date(1993, 4, 4),
            role=User.Role.OM,
        )
        # 운영매니저 담당 과정 연결
        OperationManager.objects.create(user=self.om_user, course=self.course)
        OperationManager.objects.create(user=self.om_user, course=self.course2)

        # 수강생 유저
        self.student_user = User.objects.create_user(
            email="student@example.com",
            password="password123",
            name="수강생",
            nickname="수강생",
            phone_number="01055555555",
            gender=User.Gender.MALE,
            birthday=date(2000, 1, 1),
            role=User.Role.STUDENT,
        )
        # 수강생 기수 연결
        CohortStudent.objects.create(user=self.student_user, cohort=self.cohort)

        # 일반 유저
        self.normal_user = User.objects.create_user(
            email="user@example.com",
            password="password123",
            name="일반유저",
            nickname="일반유저",
            phone_number="01066666666",
            gender=User.Gender.MALE,
            birthday=date(2000, 2, 2),
            role=User.Role.USER,
        )

    def _get_url(self, account_id: int) -> str:
        return f"/api/v1/admin/accounts/{account_id}/"

    def _auth_headers(self, user: User) -> dict[str, str]:
        token = AccessToken.for_user(user)
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    def test_admin_can_view_user_detail(self) -> None:
        """관리자가 회원 상세 정보를 조회할 수 있다."""
        response = self.client.get(
            self._get_url(self.normal_user.id),
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["id"], self.normal_user.id)
        self.assertEqual(data["email"], self.normal_user.email)
        self.assertEqual(data["name"], self.normal_user.name)
        self.assertEqual(data["nickname"], self.normal_user.nickname)
        self.assertEqual(data["role"], "USER")
        self.assertEqual(data["status"], "ACTIVATED")
        self.assertEqual(data["assigned_courses"], [])

    def test_ta_can_view_user_detail(self) -> None:
        """조교가 회원 상세 정보를 조회할 수 있다."""
        response = self.client.get(
            self._get_url(self.normal_user.id),
            **self._auth_headers(self.ta_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_view_ta_user_returns_assigned_cohorts(self) -> None:
        """조교 회원 조회 시 담당 기수 목록이 반환된다."""
        response = self.client.get(
            self._get_url(self.ta_user.id),
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data["assigned_courses"]), 2)

        # 첫 번째 담당 기수 확인
        assigned = data["assigned_courses"][0]
        self.assertIn("course", assigned)
        self.assertIn("cohort", assigned)
        self.assertEqual(assigned["course"]["name"], "백엔드 부트캠프")
        self.assertIn("number", assigned["cohort"])
        self.assertIn("status", assigned["cohort"])

    def test_view_lc_user_returns_assigned_courses(self) -> None:
        """러닝코치 회원 조회 시 담당 과정 목록이 반환된다."""
        response = self.client.get(
            self._get_url(self.lc_user.id),
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data["assigned_courses"]), 1)

        assigned = data["assigned_courses"][0]
        self.assertIn("course", assigned)
        self.assertNotIn("cohort", assigned)
        self.assertEqual(assigned["course"]["name"], "백엔드 부트캠프")

    def test_view_om_user_returns_assigned_courses(self) -> None:
        """운영매니저 회원 조회 시 담당 과정 목록이 반환된다."""
        response = self.client.get(
            self._get_url(self.om_user.id),
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data["assigned_courses"]), 2)

        # 과정만 있고 기수는 없음
        for assigned in data["assigned_courses"]:
            self.assertIn("course", assigned)
            self.assertNotIn("cohort", assigned)

    def test_view_student_user_returns_enrolled_cohorts(self) -> None:
        """수강생 회원 조회 시 수강 기수 목록이 반환된다."""
        response = self.client.get(
            self._get_url(self.student_user.id),
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data["assigned_courses"]), 1)

        assigned = data["assigned_courses"][0]
        self.assertIn("course", assigned)
        self.assertIn("cohort", assigned)
        self.assertEqual(assigned["course"]["name"], "백엔드 부트캠프")
        self.assertEqual(assigned["cohort"]["number"], 1)

    def test_returns_401_when_unauthenticated(self) -> None:
        """인증되지 않은 사용자는 401을 받는다."""
        response = self.client.get(self._get_url(self.normal_user.id))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_returns_403_for_normal_user(self) -> None:
        """일반 유저는 403을 받는다."""
        response = self.client.get(
            self._get_url(self.ta_user.id),
            **self._auth_headers(self.normal_user),
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        data = response.json()
        self.assertEqual(data["detail"], "권한이 없습니다.")

    def test_returns_404_when_user_not_found(self) -> None:
        """존재하지 않는 회원 조회 시 404를 받는다."""
        response = self.client.get(
            self._get_url(99999),
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.json()
        self.assertEqual(data["error_detail"], "사용자 정보를 찾을 수 없습니다.")

    def test_deactivated_user_status(self) -> None:
        """비활성화된 유저의 status가 DEACTIVATED로 반환된다."""
        self.normal_user.is_active = False
        self.normal_user.save()

        response = self.client.get(
            self._get_url(self.normal_user.id),
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["status"], "DEACTIVATED")
