from datetime import date, timedelta
from typing import Any

from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken

from apps.courses.models import Cohort, CohortStudent, Course
from apps.courses.models.subjects import Subject
from apps.exams.models import Exam, ExamDeployment
from apps.exams.models.exam_submissions import ExamSubmission
from apps.users.models import User


class AdminStudentScoreAPITest(TestCase):
    """학생별 과목 점수 조회 API 테스트."""

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

        # 과목 생성
        self.subject1 = Subject.objects.create(
            course=self.course,
            title="HTML/CSS",
            number_of_days=5,
            number_of_hours=40,
        )
        self.subject2 = Subject.objects.create(
            course=self.course,
            title="JavaScript",
            number_of_days=10,
            number_of_hours=80,
        )

        # 시험 생성
        self.exam1 = Exam.objects.create(
            subject=self.subject1,
            title="HTML/CSS 기초 시험",
        )
        self.exam2 = Exam.objects.create(
            subject=self.subject2,
            title="JavaScript 기초 시험",
        )

        # 시험 배포 생성
        self.deployment1 = ExamDeployment.objects.create(
            cohort=self.cohort,
            exam=self.exam1,
            duration_time=60,
            access_code="test123",
            open_at=timezone.now(),
            close_at=timezone.now() + timedelta(hours=2),
            questions_snapshot_json=[],
            status=ExamDeployment.StatusChoices.ACTIVATED,
        )
        self.deployment2 = ExamDeployment.objects.create(
            cohort=self.cohort,
            exam=self.exam2,
            duration_time=60,
            access_code="test456",
            open_at=timezone.now(),
            close_at=timezone.now() + timedelta(hours=2),
            questions_snapshot_json=[],
            status=ExamDeployment.StatusChoices.ACTIVATED,
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

        # 학생 유저
        self.student = User.objects.create_user(
            email="student@example.com",
            password="password123",
            name="김학생",
            nickname="학생",
            phone_number="01033333333",
            gender=User.Gender.MALE,
            birthday=date(2000, 1, 1),
            role=User.Role.STUDENT,
        )
        CohortStudent.objects.create(user=self.student, cohort=self.cohort)

        # 시험 제출 생성
        ExamSubmission.objects.create(
            submitter=self.student,
            deployment=self.deployment1,
            started_at=timezone.now(),
            answers_json=[],
            score=85,
            correct_answer_count=17,
        )
        ExamSubmission.objects.create(
            submitter=self.student,
            deployment=self.deployment2,
            started_at=timezone.now(),
            answers_json=[],
            score=65,
            correct_answer_count=13,
        )

        # 일반 유저 (권한 없음)
        self.normal_user = User.objects.create_user(
            email="normal@example.com",
            password="password123",
            name="일반유저",
            nickname="일반유저",
            phone_number="01044444444",
            gender=User.Gender.MALE,
            birthday=date(2000, 5, 5),
            role=User.Role.USER,
        )

    def _get_url(self, student_id: int) -> str:
        return f"/api/v1/admin/students/{student_id}/scores"

    def _auth_headers(self, user: User) -> Any:
        token = AccessToken.for_user(user)
        return {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    def test_admin_can_get_student_scores(self) -> None:
        """관리자가 학생의 과목별 점수를 조회할 수 있다."""
        response = self.client.get(
            self._get_url(self.student.id),
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), 2)

        # 과목별 점수 확인
        subjects = {item["subject"]: item["score"] for item in data}
        self.assertEqual(subjects["HTML/CSS"], 85)
        self.assertEqual(subjects["JavaScript"], 65)

    def test_ta_can_get_student_scores(self) -> None:
        """조교가 학생의 과목별 점수를 조회할 수 있다."""
        response = self.client.get(
            self._get_url(self.student.id),
            **self._auth_headers(self.ta_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_response_format(self) -> None:
        """응답 형식이 올바르다."""
        response = self.client.get(
            self._get_url(self.student.id),
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        for item in data:
            self.assertIn("subject", item)
            self.assertIn("score", item)
            self.assertIsInstance(item["subject"], str)
            self.assertIsInstance(item["score"], int)

    def test_returns_empty_list_when_no_submissions(self) -> None:
        """제출 기록이 없으면 빈 배열을 반환한다."""
        # 제출 기록 없는 새 학생 생성
        new_student = User.objects.create_user(
            email="newstudent@example.com",
            password="password123",
            name="새학생",
            nickname="새학생",
            phone_number="01055555555",
            gender=User.Gender.MALE,
            birthday=date(2001, 1, 1),
            role=User.Role.STUDENT,
        )

        response = self.client.get(
            self._get_url(new_student.id),
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), [])

    def test_returns_404_when_student_not_found(self) -> None:
        """존재하지 않는 학생 조회 시 404를 받는다."""
        response = self.client.get(
            self._get_url(99999),
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["error_detail"], "학생을 찾을 수 없습니다.")

    def test_returns_404_when_user_is_not_student(self) -> None:
        """STUDENT 권한이 아닌 유저 조회 시 404를 받는다."""
        response = self.client.get(
            self._get_url(self.admin_user.id),
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_returns_401_when_unauthenticated(self) -> None:
        """인증되지 않은 사용자는 401을 받는다."""
        response = self.client.get(self._get_url(self.student.id))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_returns_403_for_normal_user(self) -> None:
        """일반 유저는 403을 받는다."""
        response = self.client.get(
            self._get_url(self.student.id),
            **self._auth_headers(self.normal_user),
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_calculates_average_score_for_multiple_exams(self) -> None:
        """같은 과목에 여러 시험이 있으면 평균 점수를 계산한다."""
        # 같은 과목에 추가 시험 생성
        exam3 = Exam.objects.create(
            subject=self.subject1,
            title="HTML/CSS 심화 시험",
        )
        deployment3 = ExamDeployment.objects.create(
            cohort=self.cohort,
            exam=exam3,
            duration_time=60,
            access_code="test789",
            open_at=timezone.now(),
            close_at=timezone.now() + timedelta(hours=2),
            questions_snapshot_json=[],
            status=ExamDeployment.StatusChoices.ACTIVATED,
        )
        ExamSubmission.objects.create(
            submitter=self.student,
            deployment=deployment3,
            started_at=timezone.now(),
            answers_json=[],
            score=95,  # 기존 85점과 평균 90점
            correct_answer_count=19,
        )

        response = self.client.get(
            self._get_url(self.student.id),
            **self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        subjects = {item["subject"]: item["score"] for item in data}
        self.assertEqual(subjects["HTML/CSS"], 90)  # (85 + 95) / 2 = 90
