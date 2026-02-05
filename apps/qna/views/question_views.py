from typing import Any, cast

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.qna.docs.api_descriptions import ApiDescriptions
from apps.qna.docs.api_request_examples import (
    QueryParameterExamples,
    RequestBodyExamples,
)
from apps.qna.docs.api_response_examples import (
    ErrorResponseExamples,
    SuccessResponseExamples,
)
from apps.qna.serializers.question.request import (
    QuestionCreateSerializer,
    QuestionQuerySerializer,
)
from apps.qna.serializers.question.response import (
    QuestionCategoryTreeResponseSerializer,
    QuestionCreateResponseSerializer,
    QuestionDetailSerializer,
    QuestionListSerializer,
)
from apps.qna.services.question.command import QuestionCommandService
from apps.qna.services.question.query import QuestionQueryService
from apps.qna.utils.model_types import User
from apps.qna.utils.permissions import IsStudent
from apps.qna.utils.qna_paginator import QnAPaginator
from apps.qna.views.base_view import QnaBaseAPIView


class QuestionCreateListAPIView(QnaBaseAPIView):
    """
    질문 등록 및 목록 조회 API View
    """

    serializer_classes = {
        "GET": QuestionQuerySerializer,
        "POST": QuestionCreateSerializer,
    }

    def get_permissions(self) -> list[Any]:
        if self.request.method == "POST":
            return [IsAuthenticated(), IsStudent()]
        return [AllowAny()]

    # 질문 등록
    # [POST] /api/v1/qna/questions
    @extend_schema(
        summary="질문 등록 API",
        description=ApiDescriptions.QUESTION_CREATE,
        request=QuestionCreateSerializer,
        examples=[RequestBodyExamples.QUESTION_CREATE],
        responses={
            201: OpenApiResponse(
                description="Created",
                response=QuestionCreateResponseSerializer,
                examples=[SuccessResponseExamples.QUESTION_CREATE],
            ),
            400: OpenApiResponse(
                description="Bad Request",
                response=dict,
                examples=[ErrorResponseExamples.QUESTION_CREATE_400],
            ),
            401: OpenApiResponse(
                description="Unauthorized",
                response=dict,
                examples=[ErrorResponseExamples.QUESTION_CREATE_401],
            ),
            403: OpenApiResponse(
                description="Forbidden",
                response=dict,
                examples=[ErrorResponseExamples.QUESTION_CREATE_403],
            ),
        },
        tags=["qna"],
    )
    def post(self, request: Request) -> Response:
        """질문 생성"""
        serializer = QuestionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 서비스 호출
        question = QuestionCommandService.create_question(
            author=cast(User, request.user), data=serializer.validated_data
        )

        # 응답 출력
        response_serializer = QuestionCreateResponseSerializer(question)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    # 질문 목록 조회
    # [GET] /api/v1/qna/questions
    @extend_schema(
        summary="질문 목록 조회 API",
        description=ApiDescriptions.QUESTION_LIST,
        parameters=[QuestionQuerySerializer],
        examples=[QueryParameterExamples.QUESTION_LIST],
        responses={
            200: OpenApiResponse(
                description="OK",
                response=QuestionListSerializer(many=True),
                examples=[SuccessResponseExamples.QUESTION_LIST],
            ),
            400: OpenApiResponse(
                description="Bad Request",
                response=dict,
                examples=[ErrorResponseExamples.QUESTION_LIST_400],
            ),
            404: OpenApiResponse(
                description="Not Found",
                response=dict,
                examples=[ErrorResponseExamples.QUESTION_LIST_404],
            ),
        },
        tags=["qna"],
    )
    def get(self, request: Request) -> Response:
        """필터링 및 검색된 질문 목록 반환"""
        # 쿼리 파라미터 검증
        query_serializer = QuestionQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        queryset = QuestionQueryService.get_question_list(query_serializer.validated_data)

        # Response 생성
        return QnAPaginator.get_paginated_data_response(
            queryset=queryset, request=request, serializer_class=QuestionListSerializer, view=self
        )


class QuestionDetailAPIView(QnaBaseAPIView):
    """
    질문 상세 조회 API View
    """

    permission_classes = [AllowAny]

    # 질의응답 상세 조회
    # [GET] /api/v1/qna/questions/{question_id}
    @extend_schema(
        summary="질문 상세 조회 API",
        description=ApiDescriptions.QUESTION_DETAIL,
        responses={
            200: OpenApiResponse(
                description="OK",
                response=QuestionDetailSerializer,
                examples=[SuccessResponseExamples.QUESTION_DETAIL],
            ),
            400: OpenApiResponse(
                description="Bad Request",
                response=dict,
                examples=[ErrorResponseExamples.QUESTION_DETAIL_400],
            ),
            404: OpenApiResponse(
                description="Not Found",
                response=dict,
                examples=[ErrorResponseExamples.QUESTION_DETAIL_404],
            ),
        },
        tags=["qna"],
    )
    def get(self, request: Request, question_id: int) -> Response:
        question = QuestionQueryService.get_question_detail(question_id)

        serializer = QuestionDetailSerializer(cast(Any, question))

        return Response(serializer.data, status=status.HTTP_200_OK)


class QuestionCategoryTreeAPIView(QnaBaseAPIView):
    """
    질의응답 카테고리 전체 계층 구조 조회 API
    """

    permission_classes = [AllowAny]

    # 카테고리 목록 조회
    # [GET] /api/v1/qna/categories
    @extend_schema(
        summary="카테고리 계층 구조 조회",
        description=ApiDescriptions.QUESTION_CATEGORY_LIST,
        responses={
            200: OpenApiResponse(
                description="OK",
                response=QuestionCategoryTreeResponseSerializer,
                examples=[SuccessResponseExamples.QUESTION_CATEGORY_LIST],
            ),
            400: OpenApiResponse(
                description="Bad Request", response=dict, examples=[ErrorResponseExamples.QUESTION_CATEGORY_LIST_400]
            ),
        },
        tags=["qna"],
    )
    def get(self, request: Request) -> Response:
        categories_tree = QuestionQueryService.get_question_category_tree()

        response_serializer = QuestionCategoryTreeResponseSerializer({"categories": categories_tree})

        return Response(response_serializer.data)
