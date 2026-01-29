import logging
from typing import Any, cast

from django.db import transaction

from apps.qna.exceptions.base_e import QnaBaseException
from apps.qna.exceptions.question_e import QuestionNotFoundException
from apps.qna.models import Answer, AnswerImage, Question
from apps.qna.utils.constants import ErrorMessages
from apps.qna.utils.model_types import User

logger = logging.getLogger(__name__)


class AnswerCommandService:
    """
    답변 관련 데이터 변경(CUD) 로직 처리 서비스
    """

    @staticmethod
    @transaction.atomic
    def create_answer(question_id: int, author: User, data: dict[str, Any]) -> Answer:
        """
        특정 질문에 대한 답변을 생성하고 이미지들을 일괄 저장

        Args:
            question_id (int): 답변을 달 질문의 ID (PK)
            author (User): 답변 작성자 객체 (User Instance)
            data (dict): content(str) 및 image_urls(list)를 포함한 검증된 데이터

        Returns:
            Answer: 생성된 답변 객체

        Raises:
            QuestionNotFoundException: 질문이 존재하지 않을 경우
            QuestionBaseException: 기타 등록 처리 오류 시
        """
        try:
            # 질문 조회
            try:
                question = Question.objects.select_for_update().get(id=question_id)
            except Question.DoesNotExist:
                raise QuestionNotFoundException(detail="해당 질문을 찾을 수 없습니다.")

            # 답변 생성
            content = cast(str, data["content"])
            answer = Answer.objects.create(question=question, author=author, content=content)

            # 이미지 Bulk Create
            image_urls = data.get("image_urls", [])
            if image_urls:
                AnswerImage.objects.bulk_create([AnswerImage(answer=answer, img_url=url) for url in image_urls])

            return answer

        except QuestionNotFoundException:
            raise
        except Exception as e:
            logger.error(f"{ErrorMessages.INVALID_ANSWER_CREATE} ID: {question_id}\nMessage: {str(e)}", exc_info=True)
            raise QnaBaseException(detail=ErrorMessages.INVALID_ANSWER_CREATE)
