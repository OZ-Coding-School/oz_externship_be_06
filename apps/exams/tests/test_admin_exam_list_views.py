from __future__ import annotations

from datetime import date, timedelta
from typing import Dict, Iterable, Union, cast

from django.test import Client, TestCase
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken

from apps.courses.models import Cohort
from apps.courses.models.courses import Course
from apps.courses.models.subjects import Subject
from apps.exams.constants import ErrorMessages
from apps.exams.models import Exam, ExamQuestion
from apps.users.models import User


class AdminExamListAPITest(TestCase):

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

        Exam.objects.create(subject=self.subject, title="ccc", thumbnail_img_url="exam1.png")
        Exam.objects.create(subject=self.subject, title="aaa", thumbnail_img_url="exam2.png")
        Exam.objects.create(subject=self.subject, title="bbb", thumbnail_img_url="exam3.png")

        self.admin_user = User.objects.create_user(
            email="admin@example.com",
            password="password123",
            name="어드민",
            nickname="어드민닉",
            phone_number="01099999999",
            gender=User.Gender.MALE,
            birthday=date(1995, 1, 1),
            role=User.Role.ADMIN,
        )

        self.normal_user = User.objects.create_user(
            email="user@example.com",
            password="password123",
            name="일반유저",
            nickname="닉네임",
            phone_number="01011111111",
            gender=User.Gender.FEMALE,
            birthday=date(2000, 1, 1),
            role=User.Role.USER,
        )

        self.url = "/api/v1/admin/exams"

    def _auth_client(self, user: User) -> Client:
        token = AccessToken.for_user(user)
        client = Client()
        client.defaults["HTTP_AUTHORIZATION"] = f"Bearer {token}"
        return client

    def test_401_when_no_auth(self) -> None:
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json()["error_detail"],
            ErrorMessages.UNAUTHORIZED,
        )

    def test_403_when_not_admin(self) -> None:
        client = self._auth_client(self.normal_user)

        response = client.get(self.url)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.json()["error_detail"],
            ErrorMessages.NO_EXAM_LIST_PERMISSION,
        )

    def test_400_when_invalid_sort(self) -> None:
        client = self._auth_client(self.admin_user)

        response = client.get(self.url, {"sort": "invalid", "order": "desc"})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error_detail"],
            ErrorMessages.INVALID_SUBMISSION_LIST_REQUEST,
        )

    def test_400_when_invalid_order(self) -> None:
        client = self._auth_client(self.admin_user)

        response = client.get(self.url, {"sort": "created_at", "order": "invalid"})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error_detail"],
            ErrorMessages.INVALID_SUBMISSION_LIST_REQUEST,
        )

    def test_200_success_default_sort(self) -> None:
        """기본 정렬(created_at desc)로 200 성공"""
        client = self._auth_client(self.admin_user)

        response = client.get(self.url)

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertIn("page", data)
        self.assertIn("size", data)
        self.assertIn("total_count", data)
        self.assertIn("exams", data)

        self.assertEqual(data["total_count"], 3)
        self.assertEqual(len(data["exams"]), 3)

    def test_200_success_and_title_asc_sort(self) -> None:
        client = self._auth_client(self.admin_user)

        QueryVal = Union[str, bytes, int, Iterable[Union[str, bytes, int]]]
        QueryDict = Dict[str, QueryVal]

        params = cast(
            QueryDict,
            {
                "subject_id": int(self.subject.id),
                "sort": "title",
                "order": "asc",
                "page": 1,
                "size": 10,
            },
        )

        response = client.get(self.url, params)

        self.assertEqual(response.status_code, 200)
        data = response.json()

        titles = [e["exam_title"] for e in data["exams"]]
        self.assertEqual(titles, ["aaa", "bbb", "ccc"])

    def test_200_filter_by_subject(self) -> None:
        other_subject = Subject.objects.create(
            course=self.course,
            title="다른과목",
            number_of_days=1,
            number_of_hours=1,
            thumbnail_img_url="other.png",
        )
        Exam.objects.create(subject=other_subject, title="다른 시험", thumbnail_img_url="other_exam.png")

        client = self._auth_client(self.admin_user)

        response = client.get(self.url, {"subject_id": self.subject.id})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total_count"], 3)

    def test_200_search_keyword(self) -> None:
        client = self._auth_client(self.admin_user)

        response = client.get(self.url, {"search_keyword": "bb"})

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["total_count"], 1)
        self.assertEqual(data["exams"][0]["exam_title"], "bbb")

    def test_200_question_and_submit_count_calculated_correctly(self) -> None:
        client = self._auth_client(self.admin_user)

        exam = Exam.objects.get(title="aaa")

        ExamQuestion.objects.create(
            exam=exam,
            question="문제 1",
            type=ExamQuestion.TypeChoices.OX,
            answer=True,
            point=10,
            explanation="해설 1",
        )
        ExamQuestion.objects.create(
            exam=exam,
            question="문제 2",
            type=ExamQuestion.TypeChoices.OX,
            answer=False,
            point=10,
            explanation="해설 2",
        )

        cohort = Cohort.objects.create(
            course=self.course,
            number=1,
            max_student=30,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 3, 1),
        )

        open_at = timezone.now() - timedelta(hours=1)
        close_at = timezone.now() + timedelta(days=1)

        deployment = exam.deployments.create(
            cohort=cohort,
            access_code="TESTCODE",
            open_at=open_at,
            close_at=close_at,
            questions_snapshot_json={"version": 1, "questions": []},
        )

        deployment.submissions.create(
            submitter=self.normal_user,
            started_at=timezone.now() - timedelta(minutes=5),
            answers_json={"answers": []},
            score=20,
            correct_answer_count=2,
            cheating_count=0,
        )

        response = client.get(self.url, {"sort": "title", "order": "asc"})
        self.assertEqual(response.status_code, 200)

        data = response.json()
        exams = data["exams"]

        exam_aaa = next(e for e in exams if e["exam_title"] == "aaa")

        self.assertEqual(exam_aaa["question_count"], 2)
        self.assertEqual(exam_aaa["submit_count"], 1)

        for e in exams:
            if e["exam_title"] != "aaa":
                self.assertEqual(e["question_count"], 0)
                self.assertEqual(e["submit_count"], 0)
