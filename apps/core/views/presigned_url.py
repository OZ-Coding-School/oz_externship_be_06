
from __future__ import annotations

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.services.command import PresignedUrlCommandService, StorageTarget
from apps.core.serializers.request import PresignedUrlRequestSerializer
from apps.core.serializers.response import PresignedUrlResponseSerializer


class BasePresignedUrlAPIView(APIView):
    """
    이미지 업로드용 Presigned URL 발급 베이스 뷰
    도메인을 결정을 위해 StorageTarget Enum 값 상속 필요
    """

    permission_classes: list = []
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