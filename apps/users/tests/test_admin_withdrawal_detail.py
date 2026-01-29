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
from apps.users.models import User, Withdrawal


class AdminWithdrawalDetailAPITest(TestCase):
    """어드민 탈퇴 내역 상세 조회 API 테스트."""

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

        # 탈퇴한 학생 유저
        self.withdrawn_student = User.objects.create_user(
            email="student@example.com",
            password="password123",
            name="김학생",
            nickname="학생",
            phone_number="01033333333",
            gender=User.Gender.MALE,
            birthday=date(2000, 1, 1),
            role=User.Role.STUDENT,
            is_active=False,
        )
        CohortStudent.objects.create(user=self.withdrawn_student, cohort=self.cohort)

        # 탈퇴한 조교 유저
        self.withdrawn_ta = User.objects.create_user(
            email="withdrawn_ta@example.com",
            password="password123",
            name="이조교",
            nickname="조교2",
            phone_number="01044444444",
            gender=User.Gender.FEMALE,
            birthday=date(1995, 5, 5),
            role=User.Role.TA,
            is_active=False,
        )
        TrainingAssistant.objects.create(user=self.withdrawn_ta, cohort=self.cohort)

        # 탈퇴한 운영매니저 유저
        self.withdrawn_om = User.objects.create_user(
            email="withdrawn_om@example.com",
            password="password123",
            name="박운매",
            nickname="운매",
            phone_number="01055555555",
            gender=User.Gender.MALE,
            birthday=date(1990, 3, 3),
            role=User.Role.OM,
            is_active=False,
        )
        OperationManager.objects.create(user=self.withdrawn_om, course=self.course)

        # 탈퇴한 러닝코치 유저
        self.withdrawn_lc = User.objects.create_user(
            email="withdrawn_lc@example.com",
            password="password123",
            name="최러닝",
            nickname="러닝",
            phone_number="01066666666",
            gender=User.Gender.FEMALE,
            birthday=date(1992, 7, 7),
            role=User.Role.LC,
            is_active=False,
        )
        LearningCoach.objects.create(user=self.withdrawn_lc, course=self.course)

        # 탈퇴 내역 생성
        self.withdrawal_student = Withdrawal.objects.create(
            user=self.withdrawn_student,
            reason=Withdrawal.Reason.GRADUATION,
            reason_detail="수료 완료했습니다.",
        )
        self.withdrawal_ta = Withdrawal.objects.create(
            user=self.withdrawn_ta,
            reason=Withdrawal.Reason.TRANSFER,
            reason_detail="다른 회사로 이직합니다.",
        )
        self.withdrawal_om = Withdrawal.objects.create(
            user=self.withdrawn_om,
            reason=Withdrawal.Reason.NO_LONGER_NEEDED,
            reason_detail="더 이상 필요 없음",
        )
        self.withdrawal_lc = Withdrawal.objects.create(
            user=self.withdrawn_lc,
            reason=Withdrawal.Reason.OTHER,
            reason_detail="개인 사정",
        )

        # 일반 유저 (권한 없음)
        self.normal_user = User.objects.create_user(
            email="normal@example.com",
            password="password123",
            name="일반유저",
            nickname="일반유저",
            phone_number="01077777777",
            gender=User.Gender.MALE,
            birthday=date(2000, 5, 5),
            role=User.Role.USER,
        )

    def _get_url(self, withdrawal_id: int) -> str:
        return f"/api/v1/admin/withdrawals/{withdrawal_id}/"

    def _auth_headers(self, user: User) -> Any:
        token = AccessToken.for_user(user)
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    def test_admin_can_get_withdrawal_detail(self) -> None:
        """관리자가 탈퇴 내역 상세를 조회할 수 있다."""
        response = self.client.get(
            self._get_url(self.withdrawal_student.id),
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["id"], self.withdrawal_student.id)

    def test_ta_can_get_withdrawal_detail(self) -> None:
        """조교가 탈퇴 내역 상세를 조회할 수 있다."""
        response = self.client.get(
            self._get_url(self.withdrawal_student.id),
            **self._auth_headers(self.ta_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_response_format(self) -> None:
        """응답 형식이 명세서와 일치한다."""
        response = self.client.get(
            self._get_url(self.withdrawal_student.id),
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # 필수 필드 확인
        self.assertIn("id", data)
        self.assertIn("user", data)
        self.assertIn("assigned_courses", data)
        self.assertIn("reason", data)
        self.assertIn("reason_display", data)
        self.assertIn("reason_detail", data)
        self.assertIn("due_date", data)
        self.assertIn("withdrawn_at", data)

        # 유저 정보 필드 확인
        user_info = data["user"]
        self.assertIn("id", user_info)
        self.assertIn("email", user_info)
        self.assertIn("nickname", user_info)
        self.assertIn("name", user_info)
        self.assertIn("gender", user_info)
        self.assertIn("role", user_info)
        self.assertIn("status", user_info)
        self.assertIn("profile_img_url", user_info)
        self.assertIn("created_at", user_info)

    def test_student_has_cohort_in_assigned_courses(self) -> None:
        """수강생의 경우 수강 과정-기수 정보가 포함된다."""
        response = self.client.get(
            self._get_url(self.withdrawal_student.id),
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertEqual(len(data["assigned_courses"]), 1)
        course_info = data["assigned_courses"][0]

        # 과정 정보 확인
        self.assertIn("course", course_info)
        self.assertEqual(course_info["course"]["name"], "백엔드 부트캠프")

        # 기수 정보 확인
        self.assertIn("cohort", course_info)
        self.assertIsNotNone(course_info["cohort"])
        self.assertEqual(course_info["cohort"]["number"], 1)

    def test_ta_has_cohort_in_assigned_courses(self) -> None:
        """조교의 경우 담당 과정-기수 정보가 포함된다."""
        response = self.client.get(
            self._get_url(self.withdrawal_ta.id),
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertEqual(len(data["assigned_courses"]), 1)
        course_info = data["assigned_courses"][0]

        self.assertIsNotNone(course_info["cohort"])
        self.assertEqual(course_info["cohort"]["number"], 1)

    def test_om_has_course_without_cohort(self) -> None:
        """운영매니저의 경우 담당 과정 목록만 포함된다 (기수 없음)."""
        response = self.client.get(
            self._get_url(self.withdrawal_om.id),
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertEqual(len(data["assigned_courses"]), 1)
        course_info = data["assigned_courses"][0]

        self.assertEqual(course_info["course"]["name"], "백엔드 부트캠프")
        self.assertIsNone(course_info["cohort"])

    def test_lc_has_course_without_cohort(self) -> None:
        """러닝코치의 경우 담당 과정 목록만 포함된다 (기수 없음)."""
        response = self.client.get(
            self._get_url(self.withdrawal_lc.id),
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertEqual(len(data["assigned_courses"]), 1)
        course_info = data["assigned_courses"][0]

        self.assertEqual(course_info["course"]["name"], "백엔드 부트캠프")
        self.assertIsNone(course_info["cohort"])

    def test_user_status_is_withdrew(self) -> None:
        """탈퇴한 유저의 상태는 WITHDREW이다."""
        response = self.client.get(
            self._get_url(self.withdrawal_student.id),
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertEqual(data["user"]["status"], "WITHDREW")

    def test_reason_display_is_korean(self) -> None:
        """탈퇴 사유가 한글로 표시된다."""
        response = self.client.get(
            self._get_url(self.withdrawal_student.id),
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertEqual(data["reason"], "GRADUATION")
        self.assertEqual(data["reason_display"], "졸업 및 수료")

    def test_returns_404_when_not_found(self) -> None:
        """존재하지 않는 탈퇴 내역 조회 시 404를 받는다."""
        response = self.client.get(
            self._get_url(99999),
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["error_detail"], "회원탈퇴 정보를 찾을 수 없습니다.")

    def test_returns_401_when_unauthenticated(self) -> None:
        """인증되지 않은 사용자는 401을 받는다."""
        response = self.client.get(self._get_url(self.withdrawal_student.id))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_returns_403_for_normal_user(self) -> None:
        """일반 유저는 403을 받는다."""
        response = self.client.get(
            self._get_url(self.withdrawal_student.id),
            **self._auth_headers(self.normal_user),
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # 탈퇴 취소 API 테스트
    def test_admin_can_cancel_withdrawal(self) -> None:
        """관리자가 탈퇴를 취소할 수 있다."""
        response = self.client.delete(
            self._get_url(self.withdrawal_student.id),
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["detail"], "회원 탈퇴 취소처리 완료.")

        # 탈퇴 내역이 삭제되었는지 확인
        self.assertFalse(Withdrawal.objects.filter(id=self.withdrawal_student.id).exists())

        # 유저가 활성화되었는지 확인
        self.withdrawn_student.refresh_from_db()
        self.assertTrue(self.withdrawn_student.is_active)

    def test_ta_can_cancel_withdrawal(self) -> None:
        """조교가 탈퇴를 취소할 수 있다."""
        response = self.client.delete(
            self._get_url(self.withdrawal_ta.id),
            **self._auth_headers(self.ta_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cancel_withdrawal_returns_404_when_not_found(self) -> None:
        """존재하지 않는 탈퇴 내역 취소 시 404를 받는다."""
        response = self.client.delete(
            self._get_url(99999),
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["error_detail"], "회원탈퇴 정보를 찾을 수 없습니다.")

    def test_cancel_withdrawal_returns_401_when_unauthenticated(self) -> None:
        """인증되지 않은 사용자는 탈퇴 취소 시 401을 받는다."""
        response = self.client.delete(self._get_url(self.withdrawal_student.id))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cancel_withdrawal_returns_403_for_normal_user(self) -> None:
        """일반 유저는 탈퇴 취소 시 403을 받는다."""
        response = self.client.delete(
            self._get_url(self.withdrawal_student.id),
            **self._auth_headers(self.normal_user),
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
