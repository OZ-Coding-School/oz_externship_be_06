from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.qna.models import Question, QuestionCategory
from apps.qna.models.answer import Answer
from apps.qna.tests.factories import create_admin_user, create_student_user
from apps.users.models import User


class AdminQuestionListAPITest(APITestCase):
    """
    어드민 질의응답 목록 조회 API (GET) 테스트
    - 성공 케이스
        - 전체 목록 조회
        - 검색어 필터링
        - 카테고리 필터링
        - 답변 상태 필터링 (waiting / answered)
        - 정렬 (latest / oldest / most_views)
        - 페이지네이션 동작 확인
    - 실패 케이스
        - 401 Unauthorized: 로그인하지 않은 유저
        - 403 Forbidden: 스태프/관리자가 아닌 유저
    """

    admin_user: User
    student_user: User
    cat_large: QuestionCategory
    cat_medium: QuestionCategory
    cat_small: QuestionCategory
    question1: Question
    question2: Question
    question3: Question
    url: str

    @classmethod
    def setUpTestData(cls) -> None:
        # 유저 생성
        cls.admin_user = create_admin_user()
        cls.student_user = create_student_user()

        # 카테고리 생성
        cls.cat_large = QuestionCategory.objects.create(name="백엔드")
        cls.cat_medium = QuestionCategory.objects.create(name="웹프레임워크", parent=cls.cat_large)
        cls.cat_small = QuestionCategory.objects.create(name="Django", parent=cls.cat_medium)

        # 질문 생성
        cls.question1 = Question.objects.create(
            title="Django ORM 역참조는 어떻게 사용하나요?",
            content="ForeignKey에 related_name을 지정하면 역참조가 가능합니다.",
            category=cls.cat_small,
            author=cls.student_user,
            view_count=132,
        )

        cls.question2 = Question.objects.create(
            title="Python 리스트 컴프리헨션 질문",
            content="리스트 컴프리헨션 사용법이 궁금합니다.",
            category=cls.cat_small,
            author=cls.student_user,
            view_count=50,
        )

        cls.question3 = Question.objects.create(
            title="REST API 설계 방법",
            content="RESTful API를 어떻게 설계해야 하나요?",
            category=cls.cat_medium,
            author=cls.student_user,
            view_count=200,
        )

        # question1에 답변 추가
        Answer.objects.create(
            question=cls.question1,
            author=cls.admin_user,
            content="post.comment_set.all() 로 접근하면 됩니다.",
        )

        # URL
        cls.url = reverse("admin-qna-questions")

    # ==========================================================================
    # 성공 케이스
    # ==========================================================================
    def test_list_all_questions_success(self) -> None:
        """[200] 전체 목록 조회"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url)
        res_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(res_data["total_count"], 3)
        self.assertEqual(len(res_data["questions"]), 3)

        # 응답 구조 확인
        first_question = res_data["questions"][0]
        self.assertIn("question_id", first_question)
        self.assertIn("title", first_question)
        self.assertIn("category_path", first_question)
        self.assertIn("content_preview", first_question)
        self.assertIn("nickname", first_question)
        self.assertIn("view_count", first_question)
        self.assertIn("has_answer", first_question)
        self.assertIn("created_at", first_question)
        self.assertIn("updated_at", first_question)

    def test_search_by_keyword(self) -> None:
        """[200] 검색어로 조회 (제목 + 내용)"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url, {"search_keyword": "ORM"})
        res_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(res_data["total_count"], 1)
        self.assertEqual(res_data["questions"][0]["title"], "Django ORM 역참조는 어떻게 사용하나요?")

    def test_filter_by_category_id(self) -> None:
        """[200] 카테고리 ID로 필터링"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url, {"category_id": self.cat_small.id})
        res_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # cat_small에 속한 질문: question1, question2
        self.assertEqual(res_data["total_count"], 2)

    def test_filter_by_answer_status_y(self) -> None:
        """[200] 답변 있는 질문만 조회 (answer_status=answered)"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url, {"answer_status": "answered"})
        res_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(res_data["total_count"], 1)
        self.assertTrue(res_data["questions"][0]["has_answer"])

    def test_filter_by_answer_status_n(self) -> None:
        """[200] 답변 없는 질문만 조회 (answer_status=waiting)"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url, {"answer_status": "waiting"})
        res_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(res_data["total_count"], 2)
        for q in res_data["questions"]:
            self.assertFalse(q["has_answer"])

    def test_sort_by_oldest(self) -> None:
        """[200] 오래된순 정렬"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url, {"sort": "oldest"})
        res_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        questions = res_data["questions"]
        # 오래된순이면 첫 번째가 가장 먼저 생성된 question1
        self.assertEqual(questions[0]["question_id"], self.question1.id)

    def test_sort_by_most_views(self) -> None:
        """[200] 조회수 많은순 정렬"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url, {"sort": "most_views"})
        res_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        questions = res_data["questions"]
        # 조회수: question3(200) > question1(132) > question2(50)
        self.assertEqual(questions[0]["question_id"], self.question3.id)

    def test_category_path_format(self) -> None:
        """[200] category_path가 '대분류 > 중분류 > 소분류' 형태"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url, {"category_id": self.cat_small.id})
        res_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for q in res_data["questions"]:
            self.assertEqual(q["category_path"], "백엔드 > 웹프레임워크 > Django")

    def test_pagination(self) -> None:
        """[200] 페이지네이션 동작"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url, {"page": 1, "size": 2})
        res_data = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(res_data["page"], 1)
        self.assertEqual(res_data["size"], 2)
        self.assertEqual(res_data["total_count"], 3)
        self.assertEqual(len(res_data["questions"]), 2)

    # ==========================================================================
    # 실패 케이스
    # ==========================================================================
    def test_unauthorized(self) -> None:
        """[401] 로그인하지 않은 경우"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_forbidden_student(self) -> None:
        """[403] 수강생이 요청한 경우"""
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
