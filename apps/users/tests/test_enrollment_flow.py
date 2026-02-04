"""
수강신청 → 승인 → 수강목록 확인 전체 플로우 테스트
"""

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.courses.models import Cohort, Course
from apps.courses.models.cohort_students import CohortStudent
from apps.users.models import StudentEnrollmentRequest, User
from apps.users.services.admin_student_enrollment_service import (
    accept_enrollments,
    reject_enrollments,
)
from apps.users.services.course_service import get_enrolled_courses
from apps.users.services.enroll_student_service import (
    AlreadyEnrolledError,
    CohortNotFoundError,
    NotUserRoleError,
    enroll_student,
)


class EnrollmentFlowTestCase(TestCase):
    """수강신청 → 승인 → 수강목록 확인 전체 플로우 테스트"""

    def setUp(self) -> None:
        """테스트 데이터 생성"""
        # 일반 사용자 생성
        self.user = User.objects.create(
            email="test_student@example.com",
            name="테스트학생",
            nickname="학생1",
            phone_number="010-1234-5678",
            gender=User.Gender.MALE,
            birthday="1990-01-01",
            role=User.Role.USER,
            is_active=True,
        )

        # 과정 생성
        self.course = Course.objects.create(
            name="Python 기초",
            tag="PY",
            description="파이썬 입문 과정",
        )

        # 기수 생성 (모집중 상태)
        self.cohort = Cohort.objects.create(
            course=self.course,
            number=15,
            max_student=30,
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=90)).date(),
            status=Cohort.StatusChoices.PREPARING,
        )

    def test_complete_enrollment_flow(self) -> None:
        """
        전체 수강신청 플로우 테스트:
        1. 일반 사용자가 수강신청
        2. 관리자가 승인
        3. 수강목록에서 확인
        """
        # ====== Step 1: 수강신청 ======
        print("\n" + "=" * 60)
        print("[Step 1] 수강신청")
        print("=" * 60)

        enrollment = enroll_student(user=self.user, cohort_id=self.cohort.id)

        self.assertEqual(enrollment.user, self.user)
        self.assertEqual(enrollment.cohort, self.cohort)
        self.assertEqual(enrollment.status, StudentEnrollmentRequest.Status.PENDING)

        print(f"  - 신청 ID: {enrollment.id}")
        print(f"  - 사용자: {self.user.email}")
        print(f"  - 기수: {self.cohort.course.name} {self.cohort.number}기")
        print(f"  - 상태: {enrollment.status}")
        print(f"  - 유저 Role: {self.user.role}")

        # 수강신청 전에는 수강목록에 없음
        enrolled_courses = get_enrolled_courses(user=self.user)
        self.assertEqual(len(enrolled_courses), 0)
        print(f"  - 수강목록: {len(enrolled_courses)}개 (아직 승인 전)")

        # ====== Step 2: 관리자 승인 ======
        print("\n" + "=" * 60)
        print("[Step 2] 관리자 승인")
        print("=" * 60)

        approved_count = accept_enrollments([enrollment.id])

        self.assertEqual(approved_count, 1)

        # 데이터 새로고침
        enrollment.refresh_from_db()
        self.user.refresh_from_db()

        self.assertEqual(enrollment.status, StudentEnrollmentRequest.Status.APPROVED)
        self.assertIsNotNone(enrollment.accepted_at)
        self.assertEqual(self.user.role, User.Role.STUDENT)

        print(f"  - 승인된 수: {approved_count}")
        print(f"  - 신청 상태: {enrollment.status}")
        print(f"  - 승인 시각: {enrollment.accepted_at}")
        print(f"  - 유저 Role 변경: USER -> {self.user.role}")

        # CohortStudent 생성 확인
        cohort_student_exists = CohortStudent.objects.filter(user=self.user, cohort=self.cohort).exists()
        self.assertTrue(cohort_student_exists)
        print(f"  - CohortStudent 생성: {cohort_student_exists}")

        # ====== Step 3: 수강목록 확인 ======
        print("\n" + "=" * 60)
        print("[Step 3] 수강목록 확인")
        print("=" * 60)

        enrolled_courses = get_enrolled_courses(user=self.user)

        self.assertEqual(len(enrolled_courses), 1)

        course_info = enrolled_courses[0]
        self.assertEqual(course_info["course"]["id"], self.course.id)
        self.assertEqual(course_info["course"]["name"], self.course.name)
        self.assertEqual(course_info["cohort"]["id"], self.cohort.id)
        self.assertEqual(course_info["cohort"]["number"], self.cohort.number)

        print(f"  - 수강목록 개수: {len(enrolled_courses)}")
        print(f"  - 과정: {course_info['course']['name']}")
        print(f"  - 기수: {course_info['cohort']['number']}기")
        print(f"  - 기수 상태: {course_info['cohort']['status']}")

        print("\n" + "=" * 60)
        print("✅ 전체 플로우 테스트 성공!")
        print("=" * 60)

    def test_enroll_student_not_user_role(self) -> None:
        """일반 회원이 아닌 경우 수강신청 불가"""
        # STUDENT 역할로 변경
        self.user.role = User.Role.STUDENT
        self.user.save()

        with self.assertRaises(NotUserRoleError):
            enroll_student(user=self.user, cohort_id=self.cohort.id)

    def test_enroll_student_cohort_not_found(self) -> None:
        """존재하지 않는 기수 신청 불가"""
        with self.assertRaises(CohortNotFoundError):
            enroll_student(user=self.user, cohort_id=99999)

    def test_enroll_student_already_enrolled(self) -> None:
        """중복 수강신청 불가"""
        # 첫 번째 신청
        enroll_student(user=self.user, cohort_id=self.cohort.id)

        # 중복 신청 시도
        with self.assertRaises(AlreadyEnrolledError):
            enroll_student(user=self.user, cohort_id=self.cohort.id)

    def test_reject_enrollment(self) -> None:
        """수강신청 거절 테스트"""
        # 수강신청
        enrollment = enroll_student(user=self.user, cohort_id=self.cohort.id)
        self.assertEqual(enrollment.status, StudentEnrollmentRequest.Status.PENDING)

        # 거절
        rejected_count = reject_enrollments([enrollment.id])
        self.assertEqual(rejected_count, 1)

        # 상태 확인
        enrollment.refresh_from_db()
        self.user.refresh_from_db()

        self.assertEqual(enrollment.status, StudentEnrollmentRequest.Status.REJECTED)
        self.assertEqual(self.user.role, User.Role.USER)  # 역할 유지

        # 수강목록에 없음
        enrolled_courses = get_enrolled_courses(user=self.user)
        self.assertEqual(len(enrolled_courses), 0)

    def test_multiple_cohort_enrollments(self) -> None:
        """여러 기수 수강신청 및 승인"""
        # 추가 기수 생성
        cohort2 = Cohort.objects.create(
            course=self.course,
            number=16,
            max_student=30,
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=90)).date(),
            status=Cohort.StatusChoices.PREPARING,
        )

        # 다른 과정 생성
        course2 = Course.objects.create(
            name="JavaScript 기초",
            tag="JS",
            description="자바스크립트 입문",
        )
        cohort3 = Cohort.objects.create(
            course=course2,
            number=10,
            max_student=25,
            start_date=timezone.now().date(),
            end_date=(timezone.now() + timedelta(days=60)).date(),
            status=Cohort.StatusChoices.PREPARING,
        )

        # 첫 번째 기수 신청 및 승인
        enrollment1 = enroll_student(user=self.user, cohort_id=self.cohort.id)
        accept_enrollments([enrollment1.id])

        self.user.refresh_from_db()
        self.assertEqual(self.user.role, User.Role.STUDENT)

        # 이제 STUDENT 역할이므로 추가 신청 불가
        with self.assertRaises(NotUserRoleError):
            enroll_student(user=self.user, cohort_id=cohort2.id)

        # 수강목록 확인 (1개)
        enrolled_courses = get_enrolled_courses(user=self.user)
        self.assertEqual(len(enrolled_courses), 1)
