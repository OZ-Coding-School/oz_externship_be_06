from __future__ import annotations

import logging
import os
from typing import Any, cast

import google.generativeai as genai
from django.db import transaction
from google.generativeai.types import RequestOptions
from rest_framework import status

from apps.qna.constants import ErrorMessages
from apps.qna.exceptions.base import QnaBaseException
from apps.qna.models import Answer, AnswerImage, Question, QuestionAIAnswer
from apps.qna.utils.config_ai_model import AIModelConfig
from apps.qna.utils.model_types import User

logger = logging.getLogger("django")


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


class AIAnswerCommandService:
    """
    AI 답변 생성 및 비즈니스 로직 담당 서비스
    """

    @classmethod
    @transaction.atomic
    def generate_ai_answer(cls, question_id: int, using_model: str) -> QuestionAIAnswer:
        """
        특정 질문에 대한 AI 답변을 생성하고 저장함.
        이미 답변이 존재하는 경우 409 Conflict를 발생시킴.

        Args:
            question_id: 질문 ID
            using_model: 사용할 AI 모델 타입 (Gemini 또는 GPT)

        Returns:
            QuestionAIAnswer: 생성된 AI 답변 객체
        """
        # 질문 존재 확인 (404)
        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            raise QnaBaseException(
                detail=ErrorMessages.NOT_FOUND_AI_QUESTION,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # 중복 답변 체크 (409)
        if QuestionAIAnswer.objects.filter(question=question).exists():
            raise QnaBaseException(
                detail=ErrorMessages.CONFLICT_AI_GEN_ANSWER,
                status_code=status.HTTP_409_CONFLICT,
            )

        # 모델 타입에서 세부 모델명 조회
        try:
            model_name = AIModelConfig.get_model_name(using_model)
        except ValueError:
            logger.error(f"Invalid model type: {using_model}")
            raise QnaBaseException(
                detail=ErrorMessages.INVALID_AI_REQUEST,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # AI 모델 호출 및 답변 생성
        try:
            generated_text = cls._call_ai_model(
                title=question.title,
                content=question.content,
                model_name=model_name,
            )
        except Exception as e:
            logger.error(f"AI Generation Failed: {str(e)}")
            raise QnaBaseException(
                detail=ErrorMessages.FAILED_AI_GEN_ANSWER,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # 답변 저장 (DB에는 모델 타입 저장: Gemini, GPT)
        ai_answer = QuestionAIAnswer.objects.create(
            question=question,
            output=generated_text,
            using_model=using_model,
        )

        # 질문 상태 업데이트
        question.is_ai_answered = True
        question.save(update_fields=["is_ai_answered"])

        return ai_answer

    @classmethod
    def _call_ai_model(cls, title: str, content: str, model_name: str) -> str:
        """
        AI 모델 API를 호출하여 질문에 대한 답변을 생성합니다.

        Args:
            title: 질문 제목
            content: 질문 본문 내용
            model_name: 사용할 세부 모델명 (gemini-2.5-pro, gpt-4o 등)

        Returns:
            str: AI가 생성한 답변 텍스트

        Raises:
            ValueError: API 키가 설정되지 않은 경우
            Exception: API 호출 실패 시
        """
        # Gemini 모델인 경우
        if model_name.startswith("gemini"):
            return cls._call_gemini_api(title, content, model_name)

        # GPT 모델인 경우
        if model_name.startswith("gpt"):
            return cls._call_openai_api(title, content, model_name)

        raise ValueError(f"지원하지 않는 세부 모델입니다: {model_name}")

    @classmethod
    def _call_gemini_api(cls, title: str, content: str, model_name: str) -> str:
        """
        Google Gemini API를 호출합니다.
        """
        AIModelConfig.ensure_gemini_configured()

        model = genai.GenerativeModel(  # type: ignore[attr-defined]
            model_name=model_name,
            generation_config=genai.GenerationConfig(  # type: ignore[attr-defined]
                temperature=0.7,
                top_p=0.9,
                max_output_tokens=1024,
            ),
        )

        prompt = cls._build_prompt(title, content)

        response = model.generate_content(
            prompt,
            request_options=RequestOptions(timeout=AIModelConfig.REQUEST_TIMEOUT),
        )

        if not response.text:
            logger.warning("Gemini API가 빈 응답을 반환했습니다.")
            raise ValueError("AI 응답이 비어있습니다.")

        return cast(str, response.text)

    @classmethod
    def _call_openai_api(cls, title: str, content: str, model_name: str) -> str:
        """
        OpenAI API를 호출합니다.
        """
        # 현재는 Gemini만 지원하므로 예외 발생
        raise NotImplementedError("OpenAI API 연동은 아직 구현되지 않았습니다.")

    @staticmethod
    def _build_prompt(title: str, content: str) -> str:
        """
        AI 모델에 전달할 프롬프트를 구성합니다.

        Args:
            title: 질문 제목
            content: 질문 본문

        Returns:
            str: 구성된 프롬프트 문자열
        """
        return f"""당신은 오즈코딩스쿨의 학습 도우미 AI입니다.
수강생의 프로그래밍 관련 질문에 친절하고 정확하게 답변해주세요.

[답변 가이드라인]
- 명확하고 이해하기 쉬운 설명을 제공하세요
- 필요한 경우 간단한 코드 예시를 포함하세요
- 답변은 한국어로 작성하세요

[질문 제목]
{title}

[질문 내용]
{content}

[답변]"""
