from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

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
from apps.qna.tests.factories import (
    create_admin_user,
    create_lc_user,
    create_om_user,
    create_student_user,
    create_ta_user,
)
from apps.users.models import User


@override_settings(USE_QNA_MOCK=False)
class AdminQuestionDetailAPITest(APITestCase):
    """
    어드민 질문 상세 조회 API (GET) 테스트
    - 성공 케이스
        - 200 OK: 기본 조회 (질문/이미지/답변 데이터)
        - 200 OK: 답변이 없는 질문 조회
        - 200 OK: 다양한 역할별 작성자 정보 검증
    - 실패 케이스
        - 401 Unauthorized: 로그인하지 않은 유저
        - 403 Forbidden: STUDENT 유저 접근
        - 404 Not Found: 존재하지 않는 question_id
    """

    course: Course
    cohort: Cohort
    admin_user: User
    student_user: User
    ta_user: User
    lc_user: User
    om_user: User
    cat_depth1: QuestionCategory
    cat_depth2: QuestionCategory
    cat_depth3: QuestionCategory
    question: Question
    img1: QuestionImage
    img2: QuestionImage
    student_answer: Answer
    ta_answer: Answer
    lc_answer: Answer
    om_answer: Answer
    admin_answer: Answer
    url: str

    @classmethod
    def setUpTestData(cls) -> None:
        # 코스 및 기수 생성
        cls.course = Course.objects.create(name="백엔드 개발", tag="BE")
        cls.cohort = Cohort.objects.create(
            course=cls.course,
            number=3,
            max_student=30,
            start_date="2025-01-01",
            end_date="2025-06-30",
        )

        # 테스트용 유저
        cls.admin_user = create_admin_user()

        cls.student_user = create_student_user()
        CohortStudent.objects.create(user=cls.student_user, cohort=cls.cohort)

        cls.ta_user = create_ta_user()
        TrainingAssistant.objects.create(user=cls.ta_user, cohort=cls.cohort)

        cls.lc_user = create_lc_user()
        LearningCoach.objects.create(user=cls.lc_user, course=cls.course)

        cls.om_user = create_om_user()
        OperationManager.objects.create(user=cls.om_user, course=cls.course)

        # 카테고리 계층 생성 (대 > 중 > 소)
        cls.cat_depth1 = QuestionCategory.objects.create(name="개발")
        cls.cat_depth2 = QuestionCategory.objects.create(name="백엔드", parent=cls.cat_depth1)
        cls.cat_depth3 = QuestionCategory.objects.create(name="Django", parent=cls.cat_depth2)

        # 질문 생성
        cls.question = Question.objects.create(
            author=cls.student_user,
            category=cls.cat_depth3,
            title="어드민 상세 조회 테스트 제목",
            content="테스트 본문 내용입니다.",
            view_count=10,
        )

        # 이미지 추가
        cls.img1 = QuestionImage.objects.create(question=cls.question, img_url="http://example.com/img1.jpg")
        cls.img2 = QuestionImage.objects.create(question=cls.question, img_url="http://example.com/img2.jpg")

        # 다양한 역할의 답변 추가
        cls.student_answer = Answer.objects.create(
            author=cls.student_user, question=cls.question, content="수강생 답변입니다.", is_adopted=True
        )
        cls.ta_answer = Answer.objects.create(author=cls.ta_user, question=cls.question, content="조교 답변입니다.")
        cls.lc_answer = Answer.objects.create(author=cls.lc_user, question=cls.question, content="러닝코치 답변입니다.")
        cls.om_answer = Answer.objects.create(
            author=cls.om_user, question=cls.question, content="운영매니저 답변입니다."
        )
        cls.admin_answer = Answer.objects.create(
            author=cls.admin_user, question=cls.question, content="관리자 답변입니다."
        )

        # URL
        cls.url = reverse("admin-qna-question-detail", kwargs={"question_id": cls.question.id})

    # ==========================================================================
    # 성공 케이스
    # ==========================================================================
    def test_admin_question_detail_success(self) -> None:
        """[200] 어드민이 상세 조회 → 응답 필드 전체 검증"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 질문 기본 정보
        self.assertEqual(data["question_id"], self.question.id)
        self.assertEqual(data["title"], "어드민 상세 조회 테스트 제목")
        self.assertEqual(data["content"], "테스트 본문 내용입니다.")
        self.assertEqual(data["view_count"], 10)  # 어드민 조회 시 조회수 증가 없음
        self.assertTrue(data["has_answer"])

        # 이미지
        self.assertEqual(len(data["images"]), 2)
        self.assertIn({"id": self.img1.id, "img_url": "http://example.com/img1.jpg"}, data["images"])

        # 작성자 정보
        author = data["author"]
        self.assertEqual(author["nickname"], "수강생")
        self.assertEqual(author["course_generation"], "백엔드 개발 3기")

        # 답변 수
        self.assertEqual(len(data["answers"]), 5)

    def test_admin_question_detail_no_answers(self) -> None:
        """[200] 답변 없는 질문 → has_answer=false, answers=[]"""
        empty_q = Question.objects.create(
            author=self.student_user, category=self.cat_depth1, title="답변없는 질문", content="내용"
        )
        url = reverse("admin-qna-question-detail", kwargs={"question_id": empty_q.id})

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(url)
        data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(data["has_answer"])
        self.assertEqual(data["answers"], [])

    def test_admin_question_detail_role_titles(self) -> None:
        """[200] 다양한 역할의 답변 작성자 role_title, course_generation 검증"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url)
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

    # ==========================================================================
    # 실패 케이스
    # ==========================================================================
    def test_admin_question_detail_unauthorized(self) -> None:
        """[401] 비로그인"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()["error_detail"], ErrorMessages.UNAUTHORIZED_ADMIN_QUESTION_DETAIL.value)

    def test_admin_question_detail_forbidden_student(self) -> None:
        """[403] STUDENT 접근"""
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()["error_detail"], ErrorMessages.FORBIDDEN_ADMIN_QUESTION_DETAIL.value)

    def test_admin_question_detail_not_found(self) -> None:
        """[404] 존재하지 않는 question_id"""
        url = reverse("admin-qna-question-detail", kwargs={"question_id": 99999})
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()["error_detail"], ErrorMessages.NOT_FOUND_QUESTION.value)
