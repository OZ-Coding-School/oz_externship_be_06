from enum import Enum
from typing import Any

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.serializers.presigned_url import (
    PresignedUrlRequestSerializer,
    PresignedUrlResponseSerializer,
)
from apps.core.views.presigned_url import BasePresignedUrlAPIView
from apps.core.utils.permissions import CanWriteAnswerComment, IsStudentRole


class StorageTarget(Enum):
    """
    이미지 업로드 도메인 및 S3 경로 정의 Enum
    """

    QUESTION = ("question", "uploads/images/questions")
    ANSWER = ("answer", "uploads/images/answers")

    def __init__(self, domain: str, s3_path: str):
        self.domain = domain
        self.s3_path = s3_path


class QuestionPresignedUrlAPIView(BasePresignedUrlAPIView):
    """
    질문 이미지 업로드용 Presigned URL 발급 API
    """

    storage_target = StorageTarget.QUESTION

    serializer_class = PresignedUrlRequestSerializer

    def get_permissions(self) -> list[Any]:
        return [IsAuthenticated(), IsStudentRole()]

    @extend_schema(
        tags=["qna"],
        summary="질문 이미지 업로드 URL 발급",
        description="""
        S3의 'question/' 경로로 이미지를 업로드하기 위한 presigned-URL을 발급합니다.
        로그인 및 질문 작성 권한(STUDENT)을 가진 사용자만 사용 가능합니다.
        """,
        request=PresignedUrlRequestSerializer,
        responses={
            200: OpenApiResponse(
                description="OK",
                response=PresignedUrlResponseSerializer,
            ),
            400: OpenApiResponse(
                description="Bad Request",
            ),
            401: OpenApiResponse(
                description="Unauthorized",
            ),
            403: OpenApiResponse(
                description="Forbidden",
            ),
        },
    )
    def put(self, request: Request) -> Response:
        return super().put(request)


class AnswerPresignedUrlAPIView(BasePresignedUrlAPIView):
    """
    답변 이미지 업로드용 Presigned URL 발급 API
    """

    storage_target = StorageTarget.ANSWER

    serializer_class = PresignedUrlRequestSerializer

    def get_permissions(self) -> list[Any]:
        return [IsAuthenticated(), CanWriteAnswerComment()]

    @extend_schema(
        tags=["qna"],
        summary="답변 이미지 업로드 URL 발급",
        description="""
        S3의 'answers/' 경로로 이미지를 업로드하기 위한 presigned-URL을 발급합니다.
        로그인 및 댓글 작성 권한(STUDENT, TA, LC, OM, ADMIN)을 가진 사용자만 사용 가능합니다.
        """,
        request=PresignedUrlRequestSerializer,
        responses={
            200: OpenApiResponse(
                description="OK",
                response=PresignedUrlResponseSerializer,
            ),
            400: OpenApiResponse(
                description="Bad Request",
            ),
            401: OpenApiResponse(
                description="Unauthorized",
            ),
            403: OpenApiResponse(
                description="Forbidden",
            ),
        },
    )
    def put(self, request: Request) -> Response:
        return super().put(request)
