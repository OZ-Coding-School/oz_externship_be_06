from datetime import date, timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.courses.models import Cohort, CohortStudent, Course, Subject
from apps.users.models import User


class AdminCohortCreateAPITests(TestCase):
    """109: 기수 등록 API 테스트"""

    client: APIClient

    def setUp(self) -> None:
        self.client = APIClient()
        self.url = "/api/v1/admin/cohorts"

        self.admin_user = User.objects.create_user(
            email="admin@example.com",
            password="Testpass123!",
            birthday=date(2000, 1, 1),
            phone_number="01012345678",
            name="관리자",
            nickname="admin",
            gender="MALE",
            role=User.Role.ADMIN,
            is_staff=True,
            is_active=True,
        )

        self.student_user = User.objects.create_user(
            email="student@example.com",
            password="Testpass123!",
            birthday=date(2000, 1, 1),
            phone_number="01012345679",
            name="수강생",
            nickname="student",
            gender="MALE",
            role=User.Role.STUDENT,
            is_active=True,
        )

        self.course = Course.objects.create(
            name="백엔드 부트캠프",
            tag="BE",
        )

    def _set_auth(self, user: User) -> None:
        access = str(RefreshToken.for_user(user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def test_create_cohort_success_201(self) -> None:
        self._set_auth(self.admin_user)

        data = {
            "course_id": self.course.id,
            "number": 15,
            "max_student": 30,
            "start_date": "2025-11-01",
            "end_date": "2026-04-30",
            "status": "PREPARING",
        }

        res = self.client.post(self.url, data, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        response_data = res.json()
        self.assertEqual(response_data["detail"], "기수가 등록되었습니다.")
        self.assertIn("id", response_data)

        cohort = Cohort.objects.get(id=response_data["id"])
        self.assertEqual(cohort.number, 15)
        self.assertEqual(cohort.course_id, self.course.id)

    def test_create_cohort_without_status_201(self) -> None:
        self._set_auth(self.admin_user)

        data = {
            "course_id": self.course.id,
            "number": 16,
            "max_student": 25,
            "start_date": "2025-12-01",
            "end_date": "2026-05-31",
        }

        res = self.client.post(self.url, data, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        cohort = Cohort.objects.get(id=res.json()["id"])
        self.assertEqual(cohort.status, Cohort.StatusChoices.PREPARING)

    def test_create_cohort_invalid_date_400(self) -> None:
        self._set_auth(self.admin_user)

        data = {
            "course_id": self.course.id,
            "number": 15,
            "max_student": 30,
            "start_date": "2026-04-30",
            "end_date": "2025-11-01",
        }

        res = self.client.post(self.url, data, format="json")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_cohort_course_not_found_404(self) -> None:
        self._set_auth(self.admin_user)

        data = {
            "course_id": 99999,
            "number": 15,
            "max_student": 30,
            "start_date": "2025-11-01",
            "end_date": "2026-04-30",
        }

        res = self.client.post(self.url, data, format="json")

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error_detail", res.json())

    def test_create_cohort_unauthenticated_401(self) -> None:
        data = {
            "course_id": self.course.id,
            "number": 15,
            "max_student": 30,
            "start_date": "2025-11-01",
            "end_date": "2026-04-30",
        }

        res = self.client.post(self.url, data, format="json")

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_cohort_forbidden_403(self) -> None:
        self._set_auth(self.student_user)

        data = {
            "course_id": self.course.id,
            "number": 15,
            "max_student": 30,
            "start_date": "2025-11-01",
            "end_date": "2026-04-30",
        }

        res = self.client.post(self.url, data, format="json")

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class CohortListAPITests(TestCase):
    """110: 기수 리스트 조회 API 테스트"""

    client: APIClient

    def setUp(self) -> None:
        self.client = APIClient()

        self.user = User.objects.create_user(
            email="user@example.com",
            password="Testpass123!",
            birthday=date(2000, 1, 1),
            phone_number="01012345678",
            name="사용자",
            nickname="user",
            gender="MALE",
            role=User.Role.STUDENT,
            is_active=True,
        )

        self.course = Course.objects.create(name="백엔드", tag="BE")

        self.cohort1 = Cohort.objects.create(
            course=self.course,
            number=14,
            max_student=30,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 6, 30),
            status=Cohort.StatusChoices.IN_PROGRESS,
        )
        self.cohort2 = Cohort.objects.create(
            course=self.course,
            number=15,
            max_student=30,
            start_date=date(2025, 7, 1),
            end_date=date(2025, 12, 31),
            status=Cohort.StatusChoices.PREPARING,
        )

        self.url = f"/api/v1/{self.course.id}/cohorts"

    def _set_auth(self, user: User) -> None:
        access = str(RefreshToken.for_user(user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def test_list_cohorts_success_200(self) -> None:
        self._set_auth(self.user)

        res = self.client.get(self.url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["number"], 14)
        self.assertEqual(data[1]["number"], 15)

    def test_list_cohorts_empty_200(self) -> None:
        self._set_auth(self.user)

        other_course = Course.objects.create(name="프론트", tag="FE")
        url = f"/api/v1/{other_course.id}/cohorts"

        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.json(), [])

    def test_list_cohorts_unauthenticated_401(self) -> None:
        res = self.client.get(self.url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AdminCohortUpdateAPITests(TestCase):
    """111: 기수 정보 수정 API 테스트"""

    client: APIClient

    def setUp(self) -> None:
        self.client = APIClient()

        self.admin_user = User.objects.create_user(
            email="admin@example.com",
            password="Testpass123!",
            birthday=date(2000, 1, 1),
            phone_number="01012345678",
            name="관리자",
            nickname="admin",
            gender="MALE",
            role=User.Role.ADMIN,
            is_staff=True,
            is_active=True,
        )

        self.student_user = User.objects.create_user(
            email="student@example.com",
            password="Testpass123!",
            birthday=date(2000, 1, 1),
            phone_number="01012345679",
            name="수강생",
            nickname="student",
            gender="MALE",
            role=User.Role.STUDENT,
            is_active=True,
        )

        self.course = Course.objects.create(name="백엔드", tag="BE")
        self.cohort = Cohort.objects.create(
            course=self.course,
            number=15,
            max_student=30,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 6, 30),
            status=Cohort.StatusChoices.PREPARING,
        )

        self.url = f"/api/v1/admin/cohorts/{self.cohort.id}"

    def _set_auth(self, user: User) -> None:
        access = str(RefreshToken.for_user(user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def test_update_cohort_success_200(self) -> None:
        self._set_auth(self.admin_user)

        data = {"max_student": 40, "status": "IN_PROGRESS"}

        res = self.client.patch(self.url, data, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        response_data = res.json()
        self.assertEqual(response_data["max_student"], 40)
        self.assertEqual(response_data["status"], "IN_PROGRESS")

    def test_update_cohort_partial_200(self) -> None:
        self._set_auth(self.admin_user)

        data = {"number": 16}

        res = self.client.patch(self.url, data, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.cohort.refresh_from_db()
        self.assertEqual(self.cohort.number, 16)

    def test_update_cohort_invalid_date_400(self) -> None:
        self._set_auth(self.admin_user)

        data = {"start_date": "2025-07-01"}

        res = self.client.patch(self.url, data, format="json")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_cohort_not_found_404(self) -> None:
        self._set_auth(self.admin_user)

        url = "/api/v1/admin/cohorts/99999"

        res = self.client.patch(url, {"number": 20}, format="json")

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_cohort_unauthenticated_401(self) -> None:
        data = {"max_student": 40}

        res = self.client.patch(self.url, data, format="json")

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_cohort_forbidden_403(self) -> None:
        self._set_auth(self.student_user)

        data = {"max_student": 40}

        res = self.client.patch(self.url, data, format="json")

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminCohortAvgScoresAPITests(TestCase):
    """112: 기수별 평균 점수 조회 API 테스트"""

    client: APIClient

    def setUp(self) -> None:
        self.client = APIClient()

        self.admin_user = User.objects.create_user(
            email="admin@example.com",
            password="Testpass123!",
            birthday=date(2000, 1, 1),
            phone_number="01012345678",
            name="관리자",
            nickname="admin",
            gender="MALE",
            role=User.Role.ADMIN,
            is_staff=True,
            is_active=True,
        )

        self.student_user = User.objects.create_user(
            email="student@example.com",
            password="Testpass123!",
            birthday=date(2000, 1, 1),
            phone_number="01012345679",
            name="수강생",
            nickname="student",
            gender="MALE",
            role=User.Role.STUDENT,
            is_active=True,
        )

        self.course = Course.objects.create(name="백엔드", tag="BE")
        self.cohort = Cohort.objects.create(
            course=self.course,
            number=15,
            max_student=30,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 6, 30),
        )

        self.url = f"/api/v1/admin/courses/{self.course.id}/cohorts/avg-scores"

    def _set_auth(self, user: User) -> None:
        access = str(RefreshToken.for_user(user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def test_get_avg_scores_success_200(self) -> None:
        self._set_auth(self.admin_user)

        res = self.client.get(self.url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "15기")
        self.assertEqual(data[0]["score"], 0)

    def test_get_avg_scores_empty_200(self) -> None:
        self._set_auth(self.admin_user)

        other_course = Course.objects.create(name="프론트", tag="FE")
        url = f"/api/v1/admin/courses/{other_course.id}/cohorts/avg-scores"

        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.json(), [])

    def test_get_avg_scores_course_not_found_404(self) -> None:
        self._set_auth(self.admin_user)

        url = "/api/v1/admin/courses/99999/cohorts/avg-scores"

        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_avg_scores_unauthenticated_401(self) -> None:
        res = self.client.get(self.url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_avg_scores_forbidden_403(self) -> None:
        self._set_auth(self.student_user)

        res = self.client.get(self.url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminCohortStudentsAPITests(TestCase):
    """113: 기수별 수강생 목록 조회 API 테스트"""

    client: APIClient

    def setUp(self) -> None:
        self.client = APIClient()

        self.admin_user = User.objects.create_user(
            email="admin@example.com",
            password="Testpass123!",
            birthday=date(2000, 1, 1),
            phone_number="01012345678",
            name="관리자",
            nickname="admin",
            gender="MALE",
            role=User.Role.ADMIN,
            is_staff=True,
            is_active=True,
        )

        self.student1 = User.objects.create_user(
            email="student1@example.com",
            password="Testpass123!",
            birthday=date(2000, 1, 1),
            phone_number="01012345679",
            name="류액트",
            nickname="ryuact",
            gender="MALE",
            role=User.Role.STUDENT,
            is_active=True,
        )

        self.student2 = User.objects.create_user(
            email="student2@example.com",
            password="Testpass123!",
            birthday=date(2000, 1, 1),
            phone_number="01012345680",
            name="권노드",
            nickname="kwonnode",
            gender="MALE",
            role=User.Role.STUDENT,
            is_active=True,
        )

        self.course = Course.objects.create(name="백엔드", tag="BE")
        self.cohort = Cohort.objects.create(
            course=self.course,
            number=15,
            max_student=30,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 6, 30),
        )

        CohortStudent.objects.create(user=self.student1, cohort=self.cohort)
        CohortStudent.objects.create(user=self.student2, cohort=self.cohort)

        self.url = f"/api/v1/admin/cohorts/{self.cohort.id}/students"

    def _set_auth(self, user: User) -> None:
        access = str(RefreshToken.for_user(user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def test_get_students_success_200(self) -> None:
        self._set_auth(self.admin_user)

        res = self.client.get(self.url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertEqual(len(data), 2)
        values = [d["value"] for d in data]
        self.assertIn("ryuact", values)
        self.assertIn("kwonnode", values)

    def test_get_students_empty_200(self) -> None:
        self._set_auth(self.admin_user)

        empty_cohort = Cohort.objects.create(
            course=self.course,
            number=16,
            max_student=30,
            start_date=date(2025, 7, 1),
            end_date=date(2025, 12, 31),
        )
        url = f"/api/v1/admin/cohorts/{empty_cohort.id}/students"

        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.json(), [])

    def test_get_students_cohort_not_found_404(self) -> None:
        self._set_auth(self.admin_user)

        url = "/api/v1/admin/cohorts/99999/students"

        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_students_unauthenticated_401(self) -> None:
        res = self.client.get(self.url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_students_forbidden_403(self) -> None:
        self._set_auth(self.student1)

        res = self.client.get(self.url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminSubjectListAPITests(TestCase):
    """114: 과목 목록 조회 API 테스트"""

    client: APIClient

    def setUp(self) -> None:
        self.client = APIClient()

        self.admin_user = User.objects.create_user(
            email="admin@example.com",
            password="Testpass123!",
            birthday=date(2000, 1, 1),
            phone_number="01012345678",
            name="관리자",
            nickname="admin",
            gender="MALE",
            role=User.Role.ADMIN,
            is_staff=True,
            is_active=True,
        )

        self.student_user = User.objects.create_user(
            email="student@example.com",
            password="Testpass123!",
            birthday=date(2000, 1, 1),
            phone_number="01012345679",
            name="수강생",
            nickname="student",
            gender="MALE",
            role=User.Role.STUDENT,
            is_active=True,
        )

        self.course = Course.objects.create(name="백엔드", tag="BE")

        self.subject1 = Subject.objects.create(
            course=self.course,
            title="Python",
            number_of_days=10,
            number_of_hours=80,
            status=True,
        )
        self.subject2 = Subject.objects.create(
            course=self.course,
            title="Django",
            number_of_days=15,
            number_of_hours=120,
            status=False,
        )

        self.url = f"/api/v1/admin/courses/{self.course.id}/subjects"

    def _set_auth(self, user: User) -> None:
        access = str(RefreshToken.for_user(user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def test_list_subjects_success_200(self) -> None:
        self._set_auth(self.admin_user)

        res = self.client.get(self.url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.json()
        self.assertEqual(len(data), 2)
        titles = [d["title"] for d in data]
        self.assertIn("Python", titles)
        self.assertIn("Django", titles)

    def test_list_subjects_status_format_200(self) -> None:
        self._set_auth(self.admin_user)

        res = self.client.get(self.url)

        data = res.json()
        python_subject = next(d for d in data if d["title"] == "Python")
        django_subject = next(d for d in data if d["title"] == "Django")
        self.assertEqual(python_subject["status"], "activated")
        self.assertEqual(django_subject["status"], "deactivated")

    def test_list_subjects_empty_200(self) -> None:
        self._set_auth(self.admin_user)

        other_course = Course.objects.create(name="프론트", tag="FE")
        url = f"/api/v1/admin/courses/{other_course.id}/subjects"

        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.json(), [])

    def test_list_subjects_unauthenticated_401(self) -> None:
        res = self.client.get(self.url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_subjects_forbidden_403(self) -> None:
        self._set_auth(self.student_user)

        res = self.client.get(self.url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminSubjectScatterAPITests(TestCase):
    """115: 과목별 학습시간/점수 산점도 조회 API 테스트"""

    client: APIClient

    def setUp(self) -> None:
        self.client = APIClient()

        self.admin_user = User.objects.create_user(
            email="admin@example.com",
            password="Testpass123!",
            birthday=date(2000, 1, 1),
            phone_number="01012345678",
            name="관리자",
            nickname="admin",
            gender="MALE",
            role=User.Role.ADMIN,
            is_staff=True,
            is_active=True,
        )

        self.student_user = User.objects.create_user(
            email="student@example.com",
            password="Testpass123!",
            birthday=date(2000, 1, 1),
            phone_number="01012345679",
            name="수강생",
            nickname="student",
            gender="MALE",
            role=User.Role.STUDENT,
            is_active=True,
        )

        self.course = Course.objects.create(name="백엔드", tag="BE")
        self.subject = Subject.objects.create(
            course=self.course,
            title="Python",
            number_of_days=10,
            number_of_hours=80,
        )

        self.url = f"/api/v1/admin/subjects/{self.subject.id}/scatter"

    def _set_auth(self, user: User) -> None:
        access = str(RefreshToken.for_user(user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def test_get_scatter_success_200(self) -> None:
        self._set_auth(self.admin_user)

        res = self.client.get(self.url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsInstance(res.json(), list)

    def test_get_scatter_subject_not_found_404(self) -> None:
        self._set_auth(self.admin_user)

        url = "/api/v1/admin/subjects/99999/scatter"

        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_scatter_unauthenticated_401(self) -> None:
        res = self.client.get(self.url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_scatter_forbidden_403(self) -> None:
        self._set_auth(self.student_user)

        res = self.client.get(self.url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
