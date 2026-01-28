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
from apps.exams.models import Exam, ExamDeployment, ExamQuestion
from apps.users.models import User


class AdminExamQuestionCreateAPITest(TestCase):
    """어드민 쪽지시험 문제 등록 API 테스트."""

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
        self.student = User.objects.create_user(
            email="student@example.com",
            password="password123",
            name="학생",
            nickname="닉네임",
            phone_number="01012345678",
            gender=User.Gender.MALE,
            birthday=date(2000, 1, 1),
            role=User.Role.STUDENT,
            is_active=True,
        )

    def _auth_headers(self, user: User) -> Any:
        token = AccessToken.for_user(user)
        return {"Authorization": f"Bearer {token}"}

    def _create_question(self, point: int = 1) -> None:
        ExamQuestion.objects.create(
            exam=self.exam,
            type=ExamQuestion.TypeChoices.MULTI_SELECT,
            question="문제",
            prompt="",
            blank_count=0,
            options_json=json.dumps(["A", "B"]),
            answer=["A"],
            point=point,
            explanation="",
        )

    def test_admin_can_create_question(self) -> None:
        payload = {
            "type": "multiple_choice",
            "question": "다지선다 문제",
            "prompt": "",
            "options": ["A", "B", "C"],
            "blank_count": 0,
            "correct_answer": ["A", "C"],
            "point": 10,
            "explanation": "설명",
        }

        response = self.client.post(
            f"/api/v1/admin/exams/{self.exam.id}/questions/",
            data=json.dumps(payload),
            content_type="application/json",
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["exam_id"], self.exam.id)
        self.assertEqual(data["type"], "multiple_choice")
        self.assertEqual(data["point"], 10)

    def test_returns_401_when_unauthenticated(self) -> None:
        payload = {
            "type": "ox",
            "question": "OX 문제",
            "correct_answer": "O",
            "point": 5,
            "explanation": "",
        }

        response = self.client.post(
            f"/api/v1/admin/exams/{self.exam.id}/questions/",
            data=json.dumps(payload),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)
        data = response.json()
        self.assertEqual(data["error_detail"], ErrorMessages.UNAUTHORIZED.value)

    def test_returns_403_for_non_staff(self) -> None:
        payload = {
            "type": "ox",
            "question": "OX 문제",
            "correct_answer": "O",
            "point": 5,
            "explanation": "",
        }

        response = self.client.post(
            f"/api/v1/admin/exams/{self.exam.id}/questions/",
            data=json.dumps(payload),
            content_type="application/json",
            headers=self._auth_headers(self.student),
        )

        self.assertEqual(response.status_code, 403)
        data = response.json()
        self.assertEqual(data["error_detail"], ErrorMessages.NO_QUESTION_CREATE_PERMISSION.value)

    def test_returns_404_when_exam_missing(self) -> None:
        payload = {
            "type": "ox",
            "question": "OX 문제",
            "correct_answer": "O",
            "point": 5,
            "explanation": "",
        }

        response = self.client.post(
            "/api/v1/admin/exams/9999/questions/",
            data=json.dumps(payload),
            content_type="application/json",
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertEqual(data["error_detail"], ErrorMessages.EXAM_ADMIN_NOT_FOUND.value)

    def test_returns_409_when_question_limit_exceeded(self) -> None:
        for _ in range(20):
            self._create_question(point=1)

        payload = {
            "type": "ox",
            "question": "OX 문제",
            "correct_answer": "O",
            "point": 1,
            "explanation": "",
        }

        response = self.client.post(
            f"/api/v1/admin/exams/{self.exam.id}/questions/",
            data=json.dumps(payload),
            content_type="application/json",
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 409)
        data = response.json()
        self.assertEqual(
            data["error_detail"],
            ErrorMessages.QUESTION_CREATE_CONFLICT.value,
        )

    def test_returns_409_when_total_points_exceeded(self) -> None:
        for _ in range(10):
            self._create_question(point=10)

        payload = {
            "type": "ox",
            "question": "OX 문제",
            "correct_answer": "O",
            "point": 1,
            "explanation": "",
        }

        response = self.client.post(
            f"/api/v1/admin/exams/{self.exam.id}/questions/",
            data=json.dumps(payload),
            content_type="application/json",
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 409)
        data = response.json()
        self.assertEqual(
            data["error_detail"],
            ErrorMessages.QUESTION_CREATE_CONFLICT.value,
        )

    def test_returns_400_for_invalid_type(self) -> None:
        payload = {
            "type": "unknown",
            "question": "잘못된 타입",
            "correct_answer": "O",
            "point": 5,
        }

        response = self.client.post(
            f"/api/v1/admin/exams/{self.exam.id}/questions/",
            data=json.dumps(payload),
            content_type="application/json",
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["error_detail"], ErrorMessages.INVALID_QUESTION_CREATE_REQUEST.value)

    def test_returns_400_for_invalid_point(self) -> None:
        payload = {
            "type": "ox",
            "question": "점수 오류",
            "correct_answer": "O",
            "point": 11,
        }

        response = self.client.post(
            f"/api/v1/admin/exams/{self.exam.id}/questions/",
            data=json.dumps(payload),
            content_type="application/json",
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["error_detail"], ErrorMessages.INVALID_QUESTION_CREATE_REQUEST.value)

    def test_returns_400_for_multiple_choice_without_options(self) -> None:
        payload = {
            "type": "multiple_choice",
            "question": "보기 없음",
            "correct_answer": ["A"],
            "point": 5,
        }

        response = self.client.post(
            f"/api/v1/admin/exams/{self.exam.id}/questions/",
            data=json.dumps(payload),
            content_type="application/json",
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["error_detail"], ErrorMessages.INVALID_QUESTION_CREATE_REQUEST.value)

    def test_returns_400_for_ordering_answer_mismatch(self) -> None:
        payload = {
            "type": "ordering",
            "question": "순서 정렬",
            "options": ["A", "B", "C"],
            "correct_answer": ["A", "B"],
            "point": 5,
        }

        response = self.client.post(
            f"/api/v1/admin/exams/{self.exam.id}/questions/",
            data=json.dumps(payload),
            content_type="application/json",
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["error_detail"], ErrorMessages.INVALID_QUESTION_CREATE_REQUEST.value)

    def test_returns_400_for_fill_blank_missing_prompt(self) -> None:
        payload = {
            "type": "fill_blank",
            "question": "빈칸 문제",
            "blank_count": 2,
            "correct_answer": ["A", "B"],
            "point": 5,
        }

        response = self.client.post(
            f"/api/v1/admin/exams/{self.exam.id}/questions/",
            data=json.dumps(payload),
            content_type="application/json",
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["error_detail"], ErrorMessages.INVALID_QUESTION_CREATE_REQUEST.value)

    def test_returns_400_for_fill_blank_count_mismatch(self) -> None:
        payload = {
            "type": "fill_blank",
            "question": "빈칸 문제",
            "prompt": "지문",
            "blank_count": 2,
            "correct_answer": ["A"],
            "point": 5,
        }

        response = self.client.post(
            f"/api/v1/admin/exams/{self.exam.id}/questions/",
            data=json.dumps(payload),
            content_type="application/json",
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["error_detail"], ErrorMessages.INVALID_QUESTION_CREATE_REQUEST.value)

    def test_returns_400_for_short_answer_invalid_type(self) -> None:
        payload = {
            "type": "short_answer",
            "question": "단답형",
            "correct_answer": ["A"],
            "point": 5,
        }

        response = self.client.post(
            f"/api/v1/admin/exams/{self.exam.id}/questions/",
            data=json.dumps(payload),
            content_type="application/json",
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["error_detail"], ErrorMessages.INVALID_QUESTION_CREATE_REQUEST.value)

    def test_returns_400_for_ox_invalid_answer(self) -> None:
        payload = {
            "type": "ox",
            "question": "OX 문제",
            "correct_answer": "Z",
            "point": 5,
        }

        response = self.client.post(
            f"/api/v1/admin/exams/{self.exam.id}/questions/",
            data=json.dumps(payload),
            content_type="application/json",
            headers=self._auth_headers(self.admin_user),
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["error_detail"], ErrorMessages.INVALID_QUESTION_CREATE_REQUEST.value)
