from __future__ import annotations

from typing import Any, cast
import logging

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status

from apps.qna.constants import ErrorMessages
from apps.qna.exceptions.base import QnaBaseException
from apps.qna.models import Answer, AnswerImage, Question,  QuestionAIAnswer
from apps.qna.utils.model_types import User


class AnswerCommandService:
    """
    답변 관련 데이터 변경(CUD) 로직 처리 서비스
    """

    @staticmethod
    @transaction.atomic
    def create_answer(question_id: int, author: User, data: dict[str, Any]) -> Answer:
        """
        특정 질문에 대한 답변을 생성하고 이미지들을 일괄 저장

        - Args:
            question_id (int): 답변을 달 질문의 ID (PK)
            author (User): 답변 작성자 객체 (User Instance)
            data (dict): content(str) 및 image_urls(list)를 포함한 검증된 데이터
        - Returns:
            Answer: 생성된 답변 객체
        - Raises:
            QuestionNotFoundException: 질문이 존재하지 않을 경우
        """
        # 질문 조회
        try:
            question = Question.objects.select_for_update().get(id=question_id)
        except Question.DoesNotExist:
            raise QnaBaseException(detail=ErrorMessages.NOT_FOUND_QUESTION, status_code=status.HTTP_404_NOT_FOUND)

        # 답변 생성
        content = cast(str, data["content"])
        answer = Answer.objects.create(question=question, author=author, content=content)

        # 이미지 Bulk Create
        image_urls = data.get("image_urls", [])
        if image_urls:
            AnswerImage.objects.bulk_create([AnswerImage(answer=answer, img_url=url) for url in image_urls])

        return answer


logger = logging.getLogger("django")


class AIAnswerCommandService:
    """
    AI 답변 생성 및 비즈니스 로직 담당 서비스
    """

    @classmethod
    def generate_ai_answer(cls, question_id: int) -> QuestionAIAnswer:
        """
        특정 질문에 대한 AI 답변을 생성하고 저장함.
        이미 답변이 존재하는 경우 409 Conflict를 발생시킴.
        """
        # 1. 질문 존재 확인 (404)
        question = get_object_or_404(Question, id=question_id)

        # 2. 중복 답변 체크 (409)
        if QuestionAIAnswer.objects.filter(question=question).exists():
            raise QnaBaseException(
                detail=ErrorMessages.ALREADY_EXISTS_AI_GEN_ANSWER,
                status_code=status.HTTP_409_CONFLICT
            )

        # 3. AI 모델 호출 및 답변 생성 (Gemini API 호출부 가정)
        # 실제 환경에서는 별도의 AI 유틸리티나 태스크 큐(Celery)를 활용할 수 있습니다.
        try:
            generated_text = cls._call_ai_model(question.title, question.content)
            model_name = "gemini-2.5-pro"
        except Exception as e:
            logger.error(f"AI Generation Failed: {str(e)}")
            raise QnaBaseException(
                detail="AI 답변 생성 중 일시적인 오류가 발생했습니다.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        # 4. 답변 저장
        ai_answer = QuestionAIAnswer.objects.create(
            question=question,
            output=generated_text,
            using_model=model_name
        )

        # 5. 질문 상태 업데이트 (필요 시)
        question.is_ai_answered = True
        question.save(update_fields=["is_ai_answered"])

        return ai_answer

    @classmethod
    def _call_ai_model(cls, title: str, content: str) -> str:
        """
        실제 AI 모델(Gemini 등)에게 답변을 요청하는 내부 메서드
        (현재는 요구사항 예시 데이터를 반환하도록 구현)
        """
        # TODO: 실제 Google Gemini API 연동 로직 구현
        return "리스트는 수정 가능한 자료구조이며, 튜플은 수정이 불가능한 자료구조입니다. 리스트는 [], 튜플은 () 를 사용합니다."