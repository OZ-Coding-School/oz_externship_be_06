from django.urls import reverse
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exams.permissions import IsExamStaff
from apps.exams.serializers.admin_exam_deployment_detail_serializers import (
    AdminExamDeploymentDetailResponseSerializer,
)
from apps.exams.serializers.error_serializers import ErrorResponseSerializer
from apps.exams.services.admin_exam_deployment_detail_service import (
    ExamDeploymentDetailNotFoundError,
    get_exam_deployment_detail,
)


class AdminExamDeploymentDetailAPIView(APIView):
    """어드민 쪽지시험 배포 상세 조회 API."""

    permission_classes = [IsAuthenticated, IsExamStaff]
    serializer_class = AdminExamDeploymentDetailResponseSerializer

    @extend_schema(
        tags=["admin_exams"],
        summary="어드민 쪽지시험 배포 상세 조회 API",
        description="""
        스태프/관리자가 쪽지시험 배포 상세 정보를 조회합니다.
        시험 정보, 배포 정보, 응시 통계를 반환합니다.
        """,
        responses={
            200: AdminExamDeploymentDetailResponseSerializer,
            400: OpenApiResponse(ErrorResponseSerializer, description="유효하지 않은 요청"),
            401: OpenApiResponse(ErrorResponseSerializer, description="인증 실패"),
            403: OpenApiResponse(ErrorResponseSerializer, description="배포 조회 권한 없음"),
            404: OpenApiResponse(ErrorResponseSerializer, description="배포 정보 없음"),
        },
    )
    def get(self, request: Request, deployment_id: int) -> Response:
        if deployment_id <= 0:
            return Response(
                {"error_detail": "유효하지 않은 배포 상세 조회 요청입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            payload = get_exam_deployment_detail(deployment_id)
        except ExamDeploymentDetailNotFoundError:
            return Response(
                {"error_detail": "해당 배포 정보를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        access_url = request.build_absolute_uri(reverse("exams:take-exam", kwargs={"deployment_id": deployment_id}))
        payload["exam_access_url"] = access_url

        serializer = self.serializer_class(payload)
        return Response(serializer.data, status=status.HTTP_200_OK)
