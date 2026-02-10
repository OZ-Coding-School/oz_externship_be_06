from typing import Any

from django.db import transaction
from rest_framework import status

from apps.qna.constants import ErrorMessages
from apps.qna.exceptions import QnaBaseException
from apps.qna.models import Question, QuestionCategory, QuestionImage
from apps.qna.utils.content_parser import ContentParser
from apps.qna.utils.model_types import User

# ==============================================================================
# QuestionCommandService
#   - create_question: 질문 생성
#   - update_question: 질문 수정
# ==============================================================================


class QuestionCommandService:
    """
    - create_question: 질문 생성
    - update_question: 질문 수정
    """

    @staticmethod
    @transaction.atomic
    def create_question(author: User, data: dict[str, Any]) -> Question:
        """
        새로운 질문 생성
        - Args:
            author (User): 질문 작성자 객체 (User Instance)
            data (dict): title(str), content(str), category_id(int)를 포함한 검증된 데이터
        - Returns:
            Question: 생성된 질문 객체
        - Raises:
            QnaBaseException(404): 카테고리가 존재하지 않을 경우
        """

        category_id = data.pop("category_id")

        try:
            category = QuestionCategory.objects.get(id=category_id)
        except QuestionCategory.DoesNotExist:
            raise QnaBaseException(detail=ErrorMessages.NOT_FOUND_CATEGORY, status_code=status.HTTP_404_NOT_FOUND)

        question = Question.objects.create(author=author, category=category, **data)

        if "content" in data:
            # content에서 새 이미지 URL 리스트 추출 (중복 제거를 위해 Set 사용)
            image_urls = set(ContentParser.extract_all_image_urls(question.content))

            # 이미지 생성
            if image_urls:
                QuestionImage.objects.bulk_create([QuestionImage(question=question, img_url=url) for url in image_urls])

        return question

    @staticmethod
    @transaction.atomic
    def update_question(question_id: int, user: User, data: dict[str, Any]) -> Question:
        """
        질문을 수정하고 이미지들을 업데이트
        - Args:
            question_id (int): 수정할 질문의 ID (PK)
            user (User): 수정 요청한 사용자 객체
            data (dict): title(str), content(str), category_id(int)를 포함한 검증된 데이터
        - Returns:
            Question: 수정된 질문 객체
        - Raises:
            QnaBaseException(404): 질문이 존재하지 않을 경우
            QnaBaseException(403): 본인이 작성한 질문이 아닐 경우
        """
        # 질문 조회
        try:
            question = Question.objects.select_for_update().get(id=question_id)
        except Question.DoesNotExist:
            raise QnaBaseException(detail=ErrorMessages.NOT_FOUND_QUESTION, status_code=status.HTTP_404_NOT_FOUND)

        # 작성자 확인
        if question.author_id != user.id:
            raise QnaBaseException(
                detail=ErrorMessages.FORBIDDEN_QUESTION_UPDATE, status_code=status.HTTP_403_FORBIDDEN
            )

        # 필드 업데이트
        update_fields = ["updated_at"]

        if "title" in data:
            if not isinstance(data["title"], str):
                raise QnaBaseException(detail="제목은 문자열이어야 합니다.")
            question.title = data["title"]
            update_fields.append("title")

        if "content" in data:
            if not isinstance(data["content"], str):
                raise QnaBaseException(detail="내용은 문자열이어야 합니다.")
            question.content = data["content"]
            update_fields.append("content")

        if "category_id" in data:
            category_id = data["category_id"]
            if not isinstance(category_id, int):
                raise QnaBaseException(detail="카테고리 ID는 숫자여야 합니다.")
            try:
                question.category = QuestionCategory.objects.get(id=category_id)
                update_fields.append("category")
            except QuestionCategory.DoesNotExist:
                raise QnaBaseException(detail=ErrorMessages.NOT_FOUND_CATEGORY, status_code=status.HTTP_404_NOT_FOUND)

        question.save(update_fields=update_fields)

        # 이미지 효율적 동기화 (Diffing)
        if "content" in data:
            # content에서 새 이미지 URL 리스트 추출 (중복 제거를 위해 Set 사용)
            new_image_urls = set(ContentParser.extract_all_image_urls(question.content))

            # 현재 question_id의 기존 이미지 URL 리스트 조회
            existing_images = QuestionImage.objects.filter(question=question)
            existing_image_urls = set(existing_images.values_list("img_url", flat=True))

            # 기존에는 있었지만 새 목록에는 없는 URL (DB에서 제거)
            urls_to_delete = existing_image_urls - new_image_urls
            if urls_to_delete:
                QuestionImage.objects.filter(question=question, img_url__in=urls_to_delete).delete()

            # 새 목록에는 있지만 기존 DB에는 없는 URL (생성)
            urls_to_create = new_image_urls - existing_image_urls
            if urls_to_create:
                QuestionImage.objects.bulk_create(
                    [QuestionImage(question=question, img_url=url) for url in urls_to_create]
                )

            # 새 목록과 기존 목록 모두 있는 URL은 아무 작업도 하지 않음

        return question
