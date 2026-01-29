import logging
from typing import Any

from django.db import transaction
from django.db.models import Count, F, Q, QuerySet

from apps.qna.exceptions.base_e import QnaBaseException
from apps.qna.exceptions.question_e import QuestionNotFoundException
from apps.qna.models import Question
from apps.qna.utils.constants import ErrorMessages

logger = logging.getLogger(__name__)


class QuestionQueryService:
    """
    질문 데이터 조회(Read) 로직 처리 서비스
    """

    @staticmethod
    def get_question_list(filters: dict[str, Any]) -> QuerySet[Question]:
        """
        검색, 필터링, 정렬 로직을 수행하고 질문 목록을 반환

        Args:
            filters (dict): 검색어(search_keyword), 카테고리(category_id), 답변상태(answer_status), 정렬(sort) 등의 필터 조건

        Returns:
            QuerySet[Question]: 필터링된 질문 QuerySet

        Raises:
            QuestionNotFoundException: 조건에 맞는 질문이 하나도 없을 경우 (404)
            QuestionBaseException: 기타 조회 처리 오류 시
        """
        try:
            queryset = Question.objects.select_related("author", "category__parent__parent").annotate(
                answer_count=Count("answers")
            )

            search_keyword = filters.get("search_keyword")
            if search_keyword:
                queryset = queryset.filter(Q(title__icontains=search_keyword) | Q(content__icontains=search_keyword))

            category_id = filters.get("category_id")
            if category_id:
                queryset = queryset.filter(category_id=category_id)

            answer_status = filters.get("answer_status")
            if answer_status == "waiting":
                queryset = queryset.filter(answer_count=0)
            elif answer_status == "answered":
                queryset = queryset.filter(answer_count__gt=0)

            sort = filters.get("sort")
            if sort == "latest":
                queryset = queryset.order_by("-created_at")
            elif sort == "oldest":
                queryset = queryset.order_by("created_at")
            elif sort == "most_views":
                queryset = queryset.order_by("-view_count")

            if not queryset.exists():
                raise QuestionNotFoundException(detail=ErrorMessages.NOT_FOUND_QUESTION_LIST)
            return queryset

        except QuestionNotFoundException:
            raise
        except Exception as e:
            logger.error(f"{ErrorMessages.INVALID_QUESTION_DETAIL}\nMessage: {str(e)}", exc_info=True)
            raise QnaBaseException(detail=ErrorMessages.INVALID_QUESTION_DETAIL)

    @staticmethod
    @transaction.atomic
    def get_question_detail(question_id: int) -> Question:
        """
        질문 상세 정보를 조회하고 조회수를 1 증가

        Args:
            question_id (int): 조회할 질문의 ID (PK)

        Returns:
            Question: 상세 정보를 포함한 질문 객체 (Author, Category, Answers, Comments 등 포함)

        Raises:
            QuestionNotFoundException: 질문이 존재하지 않을 경우
            QuestionBaseException: 기타 조회 처리 오류 시
        """
        try:
            # 조회수 증가
            Question.objects.filter(id=question_id).update(view_count=F("view_count") + 1)

            # 질문 조회 및 관련 데이터 로딩
            question = (
                Question.objects.select_related("author", "category__parent__parent")
                .prefetch_related("images", "answers__author", "answers__comments__author")
                .get(id=question_id)
            )

            return question

        except Question.DoesNotExist:
            raise QuestionNotFoundException(detail=ErrorMessages.NOT_FOUND_QUESTION)
        except Exception as e:
            logger.error(f"{ErrorMessages.INVALID_QUESTION_DETAIL} ID: {question_id}\nMessage: {str(e)}", exc_info=True)
            raise QnaBaseException(detail=ErrorMessages.INVALID_QUESTION_DETAIL)
