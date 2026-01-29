from datetime import date

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase
from django.utils import timezone

from apps.courses.models import Cohort, Course, Subject
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

        self.assertEqual(judge(q, [1, 2, 4]), 4)

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
            is_active=True,
        )

        course = Course.objects.create(name="테스트 강좌", tag="TST")

        subject = Subject.objects.create(
            title="테스트과목",
            course=course,
            number_of_days=1,
            number_of_hours=1,
        )
        self.exam = Exam.objects.create(title="시험", subject=subject)
        cohort = Cohort.objects.create(
            course=course,
            number=1,
            max_student=1,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 1),
        )
        self.deployment = ExamDeployment.objects.create(
            exam=self.exam,
            cohort=cohort,
            duration_time=60,
            access_code="ABC123",
            open_at=timezone.now(),
            close_at=timezone.now(),
            status=ExamDeployment.StatusChoices.ACTIVATED,
            questions_snapshot_json=[],
        )

        # 문제 생성
        self.q1 = ExamQuestion.objects.create(
            exam=self.exam,
            question="OX 문제",
            type=ExamQuestion.TypeChoices.OX,
            answer="O",
            point=5,
        )
        self.q2 = ExamQuestion.objects.create(
            exam=self.exam,
            question="빈칸 문제",
            type=ExamQuestion.TypeChoices.FILL_IN_BLANK,
            answer=["a", "b"],
            point=10,
        )
        self.q3 = ExamQuestion.objects.create(
            exam=self.exam,
            question="객관식 문제",
            type=ExamQuestion.TypeChoices.MULTI_SELECT,
            answer=["1", "2"],
            point=5,
        )
        self.q4 = ExamQuestion.objects.create(
            exam=self.exam,
            question="단답형 문제",
            type=ExamQuestion.TypeChoices.SHORT_ANSWER,
            answer="hello",
            point=5,
        )
        self.q5 = ExamQuestion.objects.create(
            exam=self.exam,
            question="순서 정렬 문제",
            type=ExamQuestion.TypeChoices.ORDERING,
            answer=["first", "second"],
            point=10,
        )

        # 제출 생성
        self.submission = ExamSubmission.objects.create(
            submitter=self.user,
            deployment=self.deployment,
            started_at=timezone.now(),
            answers_json=[],
        )

    # 기본 edge case
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

    def test_grade_submission_with_nonexistent_question_id(self) -> None:
        # 시험에 존재하지 않는 문제 ID -> 무시하고 0점
        self.submission.answers_json = [{"question_id": 9999, "submitted_answer": "O"}]
        grade_submission(self.submission)
        self.assertEqual(self.submission.score, 0)
        self.assertEqual(self.submission.correct_answer_count, 0)

    # 실제 채점 점수 검증
    def test_grade_submission_full_score(self) -> None:
        # 모든 문제 정답 → total_score 합, correct_count 전체
        self.submission.answers_json = [
            {"question_id": self.q1.id, "submitted_answer": "O"},
            {"question_id": self.q2.id, "submitted_answer": ["a", "b"]},
            {"question_id": self.q3.id, "submitted_answer": ["1", "2"]},
            {"question_id": self.q4.id, "submitted_answer": "hello"},
            {"question_id": self.q5.id, "submitted_answer": ["first", "second"]},
        ]
        grade_submission(self.submission)
        self.assertEqual(self.submission.score, 5 + 10 + 5 + 5 + 10)
        self.assertEqual(self.submission.correct_answer_count, 5)

    def test_grade_submission_partial_score(self) -> None:
        # 부분 정답 → 점수 반영, correct_count는 부분점수는 포함하지 않고 완전히 맞춘 문제만
        self.submission.answers_json = [
            {"question_id": self.q1.id, "submitted_answer": "X"},  # 오답
            {"question_id": self.q2.id, "submitted_answer": ["a", "c"]},  # 부분점수
            {"question_id": self.q3.id, "submitted_answer": ["1"]},  # 부분점수
            {"question_id": self.q4.id, "submitted_answer": "HELLO"},  # 대소문자 O
            {"question_id": self.q5.id, "submitted_answer": ["second", "first"]},  # 순서 틀림
        ]
        grade_submission(self.submission)
        # judge 함수 기준으로 부분점수 계산
        self.assertEqual(self.submission.score, 0 + 5 + 2 + 5 + 0)
        self.assertEqual(self.submission.correct_answer_count, 1)

    # 추가 edge case
    def test_grade_submission_unknown_question_type(self) -> None:
        # 알 수 없는 문제 타입 → 점수 0 처리
        self.q1.type = "UNKNOWN_TYPE"
        self.q1.save()  # db에서 문제를 가져오기 때문에 바뀐 타입을 save() 해야함
        self.submission.answers_json = [{"question_id": self.q1.id, "submitted_answer": "O"}]
        grade_submission(self.submission)
        self.assertEqual(self.submission.score, 0)
        self.assertEqual(self.submission.correct_answer_count, 0)

    def test_fill_in_blank_unknown_type(self) -> None:
        self.q2.type = "UNKNOWN_TYPE"
        self.q2.save()
        self.submission.answers_json = [{"question_id": self.q2.id, "submitted_answer": ["a", "b"]}]
        grade_submission(self.submission)
        self.assertEqual(self.submission.score, 0)
        self.assertEqual(self.submission.correct_answer_count, 0)

    def test_multi_select_unknown_type(self) -> None:
        self.q3.type = "UNKNOWN_TYPE"
        self.q3.save()
        self.submission.answers_json = [{"question_id": self.q3.id, "submitted_answer": ["1", "2"]}]
        grade_submission(self.submission)
        self.assertEqual(self.submission.score, 0)
        self.assertEqual(self.submission.correct_answer_count, 0)

    def test_short_answer_unknown_question_type(self) -> None:
        self.q4.type = "UNKNOWN_TYPE"
        self.q4.save()  # DB에 반영
        self.submission.answers_json = [{"question_id": self.q4.id, "submitted_answer": "hello"}]
        grade_submission(self.submission)
        self.assertEqual(self.submission.score, 0)
        self.assertEqual(self.submission.correct_answer_count, 0)

    def test_ordering_unknown_question_type(self) -> None:
        self.q5.type = "UNKNOWN_TYPE"
        self.q5.save()  # DB에 반영
        self.submission.answers_json = [{"question_id": self.q5.id, "submitted_answer": ["first", "second"]}]
        grade_submission(self.submission)
        self.assertEqual(self.submission.score, 0)
        self.assertEqual(self.submission.correct_answer_count, 0)

    def test_fill_in_blank_insufficient_answers(self) -> None:
        # 빈칸 문제 답 부족 → 부분점수
        self.submission.answers_json = [{"question_id": self.q2.id, "submitted_answer": ["a"]}]
        grade_submission(self.submission)
        self.assertEqual(self.submission.score, 5)
        self.assertEqual(self.submission.correct_answer_count, 0)

    def test_multi_select_with_wrong_selection(self) -> None:
        # MULTI_SELECT 일부만 맞춰도 -> 부분점수
        self.submission.answers_json = [{"question_id": self.q3.id, "submitted_answer": ["1", "3"]}]
        grade_submission(self.submission)
        self.assertEqual(self.submission.score, 2)
        self.assertEqual(self.submission.correct_answer_count, 0)
