from __future__ import annotations

from datetime import date
from typing import Dict, Iterable, Union

from django.test import Client, TestCase
from rest_framework_simplejwt.tokens import AccessToken

from apps.courses.models.courses import Course
from apps.courses.models.subjects import Subject
from apps.exams.models import Exam
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
            "자격 인증 데이터가 제공되지 않았습니다.",
        )

    def test_403_when_not_admin(self) -> None:
        client = self._auth_client(self.normal_user)

        response = client.get(self.url)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.json()["error_detail"],
            "쪽지시험 목록 조회 권한이 없습니다.",
        )

    def test_400_when_invalid_sort(self) -> None:
        client = self._auth_client(self.admin_user)

        response = client.get(self.url, {"sort": "invalid", "order": "desc"})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error_detail"],
            "유효하지 않은 조회 요청입니다.",
        )

    def test_400_when_invalid_order(self) -> None:
        client = self._auth_client(self.admin_user)

        response = client.get(self.url, {"sort": "created_at", "order": "invalid"})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error_detail"],
            "유효하지 않은 조회 요청입니다.",
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
        QueryDict = Dict[str, QueryVal]  # 🔥 Mapping 말고 Dict

        params: QueryDict = {
            "subject_id": self.subject.id,
            "sort": "title",
            "order": "asc",
            "page": 1,
            "size": 10,
        }
        response = client.get(self.url, params)

        self.assertEqual(response.status_code, 200)
        data = response.json()

        titles = [e["title"] for e in data["exams"]]
        self.assertEqual(titles, ["aaa", "bbb", "ccc"])

    def test_200_filter_by_subject(self) -> None:
        """subject_id 필터링"""
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
        """검색어 필터링"""
        client = self._auth_client(self.admin_user)

        response = client.get(self.url, {"search_keyword": "bb"})

        self.assertEqual(response.status_code, 200)
        data = response.json()

        self.assertEqual(data["total_count"], 1)
        self.assertEqual(data["exams"][0]["title"], "bbb")
