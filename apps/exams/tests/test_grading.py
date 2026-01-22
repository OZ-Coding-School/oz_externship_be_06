from datetime import date

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from django.utils import timezone

from apps.courses.models import Course
from apps.exams.models import Exam, ExamDeployment, ExamQuestion, ExamSubmission
from apps.exams.services.grading import grade_submission, judge

User = get_user_model()


class JudgeLogicTests(SimpleTestCase):
    def test_ox_correct(self) -> None:
        q = ExamQuestion(type=ExamQuestion.TypeChoices.OX, answer="O", point=5)

        score = judge(q, "O")

        self.assertEqual(score, 5)

    def test_ox_wrong(self) -> None:
        q = ExamQuestion(type=ExamQuestion.TypeChoices.OX, answer="O", point=5)

        self.assertEqual(judge(q, "X"), 0)

    def test_short_answer_correct(self) -> None:
        q = ExamQuestion(type=ExamQuestion.TypeChoices.SHORT_ANSWER, answer="Django", point=5)

        self.assertEqual(judge(q, "django"), 5)

    def test_short_answer_wrong(self) -> None:
        q = ExamQuestion(type=ExamQuestion.TypeChoices.SHORT_ANSWER, answer="Django", point=5)

        self.assertEqual(judge(q, "Flask"), 0)

    def test_multi_select_all_correct(self) -> None:
        q = ExamQuestion(
            type=ExamQuestion.TypeChoices.MULTI_SELECT,
            answer=[1, 2, 3],
            point=6,
        )

        self.assertEqual(judge(q, [1, 2, 3]), 6)

    def test_multi_select_partial_correct(self) -> None:
        q = ExamQuestion(
            type=ExamQuestion.TypeChoices.MULTI_SELECT,
            answer=[1, 2, 3],
            point=6,
        )

        self.assertEqual(judge(q, [1, 2]), 4)

    def test_multi_select_with_wrong_selection(self) -> None:
        q = ExamQuestion(type=ExamQuestion.TypeChoices.MULTI_SELECT, answer=[1, 2, 3], point=6)

        self.assertEqual(judge(q, [1, 2, 4]), 0)

    def test_multi_select_none_correct(self) -> None:
        q = ExamQuestion(
            type=ExamQuestion.TypeChoices.MULTI_SELECT,
            answer=[1, 2, 3],
            point=6,
        )

        self.assertEqual(judge(q, [4, 5]), 0)

    def test_multi_select_invalid_user_answer_type(self) -> None:
        q = ExamQuestion(type=ExamQuestion.TypeChoices.MULTI_SELECT, answer=[1, 2], point=4)

        self.assertEqual(judge(q, {"a": 1}), 0)

    def test_multi_select_single_correct_answer(self) -> None:
        q = ExamQuestion(type=ExamQuestion.TypeChoices.MULTI_SELECT, answer=1, point=4)

        self.assertEqual(judge(q, [1]), 4)

    def test_multi_select_single_wrong_answer(self) -> None:
        q = ExamQuestion(type=ExamQuestion.TypeChoices.MULTI_SELECT, answer=1, point=4)

        self.assertEqual(judge(q, [3]), 0)

    def test_ordering_correct(self) -> None:
        q = ExamQuestion(
            type=ExamQuestion.TypeChoices.ORDERING,
            answer=["a", "b", "c"],
            point=5,
        )

        self.assertEqual(judge(q, ["a", "b", "c"]), 5)

    def test_ordering_wrong_order(self) -> None:
        q = ExamQuestion(
            type=ExamQuestion.TypeChoices.ORDERING,
            answer=["a", "b", "c"],
            point=5,
        )

        self.assertEqual(judge(q, ["b", "a", "c"]), 0)

    def test_ordering_length_mismatch(self) -> None:
        q = ExamQuestion(
            type=ExamQuestion.TypeChoices.ORDERING,
            answer=["a", "b", "c"],
            point=5,
        )

        self.assertEqual(judge(q, ["a", "b"]), 0)

    def test_fill_in_blank_all_correct(self) -> None:
        q = ExamQuestion(
            type=ExamQuestion.TypeChoices.FILL_IN_BLANK,
            answer=["Django", "Python"],
            point=10,
        )

        self.assertEqual(judge(q, [" django ", "python"]), 10)

    def test_fill_in_blank_partial_correct(self) -> None:
        q = ExamQuestion(
            type=ExamQuestion.TypeChoices.FILL_IN_BLANK,
            answer=["Django", "Python"],
            point=10,
        )

        self.assertEqual(judge(q, ["django", "java"]), 5)

    def test_fill_in_blank_all_wrong(self) -> None:
        q = ExamQuestion(
            type=ExamQuestion.TypeChoices.FILL_IN_BLANK,
            answer=["Django", "Python"],
            point=10,
        )

        self.assertEqual(judge(q, ["java", "spring"]), 0)

    def test_fill_in_blank_single_value(self) -> None:
        q = ExamQuestion(type=ExamQuestion.TypeChoices.FILL_IN_BLANK, answer="django", point=5)
        self.assertEqual(judge(q, "Django"), 5)


class GradeSubmissionTests(TestCase):
    def setUp(self) -> None:
        # 사용자, 시험, 배포, 제출 생성 (간단화)
        self.user = User.objects.create_user(
            email="test@test.com",
            password="1234",
            birthday=date(2000, 1, 1),
            gender=User.Gender.MALE,
            nickname="테스트유저",
            name="테스트 이름",
            phone_number="010-0000-0000",
        )

        course = Course.objects.create(name="테스트 강좌", tag="TST")
        self.exam = Exam.objects.create(title="시험", subject_id=1)
        self.deployment = ExamDeployment.objects.create(
            exam=self.exam,
            cohort_id=1,
            duration_time=60,
            access_code="ABC123",
            open_at=timezone.now(),
            close_at=timezone.now(),
            status=ExamDeployment.StatusChoices.ACTIVATED,
        )
        self.submission = ExamSubmission.objects.create(
            submitter=self.user,
            deployment=self.deployment,
            started_at=timezone.now(),
            answers_json=[],
        )

    def test_grade_submission_with_none_answers(self) -> None:
        # answers_json=None → 에러 없이 점수 0
        self.submission.answers_json = None
        grade_submission(self.submission)
        self.assertEqual(self.submission.score, 0)
        self.assertEqual(self.submission.correct_answer_count, 0)

    def test_grade_submission_with_invalid_answer_type(self) -> None:
        # answers_json에 dict가 아닌 타입 → 안전하게 0점 처리
        self.submission.answers_json = ["invalid"]
        grade_submission(self.submission)
        self.assertEqual(self.submission.score, 0)
        self.assertEqual(self.submission.correct_answer_count, 0)
