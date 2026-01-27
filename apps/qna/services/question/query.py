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
                queryset = queryset.order_by("-view_count")

            if not queryset.exists():
                raise QuestionNotFoundException(detail="조회 가능한 질문이 존재하지 않습니다.")
            return queryset

        except QuestionNotFoundException:
            raise
        except Exception:
            raise QuestionBaseException(detail="유효하지 않은 목록 조회 요청입니다.")

    @staticmethod
    def get_question_detail(question_id: int) -> Question:
        """질문 상세 정보 조회 (조회수 증가 포함)"""
        try:
            # 질문 조회 및 관련 데이터 Loading
            question = (
                Question.objects.select_related("author", "category__parent__parent")
                .prefetch_related("images", "answers__author", "answers__comments__author")
                .get(id=question_id)
            )

            # 조회수 증가
            Question.objects.filter(id=question_id).update(view_count=F("view_count") + 1)

            # 메모리 상의 객체도 업데이트 (응답용)
            question.view_count += 1

            return question

        except Question.DoesNotExist:
            raise QuestionNotFoundException(detail="해당 질문을 찾을 수 없습니다.")
        except Exception:
            raise QuestionBaseException(detail="유효하지 않은 질문 상세 조회 요청입니다.")
