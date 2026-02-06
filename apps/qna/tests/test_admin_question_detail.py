from typing import Any

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from apps.courses.models import (
    Cohort,
    CohortStudent,
    Course,
    LearningCoach,
    OperationManager,
    TrainingAssistant,
)
from apps.qna.constants import ErrorMessages
from apps.qna.models import (
    Answer,
    Question,
    QuestionCategory,
    QuestionImage,
)

User = get_user_model()


@override_settings(USE_QNA_MOCK=False)
class AdminQuestionDetailAPITest(TestCase):
    """
    어드민 질문 상세 조회 API (GET) 테스트
    - 성공 케이스 (기본 조회, 답변 없는 질문, 다양한 역할)
    - 실패 케이스 (401, 403, 404)
    """

    def setUp(self) -> None:
        self.client = Client()

        # 카테고리 계층 생성 (대 > 중 > 소)
        self.cat_depth1 = QuestionCategory.objects.create(name="개발")
        self.cat_depth2 = QuestionCategory.objects.create(name="백엔드", parent=self.cat_depth1)
        self.cat_depth3 = QuestionCategory.objects.create(name="Django", parent=self.cat_depth2)

        # 코스 및 기수 생성
        self.course = Course.objects.create(name="백엔드 개발", tag="BE")
        self.cohort = Cohort.objects.create(
            course=self.course,
            number=3,
            max_student=30,
            start_date="2025-01-01",
            end_date="2025-06-30",
        )

        # 어드민 유저 생성
        self.admin_user = User.objects.create_user(
            email="admin@example.com",
            password="password",
            nickname="관리자",
            name="Admin",
            role="ADMIN",
            gender="MALE",
            birthday="1990-01-01",
            is_active=True,
        )

        # 수강생 유저 생성
        self.student_user = User.objects.create_user(
            email="student@example.com",
            password="password",
            nickname="수강생",
            name="Student",
            role="STUDENT",
            gender="MALE",
            birthday="2000-01-01",
            is_active=True,
        )
        CohortStudent.objects.create(user=self.student_user, cohort=self.cohort)

        # TA 유저 생성
        self.ta_user = User.objects.create_user(
            email="ta@example.com",
            password="password",
            nickname="조교님",
            name="TA",
            role="TA",
            gender="FEMALE",
            birthday="1998-01-01",
            is_active=True,
        )
        TrainingAssistant.objects.create(user=self.ta_user, cohort=self.cohort)

        # LC 유저 생성
        self.lc_user = User.objects.create_user(
            email="lc@example.com",
            password="password",
            nickname="코치님",
            name="LC",
            role="LC",
            gender="MALE",
            birthday="1985-01-01",
            is_active=True,
        )
        LearningCoach.objects.create(user=self.lc_user, course=self.course)

        # OM 유저 생성
        self.om_user = User.objects.create_user(
            email="om@example.com",
            password="password",
            nickname="매니저님",
            name="OM",
            role="OM",
            gender="FEMALE",
            birthday="1988-01-01",
            is_active=True,
        )
        OperationManager.objects.create(user=self.om_user, course=self.course)

        # 질문 생성
        self.question = Question.objects.create(
            author=self.student_user,
            category=self.cat_depth3,
            title="어드민 상세 조회 테스트 제목",
            content="테스트 본문 내용입니다.",
            view_count=10,
        )

        # 이미지 추가
        QuestionImage.objects.create(question=self.question, img_url="http://example.com/img1.jpg")
        QuestionImage.objects.create(question=self.question, img_url="http://example.com/img2.jpg")

        # 다양한 역할의 답변 추가
        self.student_answer = Answer.objects.create(
            author=self.student_user, question=self.question, content="수강생 답변입니다.", is_adopted=True
        )
        self.ta_answer = Answer.objects.create(author=self.ta_user, question=self.question, content="조교 답변입니다.")
        self.lc_answer = Answer.objects.create(
            author=self.lc_user, question=self.question, content="러닝코치 답변입니다."
        )
        self.om_answer = Answer.objects.create(
            author=self.om_user, question=self.question, content="운영매니저 답변입니다."
        )
        self.admin_answer = Answer.objects.create(
            author=self.admin_user, question=self.question, content="관리자 답변입니다."
        )

        self.url = reverse("admin-qna-question-detail", kwargs={"question_id": self.question.id})

    def _get_auth_header(self, user: Any) -> dict[str, Any]:
        refresh = RefreshToken.for_user(user)
        return {"HTTP_AUTHORIZATION": f"Bearer {str(refresh.access_token)}"}

    def test_admin_question_detail_success(self) -> None:
        """[성공] 어드민이 상세 조회 → 응답 필드 전체 검증"""
        response = self.client.get(self.url, **self._get_auth_header(self.admin_user))
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 질문 기본 정보
        self.assertEqual(data["question_id"], self.question.id)
        self.assertEqual(data["title"], "어드민 상세 조회 테스트 제목")
        self.assertEqual(data["content"], "테스트 본문 내용입니다.")
        self.assertEqual(data["view_count"], 10)  # 어드민 조회 시 조회수 증가 없음
        self.assertTrue(data["has_answer"])

        # 이미지
        self.assertEqual(len(data["img_url"]), 2)
        self.assertIn("http://example.com/img1.jpg", data["img_url"])

        # 작성자 정보
        author = data["author"]
        self.assertEqual(author["nickname"], "수강생")
        self.assertEqual(author["course_generation"], "백엔드 개발 3기")

        # 답변 수
        self.assertEqual(len(data["answers"]), 5)

    def test_admin_question_detail_no_answers(self) -> None:
        """[성공] 답변 없는 질문 → has_answer=false, answers=[]"""
        empty_q = Question.objects.create(
            author=self.student_user, category=self.cat_depth1, title="답변없는 질문", content="내용"
        )
        url = reverse("admin-qna-question-detail", kwargs={"question_id": empty_q.id})

        response = self.client.get(url, **self._get_auth_header(self.admin_user))
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(data["has_answer"])
        self.assertEqual(data["answers"], [])

    def test_admin_question_detail_role_titles(self) -> None:
        """[성공] 다양한 역할의 답변 작성자 role_title, course_generation 검증"""
        response = self.client.get(self.url, **self._get_auth_header(self.admin_user))
        data = response.json()

        answers_by_content: dict[str, dict[str, str]] = {}
        for ans in data["answers"]:
            answers_by_content[ans["content"]] = ans["author"]

        # STUDENT
        student_author = answers_by_content["수강생 답변입니다."]
        self.assertEqual(student_author["role_title"], "")
        self.assertEqual(student_author["course_generation"], "백엔드 개발 3기")

        # TA
        ta_author = answers_by_content["조교 답변입니다."]
        self.assertEqual(ta_author["role_title"], "백엔드 개발 3기 조교")
        self.assertEqual(ta_author["course_generation"], "백엔드 개발 3기")

        # LC
        lc_author = answers_by_content["러닝코치 답변입니다."]
        self.assertEqual(lc_author["role_title"], "러닝 코치")
        self.assertEqual(lc_author["course_generation"], "")

        # OM
        om_author = answers_by_content["운영매니저 답변입니다."]
        self.assertEqual(om_author["role_title"], "교육 운영 매니저")
        self.assertEqual(om_author["course_generation"], "")

        # ADMIN
        admin_author = answers_by_content["관리자 답변입니다."]
        self.assertEqual(admin_author["role_title"], "관리자")
        self.assertEqual(admin_author["course_generation"], "")

    def test_admin_question_detail_unauthorized(self) -> None:
        """[실패] 401 Unauthorized - 비로그인"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()["error_detail"], ErrorMessages.UNAUTHORIZED_ADMIN_QUESTION_DETAIL.value)

    def test_admin_question_detail_forbidden_student(self) -> None:
        """[실패] 403 Forbidden - STUDENT 접근"""
        response = self.client.get(self.url, **self._get_auth_header(self.student_user))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["error_detail"], ErrorMessages.FORBIDDEN_ADMIN_QUESTION_DETAIL.value)

    def test_admin_question_detail_not_found(self) -> None:
        """[실패] 404 Not Found - 존재하지 않는 question_id"""
        url = reverse("admin-qna-question-detail", kwargs={"question_id": 99999})
        response = self.client.get(url, **self._get_auth_header(self.admin_user))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["error_detail"], ErrorMessages.NOT_FOUND_QUESTION.value)
