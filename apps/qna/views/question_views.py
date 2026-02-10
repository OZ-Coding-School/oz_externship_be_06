from typing import Any, cast

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.utils.permissions import IsStudentRole
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
    QuestionUpdateRequestSerializer,
)
from apps.qna.serializers.question.response import (
    QuestionCreateResponseSerializer,
    QuestionDetailSerializer,
    QuestionListSerializer,
    QuestionUpdateResponseSerializer,
)
from apps.qna.services.question.command import QuestionCommandService
from apps.qna.services.question.query import QuestionQueryService
from apps.qna.utils.qna_paginator import QuestionListPaginator as Paginator
from apps.qna.views.base_view import QnaBaseAPIView


class QuestionCreateListAPIView(QnaBaseAPIView):
    """
    /api/v1/qna/questions
    [POST] 질문 등록
    [GET] 질문 목록 조회
    """

    serializer_classes = {
        "POST": QuestionCreateSerializer,
        "GET": QuestionQuerySerializer,
    }

    def get_permissions(self) -> list[Any]:
        method = self.request.method or ""
        if method == "POST":
            return [IsAuthenticated(), IsStudentRole()]
        elif method == "GET":
            return [AllowAny()]
        raise MethodNotAllowed(method)

    # [POST] 질문 등록
    @extend_schema(
        tags=["qna"],
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
    )
    def post(self, request: Request) -> Response:
        """질문 생성"""
        serializer = QuestionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 서비스 호출
        question = QuestionCommandService.create_question(author=self.request_user, data=serializer.validated_data)

        # 응답 출력
        response_serializer = QuestionCreateResponseSerializer(question)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    # [GET] 질문 목록 조회
    @extend_schema(
        tags=["qna"],
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
    )
    def get(self, request: Request) -> Response:
        """필터링 및 검색된 질문 목록 반환"""
        # 쿼리 파라미터 검증
        query_serializer = QuestionQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        queryset = QuestionQueryService.get_question_list(query_serializer.validated_data)

        # Response 생성
        return Paginator.get_paginated_data_response(
            queryset=queryset, request=request, serializer_class=QuestionListSerializer, view=self
        )


class QuestionDetailAPIView(QnaBaseAPIView):
    """
    /api/v1/qna/questions/{question_id}
    [GET] 질문 상세 조회
    [PUT] 질문 상세 수정
    """

    serializer_classes = {
        "GET": None,
        "PUT": QuestionUpdateRequestSerializer,
    }

    def get_permissions(self) -> list[Any]:
        method = self.request.method or ""
        if method == "GET":
            return [AllowAny()]
        elif method == "PUT":
            return [IsAuthenticated(), IsStudentRole()]
        raise MethodNotAllowed(method)

    # [GET] 질의응답 상세 조회
    @extend_schema(
        tags=["qna"],
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
    )
    def get(self, request: Request, question_id: int) -> Response:
        question = QuestionQueryService.get_question_detail(question_id)

        serializer = QuestionDetailSerializer(cast(Any, question))

        return Response(serializer.data, status=status.HTTP_200_OK)

    # [PUT] 질문 수정
    @extend_schema(
        tags=["qna"],
        summary="질문 수정 API",
        description=ApiDescriptions.QUESTION_UPDATE,
        request=QuestionUpdateRequestSerializer,
        examples=[RequestBodyExamples.QUESTION_UPDATE],
        responses={
            200: OpenApiResponse(
                description="OK",
                response=QuestionUpdateResponseSerializer,
                examples=[SuccessResponseExamples.QUESTION_UPDATE],
            ),
            400: OpenApiResponse(
                description="Bad Request",
                response=dict,
                examples=[ErrorResponseExamples.QUESTION_UPDATE_400],
            ),
            401: OpenApiResponse(
                description="Unauthorized",
                response=dict,
                examples=[ErrorResponseExamples.QUESTION_UPDATE_401],
            ),
            403: OpenApiResponse(
                description="Forbidden",
                response=dict,
                examples=[ErrorResponseExamples.QUESTION_UPDATE_403],
            ),
            404: OpenApiResponse(
                description="Not Found",
                response=dict,
                examples=[ErrorResponseExamples.QUESTION_UPDATE_404],
            ),
        },
    )
    def put(self, request: Request, question_id: int) -> Response:
        serializer = QuestionUpdateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        question = QuestionCommandService.update_question(question_id, self.request_user, serializer.validated_data)

        response_serializer = QuestionUpdateResponseSerializer(question)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
