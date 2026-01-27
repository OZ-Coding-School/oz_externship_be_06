from typing import Any

from django.db.models import Count, F, Q, QuerySet

from apps.qna.exceptions.question_exception import (
    QuestionBaseException,
    QuestionNotFoundException,
)
from apps.qna.models import Question


class QuestionQueryService:
    """
    질문 데이터 조회(Read) 로직 처리 서비스
    """

    @staticmethod
    def get_question_list(filters: dict[str, Any]) -> QuerySet[Question]:
        """검색, 필터링, 정렬 로직을 수행하여 QuerySet을 반환"""
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
                queryset = queryset.order_by("-view_count")  # 조회수 내림차순

            if not queryset.exists():
                raise QuestionNotFoundException()

            return queryset

        except QuestionNotFoundException:
            raise
        except Exception as e:
            raise QuestionBaseException(detail=f"질문 목록 조회 중 오류가 발생했습니다: {str(e)}")
