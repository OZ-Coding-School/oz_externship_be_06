from django.test import SimpleTestCase

from apps.exams.models import ExamQuestion
from apps.exams.services.grading import judge


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

    def test_multi_select_none_correct(self) -> None:
        q = ExamQuestion(
            type=ExamQuestion.TypeChoices.MULTI_SELECT,
            answer=[1, 2, 3],
            point=6,
        )

        self.assertEqual(judge(q, [4, 5]), 0)

    def test_multi_select_invalid_user_answer_type(self) -> None:
        q = ExamQuestion(
            type=ExamQuestion.TypeChoices.MULTI_SELECT,
            answer=[1, 2],
            point=4
        )

        self.assertEqual(judge(q, {"a": 1}), 0)

    def test_multi_select_single_correct_answer(self) -> None:
        q = ExamQuestion(
            type=ExamQuestion.TypeChoices.MULTI_SELECT,
            answer=1,
            point=4
        )

        self.assertEqual(judge(q, [1]), 4)

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
