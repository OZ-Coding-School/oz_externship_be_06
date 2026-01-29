from __future__ import annotations

import json
from datetime import date, timedelta
from typing import Any

from django.test import TestCase
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken

from apps.courses.models.cohorts import Cohort
from apps.courses.models.courses import Course
from apps.courses.models.subjects import Subject
from apps.exams.constants import ErrorMessages
from apps.exams.models import Exam, ExamDeployment, ExamSubmission
from apps.users.models import User


class AdminExamSubmissionListAPITest(TestCase):
    """어드민 쪽지시험 응시 내역 목록 조회 API 테스트."""

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
            open_at=timezone.now() - timedelta(minutes=5),
            close_at=timezone.now() + timedelta(minutes=30),
            questions_snapshot_json={},
            status=ExamDeployment.StatusChoices.ACTIVATED,
        )
        self.admin_user = User.objects.create_user(
            email="admin@example.com",
            password="password123",
            name="관리자",
            nickname="관리자",
            phone_number="01011112222",
            gender=User.Gender.MALE,
            birthday=date(1990, 1, 1),
            role=User.Role.ADMIN,
            is_active=True,
        )
        self.staff_user = User.objects.create_user(
            email="staff@example.com",
            password="password123",
            name="스태프",
            nickname="스태프",
            phone_number="01011112223",
            gender=User.Gender.MALE,
            birthday=date(1990, 1, 1),
            role=User.Role.TA,
            is_active=True,
        )
        self.student = User.objects.create_user(
            email="student@example.com",
            password="password123",
            name="학생",
            nickname="학생",
            phone_number="01012345678",
            gender=User.Gender.MALE,
            birthday=date(2000, 1, 1),
            role=User.Role.STUDENT,
            is_active=True,
        )
        self.submission = ExamSubmission.objects.create(
            submitter=self.student,
            deployment=self.deployment,
            started_at=timezone.now() - timedelta(minutes=20),
            cheating_count=0,
            answers_json=json.dumps([]),
            score=80,
            correct_answer_count=8,
        )

    def _auth_headers(self, user: User) -> Any:
        token = AccessToken.for_user(user)
        return {"Authorization": f"Bearer {token}"}

    def test_admin_can_list_submissions(self) -> None:
        response = self.client.get(
            "/api/v1/admin/submissions/",
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("results", data)
        self.assertIn("count", data)
        self.assertGreaterEqual(len(data["results"]), 1)

    def test_staff_can_list_submissions(self) -> None:
        response = self.client.get(
            "/api/v1/admin/submissions/",
            headers=self._auth_headers(self.staff_user),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("results", data)

    def test_returns_401_when_unauthenticated(self) -> None:
        response = self.client.get("/api/v1/admin/submissions/")

        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertEqual(data["detail"], ErrorMessages.UNAUTHORIZED.value)

    def test_returns_403_for_non_staff(self) -> None:
        response = self.client.get(
            "/api/v1/admin/submissions/",
            headers=self._auth_headers(self.student),
        )

        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertEqual(data["detail"], ErrorMessages.NO_SUBMISSION_LIST_PERMISSION.value)

    def test_returns_404_when_no_submissions(self) -> None:
        ExamSubmission.objects.all().delete()

        response = self.client.get(
            "/api/v1/admin/submissions/",
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data["error_detail"], ErrorMessages.SUBMISSION_LIST_NOT_FOUND.value)

    def test_filter_by_search_keyword_nickname(self) -> None:
        response = self.client.get(
            "/api/v1/admin/submissions/",
            {"search_keyword": "학생"},
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(len(data["results"]), 1)
        self.assertEqual(data["results"][0]["nickname"], "학생")

    def test_filter_by_search_keyword_name(self) -> None:
        response = self.client.get(
            "/api/v1/admin/submissions/",
            {"search_keyword": "학생"},
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(len(data["results"]), 1)

    def test_filter_by_cohort_id(self) -> None:
        response = self.client.get(
            "/api/v1/admin/submissions/",
            {"cohort_id": self.cohort.id},
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(len(data["results"]), 1)

    def test_filter_by_exam_id(self) -> None:
        response = self.client.get(
            "/api/v1/admin/submissions/",
            {"exam_id": self.exam.id},
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(len(data["results"]), 1)

    def test_filter_by_invalid_cohort_id(self) -> None:
        response = self.client.get(
            "/api/v1/admin/submissions/",
            {"cohort_id": "invalid"},
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["error_detail"], ErrorMessages.INVALID_SUBMISSION_LIST_REQUEST.value)

    def test_filter_by_invalid_exam_id(self) -> None:
        response = self.client.get(
            "/api/v1/admin/submissions/",
            {"exam_id": "invalid"},
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["error_detail"], ErrorMessages.INVALID_SUBMISSION_LIST_REQUEST.value)

    def test_sort_by_score_desc(self) -> None:
        ExamSubmission.objects.create(
            submitter=self.student,
            deployment=self.deployment,
            started_at=timezone.now() - timedelta(minutes=10),
            cheating_count=0,
            answers_json=json.dumps([]),
            score=90,
            correct_answer_count=9,
        )

        response = self.client.get(
            "/api/v1/admin/submissions/",
            {"sort": "score", "order": "desc"},
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(len(data["results"]), 2)
        self.assertGreaterEqual(data["results"][0]["score"], data["results"][1]["score"])

    def test_sort_by_score_asc(self) -> None:
        ExamSubmission.objects.create(
            submitter=self.student,
            deployment=self.deployment,
            started_at=timezone.now() - timedelta(minutes=10),
            cheating_count=0,
            answers_json=json.dumps([]),
            score=70,
            correct_answer_count=7,
        )

        response = self.client.get(
            "/api/v1/admin/submissions/",
            {"sort": "score", "order": "asc"},
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(len(data["results"]), 2)
        self.assertLessEqual(data["results"][0]["score"], data["results"][1]["score"])

    def test_sort_by_started_at_desc(self) -> None:
        ExamSubmission.objects.create(
            submitter=self.student,
            deployment=self.deployment,
            started_at=timezone.now() - timedelta(minutes=5),
            cheating_count=0,
            answers_json=json.dumps([]),
            score=75,
            correct_answer_count=7,
        )

        response = self.client.get(
            "/api/v1/admin/submissions/",
            {"sort": "started_at", "order": "desc"},
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(len(data["results"]), 2)

    def test_pagination(self) -> None:
        for i in range(15):
            ExamSubmission.objects.create(
                submitter=self.student,
                deployment=self.deployment,
                started_at=timezone.now() - timedelta(minutes=30 - i),
                cheating_count=0,
                answers_json=json.dumps([]),
                score=80 + i,
                correct_answer_count=8,
            )

        response = self.client.get(
            "/api/v1/admin/submissions/",
            {"page": 1, "size": 10},
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertLessEqual(len(data["results"]), 10)
        self.assertIn("count", data)
        self.assertIn("next", data)

    def test_pagination_with_custom_size(self) -> None:
        for i in range(5):
            ExamSubmission.objects.create(
                submitter=self.student,
                deployment=self.deployment,
                started_at=timezone.now() - timedelta(minutes=30 - i),
                cheating_count=0,
                answers_json=json.dumps([]),
                score=80 + i,
                correct_answer_count=8,
            )

        response = self.client.get(
            "/api/v1/admin/submissions/",
            {"page": 1, "size": 3},
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertLessEqual(len(data["results"]), 3)

    def test_invalid_sort_field_defaults_to_started_at(self) -> None:
        response = self.client.get(
            "/api/v1/admin/submissions/",
            {"sort": "invalid_field"},
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("results", data)
