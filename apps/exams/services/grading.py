from typing import Any

from django.db import transaction

from apps.exams.models import ExamQuestion, ExamSubmission


def judge(question: ExamQuestion, user_answer: Any) -> int:
    correct_answer = question.answer
    q_type = question.type
    point = question.point

    # OX 문제
    if q_type == ExamQuestion.TypeChoices.OX:
        return point if (str(user_answer).strip().upper() == str(correct_answer).strip().upper()) else 0

    # 주관식 단답형
    if q_type == ExamQuestion.TypeChoices.SHORT_ANSWER:
        return point if (str(user_answer).strip().lower() == str(correct_answer).strip().lower()) else 0

    # 객관식
    if q_type == ExamQuestion.TypeChoices.MULTI_SELECT:
        if isinstance(user_answer, (str, int)):
            user_answer = [user_answer]

        if not isinstance(user_answer, (list, tuple)):
            return 0

        if not isinstance(correct_answer, (list, tuple)):
            correct_answer = [correct_answer]

        correct_set = set(correct_answer)
        user_set = set(user_answer)

        matched = len(correct_set & user_set)
        total = len(correct_set)

        if total == 0:
            return 0

        return int(point * matched / total)  # 부분 점수 (소수점 버림)

    # 순서 정렬
    if q_type == ExamQuestion.TypeChoices.ORDERING:
        if not isinstance(user_answer, (list, tuple)):
            return 0

        if not isinstance(correct_answer, (list, tuple)):
            if isinstance(correct_answer, (str, int)):
                correct_answer = [correct_answer]
            else:
                return 0

        if len(user_answer) != len(correct_answer):
            return 0

        return point if list(user_answer) == list(correct_answer) else 0

    # 빈칸 채우기
    if q_type == ExamQuestion.TypeChoices.FILL_IN_BLANK:
        if isinstance(user_answer, (str, int)):
            user_answer = [user_answer]

        if not isinstance(user_answer, (list, tuple)):
            return 0

        if isinstance(correct_answer, (str, int)):
            correct_answer = [correct_answer]

        if not isinstance(correct_answer, (list, tuple)):
            return 0

        # if len(user_answer) != len(correct_answer):
        #     return 0

        matched = 0
        total = len(correct_answer)

        for ua, ca in zip(user_answer, correct_answer):
            if str(ua).strip().lower() == str(ca).strip().lower():
                matched += 1

        if total == 0:
            return 0

        return int(point * matched / total)

    return 0


@transaction.atomic
def grade_submission(submission: ExamSubmission) -> None:
    # 제출자 답안
    answers_list = submission.answers_json or []

    # 리스트 → dict 변환: {qid: submitted_answer}
    answers = {}

    for ans in answers_list:
        if not isinstance(ans, dict):
            continue
        question_id = ans.get("question_id")
        if question_id is None:
            continue

        qid = str(ans.get("question_id"))
        submitted_answer = ans.get("submitted_answer")
        if qid is not None:
            answers[qid] = submitted_answer

    # 해당 시험의 모든 문제 가져오기
    questions = ExamQuestion.objects.filter(exam=submission.deployment.exam).only("id", "type", "answer", "point")

    total_score = 0
    correct_count = 0

    # 문제별 채점
    for question in questions:
        qid = str(question.id)

        if qid not in answers:
            continue

        # 정답과 학생답안을 비교해서 점수 계산
        earned = judge(question, answers[qid])
        total_score += earned

        # 완전히 맞춘 문제만 카운트 누적 => 부분점수 받은 문제는 카운트 X
        if earned == question.point:
            correct_count += 1

    submission.score = total_score
    submission.correct_answer_count = correct_count
    submission.save(update_fields=["score", "correct_answer_count"])
