from enum import Enum

from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework.request import Request
from rest_framework.response import Response

from apps.core.serializers.presigned_url import (
    PresignedUrlRequestSerializer,
    PresignedUrlResponseSerializer,
)
from apps.core.views.presigned_url import BasePresignedUrlAPIView


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

    @extend_schema(
        summary="질문 이미지 업로드 URL 발급",
        description="S3의 'questions/' 경로로 이미지를 업로드하기 위한 임시 URL을 발급합니다.",
        request=PresignedUrlRequestSerializer,
        responses={
            200: PresignedUrlResponseSerializer,
            400: OpenApiResponse(
                description="Bad Request",
                response=dict,
                examples=[
                    OpenApiExample(
                        name="Presigned URL 발급 실패 예시",
                        value={"error_detail": "지원하지 않는 파일 형식입니다."},
                    ),
                ],
            ),
        },
        tags=["qna"],
    )
    def put(self, request: Request) -> Response:
        return super().put(request)


class AnswerPresignedUrlAPIView(BasePresignedUrlAPIView):
    """
    답변 이미지 업로드용 Presigned URL 발급 API
    """

    storage_target = StorageTarget.ANSWER

    @extend_schema(
        summary="답변 이미지 업로드 URL 발급",
        description="S3의 'answers/' 경로로 이미지를 업로드하기 위한 임시 URL을 발급합니다.",
        request=PresignedUrlRequestSerializer,
        responses={
            200: PresignedUrlResponseSerializer,
            400: OpenApiResponse(
                description="Bad Request",
                response=dict,
                examples=[
                    OpenApiExample(
                        name="Presigned URL 발급 실패 예시",
                        value={"error_detail": "지원하지 않는 파일 형식입니다."},
                    ),
                ],
            ),
        },
        tags=["qna"],
    )
    def put(self, request: Request) -> Response:
        return super().put(request)
