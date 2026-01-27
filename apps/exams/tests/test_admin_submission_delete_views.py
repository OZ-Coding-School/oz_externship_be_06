from __future__ import annotations

from datetime import date, timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken

from apps.courses.models.cohorts import Cohort
from apps.courses.models.courses import Course
from apps.courses.models.subjects import Subject
from apps.exams.models import Exam, ExamDeployment, ExamSubmission
from apps.users.models import User


class AdminExamSubmissionDeleteAPITest(TestCase):
    """어드민 쪽지시험 응시내역 삭제 API 테스트."""

    def setUp(self) -> None:
        self.course = Course.objects.create(
            name="코스",
            tag="CS",
            description="설명",
            thumbnail_img_url="course.png",
        )
        self.subject = Subject.objects.create(
            course=self.course,
            title="과목",
            number_of_days=1,
            number_of_hours=1,
            thumbnail_img_url="subject.png",
        )
        self.cohort = Cohort.objects.create(
            course=self.course,
            number=1,
            max_student=10,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
        )
        self.exam = Exam.objects.create(
            subject=self.subject,
            title="시험",
            thumbnail_img_url="exam.png",
        )
        self.deployment = ExamDeployment.objects.create(
            cohort=self.cohort,
            exam=self.exam,
            duration_time=30,
            access_code="CODE",
            open_at=timezone.now(),
            close_at=timezone.now() + timedelta(days=1),
            questions_snapshot_json={},
            status=ExamDeployment.StatusChoices.ACTIVATED,
        )
        self.student = User.objects.create_user(
            email="student@example.com",
            password="password123",
            name="학생",
            nickname="학생",
            phone_number="01011112222",
            gender=User.Gender.MALE,
            birthday=date(2000, 1, 1),
            role=User.Role.STUDENT,
        )
        self.submission = ExamSubmission.objects.create(
            submitter=self.student,
            deployment=self.deployment,
            started_at=timezone.now(),
            cheating_count=0,
            answers_json={},
            score=0,
            correct_answer_count=0,
        )
        self.admin_user = User.objects.create_user(
            email="admin@example.com",
            password="password123",
            name="관리자",
            nickname="관리자",
            phone_number="01011113333",
            gender=User.Gender.MALE,
            birthday=date(2000, 1, 1),
            role=User.Role.ADMIN,
        )
        self.ta_user = User.objects.create_user(
            email="ta@example.com",
            password="password123",
            name="조교",
            nickname="조교",
            phone_number="01011114444",
            gender=User.Gender.FEMALE,
            birthday=date(2000, 1, 2),
            role=User.Role.TA,
        )
        self.normal_user = User.objects.create_user(
            email="user@example.com",
            password="password123",
            name="사용자",
            nickname="사용자",
            phone_number="01011115555",
            gender=User.Gender.FEMALE,
            birthday=date(2000, 1, 2),
            role=User.Role.USER,
        )

    def _auth_headers(self, user: User) -> dict[str, str]:
        token = AccessToken.for_user(user)
        return {"Authorization": f"Bearer {token}"}

    def test_admin_can_delete_submission(self) -> None:
        """관리자가 응시내역을 삭제할 수 있다."""
        response = self.client.delete(
            f"/api/v1/admin/exams/submissions/{self.submission.id}/",
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["submission_id"], self.submission.id)
        self.assertFalse(ExamSubmission.objects.filter(id=self.submission.id).exists())

    def test_ta_can_delete_submission(self) -> None:
        """조교가 응시내역을 삭제할 수 있다."""
        response = self.client.delete(
            f"/api/v1/admin/exams/submissions/{self.submission.id}/",
            headers=self._auth_headers(self.ta_user),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["submission_id"], self.submission.id)
        self.assertFalse(ExamSubmission.objects.filter(id=self.submission.id).exists())

    def test_returns_401_when_unauthenticated(self) -> None:
        """인증되지 않은 사용자는 401을 받는다."""
        response = self.client.delete(f"/api/v1/admin/exams/submissions/{self.submission.id}/")

        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertEqual(data["detail"], "자격 인증데이터(authentication credentials)가 제공되지 않았습니다.")

    def test_returns_403_for_non_staff(self) -> None:
        """스태프가 아닌 사용자는 403을 받는다."""
        response = self.client.delete(
            f"/api/v1/admin/exams/submissions/{self.submission.id}/",
            headers=self._auth_headers(self.normal_user),
        )

        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertEqual(data["detail"], "쪽지시험 응시 내역 삭제 권한이 없습니다.")

    def test_returns_400_for_invalid_submission_id(self) -> None:
        """유효하지 않은 submission_id는 400을 받는다."""
        response = self.client.delete(
            "/api/v1/admin/exams/submissions/0/",
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["error_detail"], "유효하지 않은 응시 내역 삭제 요청입니다.")

    def test_returns_404_when_submission_missing(self) -> None:
        """존재하지 않는 응시내역은 404를 받는다."""
        response = self.client.delete(
            "/api/v1/admin/exams/submissions/9999/",
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data["error_detail"], "삭제할 응시 내역을 찾을 수 없습니다.")

    def test_returns_409_when_conflict_occurs(self) -> None:
        """충돌 발생 시 409를 받는다."""
        from apps.exams.services.admin_submission_delete_service import (
            ExamSubmissionDeleteConflictError,
        )

        with patch(
            "apps.exams.views.admin_submission_delete_views.delete_exam_submission"
        ) as mock_delete:
            mock_delete.side_effect = ExamSubmissionDeleteConflictError()

            response = self.client.delete(
                f"/api/v1/admin/exams/submissions/{self.submission.id}/",
                headers=self._auth_headers(self.admin_user),
            )

            self.assertEqual(response.status_code, 409)
            data = response.json()
            self.assertEqual(data["error_detail"], "응시 내역 처리 중 충돌이 발생했습니다.")
