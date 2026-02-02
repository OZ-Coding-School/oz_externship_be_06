from typing import Optional

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.qna.serializers.common.request import PresignedUrlRequestSerializer
from apps.qna.serializers.common.response import PresignedUrlResponseSerializer
from apps.qna.services.common.command import PresignedUrlCommandService, StorageTarget
from apps.qna.views.base_view import QnaBaseAPIView


class BasePresignedUrlAPIView(QnaBaseAPIView):
    """
    이미지 업로드용 Presigned URL 발급 베이스 뷰
    공통 비즈니스 로직을 포함하며, 상속을 통해 도메인을 결정
    """

    permission_classes = [IsAuthenticated]
    storage_target: StorageTarget

    def put(self, request: Request) -> Response:
        """공통 PUT 로직: 시리얼라이저 검증 후 도메인별 서비스 호출"""

        serializer = PresignedUrlRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = PresignedUrlCommandService.get_presigned_url(
            target=self.storage_target, file_name=serializer.validated_data["file_name"]
        )

        response_serializer = PresignedUrlResponseSerializer(result)
        return Response(response_serializer.data)


class QuestionPresignedUrlAPIView(BasePresignedUrlAPIView):
    """
    질문 이미지 업로드용 Presigned URL 발급 API
    """

    storage_target = StorageTarget.QUESTION

    @extend_schema(
        summary="질문 이미지 업로드 URL 발급",
        description="S3의 'questions/' 경로로 이미지를 업로드하기 위한 임시 URL을 발급합니다.",
        request=PresignedUrlRequestSerializer,
        responses={200: PresignedUrlResponseSerializer},
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
        responses={200: PresignedUrlResponseSerializer},
        tags=["qna"],
    )
    def put(self, request: Request) -> Response:
        return super().put(request)
