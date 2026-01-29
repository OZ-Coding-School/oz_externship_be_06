from datetime import date, timedelta
from typing import Any

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from apps.courses.models import Cohort, Course
from apps.users.models import User
from apps.users.models.enrollment import StudentEnrollmentRequest


class AdminStudentEnrollmentRejectAPITest(TestCase):
    """어드민 수강생 등록 요청 거절 API 테스트."""

    def setUp(self) -> None:
        self.client = APIClient()

        # 과정 생성
        self.course = Course.objects.create(
            name="백엔드 부트캠프",
            tag="BE",
            description="백엔드 과정",
            thumbnail_img_url="https://example.com/be.png",
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
        is_active=True,
        )

        # 일반 유저들 (등록 요청자)
        self.user1 = User.objects.create_user(
            email="user1@example.com",
            password="password123",
            name="김신청",
            nickname="신청자1",
            phone_number="01033333333",
            gender=User.Gender.MALE,
            birthday=date(2000, 1, 1),
            role=User.Role.USER,
        is_active=True,
        )
        self.user2 = User.objects.create_user(
            email="user2@example.com",
            password="password123",
            name="이신청",
            nickname="신청자2",
            phone_number="01044444444",
            gender=User.Gender.FEMALE,
            birthday=date(2001, 2, 2),
            role=User.Role.USER,
        is_active=True,
        )

        # 등록 요청 생성
        self.enrollment1 = StudentEnrollmentRequest.objects.create(
            user=self.user1,
            cohort=self.cohort,
            status=StudentEnrollmentRequest.Status.PENDING,
        )
        self.enrollment2 = StudentEnrollmentRequest.objects.create(
            user=self.user2,
            cohort=self.cohort,
            status=StudentEnrollmentRequest.Status.PENDING,
        )

        # 일반 유저 (권한 없음)
        self.normal_user = User.objects.create_user(
            email="normal@example.com",
            password="password123",
            name="일반유저",
            nickname="일반유저",
            phone_number="01055555555",
            gender=User.Gender.MALE,
            birthday=date(2000, 5, 5),
            role=User.Role.USER,
        is_active=True,
        )

    def _get_url(self) -> str:
        return "/api/v1/admin/student-enrollments/reject"

    def _auth_headers(self, user: User) -> Any:
        token = AccessToken.for_user(user)
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    def test_admin_can_reject_enrollments(self) -> None:
        """관리자가 수강생 등록 요청을 거절할 수 있다."""
        response = self.client.post(
            self._get_url(),
            data={"enrollments": [self.enrollment1.id]},
            content_type="application/json",
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json()["detail"],
            "수강생 등록 신청들에 대한 거절 요청이 처리되었습니다.",
        )

        # 등록 요청 상태 확인
        self.enrollment1.refresh_from_db()
        self.assertEqual(self.enrollment1.status, StudentEnrollmentRequest.Status.REJECTED)

        # 유저 role은 변경되지 않음
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.role, User.Role.USER)

    def test_ta_can_reject_enrollments(self) -> None:
        """조교가 수강생 등록 요청을 거절할 수 있다."""
        response = self.client.post(
            self._get_url(),
            data={"enrollments": [self.enrollment1.id]},
            content_type="application/json",
            **self._auth_headers(self.ta_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_can_reject_multiple_enrollments(self) -> None:
        """여러 등록 요청을 일괄 거절할 수 있다."""
        response = self.client.post(
            self._get_url(),
            data={"enrollments": [self.enrollment1.id, self.enrollment2.id]},
            content_type="application/json",
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 두 등록 요청 모두 거절됨
        self.enrollment1.refresh_from_db()
        self.enrollment2.refresh_from_db()
        self.assertEqual(self.enrollment1.status, StudentEnrollmentRequest.Status.REJECTED)
        self.assertEqual(self.enrollment2.status, StudentEnrollmentRequest.Status.REJECTED)

    def test_already_rejected_enrollment_is_ignored(self) -> None:
        """이미 거절된 등록 요청은 무시된다."""
        self.enrollment1.status = StudentEnrollmentRequest.Status.REJECTED
        self.enrollment1.save()

        response = self.client.post(
            self._get_url(),
            data={"enrollments": [self.enrollment1.id]},
            content_type="application/json",
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_already_approved_enrollment_is_ignored(self) -> None:
        """이미 승인된 등록 요청은 거절되지 않는다."""
        self.enrollment1.status = StudentEnrollmentRequest.Status.APPROVED
        self.enrollment1.save()

        response = self.client.post(
            self._get_url(),
            data={"enrollments": [self.enrollment1.id]},
            content_type="application/json",
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 상태는 여전히 APPROVED
        self.enrollment1.refresh_from_db()
        self.assertEqual(self.enrollment1.status, StudentEnrollmentRequest.Status.APPROVED)

    def test_returns_400_when_enrollments_is_empty(self) -> None:
        """enrollments가 빈 배열이면 400을 받는다."""
        response = self.client.post(
            self._get_url(),
            data={"enrollments": []},
            content_type="application/json",
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("enrollments", response.json()["error_detail"])

    def test_returns_400_when_enrollments_is_missing(self) -> None:
        """enrollments가 없으면 400을 받는다."""
        response = self.client.post(
            self._get_url(),
            data={},
            content_type="application/json",
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("enrollments", response.json()["error_detail"])

    def test_returns_401_when_unauthenticated(self) -> None:
        """인증되지 않은 사용자는 401을 받는다."""
        response = self.client.post(
            self._get_url(),
            data={"enrollments": [self.enrollment1.id]},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_returns_403_for_normal_user(self) -> None:
        """일반 유저는 403을 받는다."""
        response = self.client.post(
            self._get_url(),
            data={"enrollments": [self.enrollment1.id]},
            content_type="application/json",
            **self._auth_headers(self.normal_user),
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
