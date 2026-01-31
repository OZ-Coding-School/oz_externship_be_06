from datetime import datetime
from typing import Any, cast

from django.conf import settings
from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.qna.docs.api_descriptions import ApiDescriptions
from apps.qna.docs.api_response_examples import (
    ErrorResponseExamples,
    SuccessResponseExamples,
)
from apps.qna.docs.api_rquest_examples import (
    QueryParameterExamples,
    RequestBodyExamples,
)
from apps.qna.models import (
    Question,
    QuestionCategory,
)
from apps.qna.serializers.question import request as ser_q_req
from apps.qna.serializers.question import response as ser_q_res
from apps.qna.services.question import command as svc_q_cmd
from apps.qna.services.question import query as svc_q_qry
from apps.qna.utils.model_types import User
from apps.qna.utils.permissions import IsStudent
from apps.qna.utils.question_list_pagination import QnAPaginator
from apps.qna.views.base_view import QnaBaseAPIView


class QuestionCreateListAPIView(QnaBaseAPIView):
    """
    질문 등록 및 목록 조회 API View
    """

    def get_permissions(self) -> list[Any]:
        if self.request.method == "POST":
            return [IsAuthenticated(), IsStudent()]
        return [AllowAny()]

    # 질문 등록
    # [POST] /api/v1/qna/questions
    @extend_schema(
        summary="질문 등록 API",
        description=ApiDescriptions.QUESTION_CREATE,
        request=ser_q_req.QuestionCreateSerializer,
        examples=RequestBodyExamples.QUESTION_CREATE,
        responses={
            201: OpenApiResponse(
                description="Created",
                response=ser_q_res.QuestionCreateResponseSerializer,
                examples=SuccessResponseExamples.QUESTION_CREATE,
            ),
            400: OpenApiResponse(
                description="Bad Request",
                response=dict,
                examples=ErrorResponseExamples.QUESTION_CREATE_400,
            ),
            401: OpenApiResponse(
                description="Unauthorized",
                response=dict,
                examples=ErrorResponseExamples.QUESTION_CREATE_401,
            ),
            403: OpenApiResponse(
                description="Forbidden",
                response=dict,
                examples=ErrorResponseExamples.QUESTION_CREATE_403,
            ),
        },
        tags=["qna"],
    )
    def post(self, request: Request) -> Response:
        """질문 생성"""
        serializer = ser_q_req.QuestionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 서비스 호출
        question = svc_q_cmd.QuestionCommandService.create_question(
            author=cast(User, request.user), data=serializer.validated_data
        )

        # 응답 출력
        response_serializer = ser_q_res.QuestionCreateResponseSerializer(question)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    # 질문 목록 조회
    # [GET] /api/v1/qna/questions
    @extend_schema(
        summary="질문 목록 조회 API",
        description=ApiDescriptions.QUESTION_LIST,
        parameters=[ser_q_req.QuestionQuerySerializer],
        examples=QueryParameterExamples.QUESTION_LIST,
        responses={
            200: OpenApiResponse(
                description="OK",
                response=ser_q_res.QuestionListSerializer(many=True),
                examples=SuccessResponseExamples.QUESTION_LIST,
            ),
            400: OpenApiResponse(
                description="Bad Request",
                response=dict,
                examples=ErrorResponseExamples.QUESTION_LIST_400,
            ),
            404: OpenApiResponse(
                description="Not Found",
                response=dict,
                examples=ErrorResponseExamples.QUESTION_LIST_404,
            ),
        },
        tags=["qna"],
    )
    def get(self, request: Request) -> Response:
        """필터링 및 검색된 질문 목록 반환"""
        # 쿼리 파라미터 검증
        query_serializer = ser_q_req.QuestionQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        # Mock Data 생성
        if settings.USE_QNA_MOCK:
            User = get_user_model()
            mock_user = User(
                id=1,
                nickname="MockUser",
                profile_img_url="https://ssl.pstatic.net/static/pwe/address/img_profile.png",
            )

            cat_root = QuestionCategory(id=1, name="개발")
            cat_mid = QuestionCategory(id=2, name="백엔드", parent=cat_root)
            cat_leaf = QuestionCategory(id=3, name="Django", parent=cat_mid)

            queryset: Any = []
            for i in range(1, 11):
                q = Question(
                    id=i,
                    author=mock_user,
                    category=cat_leaf,
                    title=f"Mock 질문 제목 {i}",
                    content=f"Mock 질문 내용입니다. {i} ![image](https://via.placeholder.com/150)",
                    view_count=i * 10,
                    created_at=datetime.now(),
                )
                # Annotate field manual injection
                setattr(q, "answer_count", i % 3)
                queryset.append(q)
        else:
            queryset = svc_q_qry.QuestionQueryService.get_question_list(query_serializer.validated_data)

        # Response 생성
        return QnAPaginator.get_paginated_data_response(
            queryset=queryset, request=request, serializer_class=ser_q_res.QuestionListSerializer, view=self
        )


class QuestionDetailAPIView(QnaBaseAPIView):
    """
    질문 상세 조회 API View
    """

    permission_classes = [AllowAny]

    # 질의응답 상세 조회
    # GET /api/v1/qna/questions/{question_id}
    @extend_schema(
        summary="질문 상세 조회 API",
        description=ApiDescriptions.QUESTION_DETAIL,
        responses={
            200: OpenApiResponse(
                description="OK",
                response=ser_q_res.QuestionDetailSerializer,
                examples=SuccessResponseExamples.QUESTION_DETAIL,
            ),
            400: OpenApiResponse(
                description="Bad Request",
                response=dict,
                examples=ErrorResponseExamples.QUESTION_DETAIL_400,
            ),
            404: OpenApiResponse(
                description="Not Found",
                response=dict,
                examples=ErrorResponseExamples.QUESTION_DETAIL_404,
            ),
        },
        tags=["qna"],
    )
    def get(self, request: Request, question_id: int) -> Response:
        # Mock Data 생성
        if settings.USE_QNA_MOCK:
            from types import SimpleNamespace

            mock_user = SimpleNamespace(
                id=1,
                nickname="MockUser",
                profile_img_url="https://ssl.pstatic.net/static/pwe/address/img_profile.png",
            )

            cat_root = SimpleNamespace(id=1, name="개발", parent=None)
            cat_mid = SimpleNamespace(id=2, name="백엔드", parent=cat_root)
            cat_leaf = SimpleNamespace(id=3, name="Django", parent=cat_mid)

            question: Any = SimpleNamespace(
                id=question_id,
                author=mock_user,
                category=cat_leaf,
                title=f"Mock 상세 질문 제목 {question_id}",
                content=f"Mock 상세 질문 내용입니다.\n\n![img](https://via.placeholder.com/200)",
                view_count=123,
                created_at=datetime.now(),
            )

            # Mock Images
            question.images = [
                SimpleNamespace(id=1, img_url="https://via.placeholder.com/200"),
                SimpleNamespace(id=2, img_url="https://via.placeholder.com/201"),
            ]

            # Mock Comments for Answer
            # AnswerComment also needs to be SimpleNamespace
            comment1 = SimpleNamespace(
                id=1,
                author=mock_user,
                content="Mock 댓글 1",
                created_at=datetime.now(),
            )
            # Answer needs to link to comment
            # Note: The AnswerSerializer typically expects 'comments' related name or field.
            # In the model, it is related_name='comments'.
            pass

            # Mock Answers
            ans1 = SimpleNamespace(
                id=1,
                question=question,
                author=mock_user,
                content="Mock 답변 내용 1",
                created_at=datetime.now(),
                is_adopted=False,
                comments=[comment1],  # Directly assign list
            )
            # Fix comment reference back to answer if needed (usually circular not needed for serialization if one way)
            comment1.answer = ans1

            question.answers = [ans1]

        else:
            question = svc_q_qry.QuestionQueryService.get_question_detail(question_id)

        serializer = ser_q_res.QuestionDetailSerializer(question)
        return Response(serializer.data, status=status.HTTP_200_OK)
