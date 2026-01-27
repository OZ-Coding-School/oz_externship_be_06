from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exams.permissions import IsExamStaff
from apps.exams.serializers.admin.deployments import (
    AdminExamDeploymentCreateRequestSerializer,
    AdminExamDeploymentCreateResponseSerializer,
)
from apps.exams.serializers.error_serializers import ErrorResponseSerializer
from apps.exams.services.admin.deployments import (
    ExamDeploymentConflictError,
    ExamDeploymentNotFoundError,
    create_exam_deployment,
)


class AdminExamDeploymentCreateAPIView(APIView):
    """어드민 쪽지시험 배포 생성 API."""

    permission_classes = [IsAuthenticated, IsExamStaff]
    serializer_class = AdminExamDeploymentCreateRequestSerializer

    @extend_schema(
        tags=["admin_exams"],
        summary="어드민 쪽지시험 배포 생성 API",
        description="""
        스태프/관리자가 쪽지시험 배포를 생성합니다.
        배포 생성 시 문제 스냅샷과 참가 코드가 생성됩니다.
        """,
        request=AdminExamDeploymentCreateRequestSerializer,
        responses={
            201: AdminExamDeploymentCreateResponseSerializer,
            400: OpenApiResponse(ErrorResponseSerializer, description="유효하지 않은 요청"),
            401: OpenApiResponse(ErrorResponseSerializer, description="인증 실패"),
            403: OpenApiResponse(ErrorResponseSerializer, description="배포 생성 권한 없음"),
            404: OpenApiResponse(ErrorResponseSerializer, description="배포 대상 정보 없음"),
            409: OpenApiResponse(ErrorResponseSerializer, description="중복 배포"),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error_detail": "유효하지 않은 배포 생성 요청입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            deployment_id = create_exam_deployment(serializer.validated_data)
        except ExamDeploymentNotFoundError:
            return Response(
                {"error_detail": "배포 대상 과정-기수 또는 시험 정보를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except ExamDeploymentConflictError:
            return Response(
                {"error_detail": "동일한 조건의 배포가 이미 존재합니다."},
                status=status.HTTP_409_CONFLICT,
            )

        response_serializer = AdminExamDeploymentCreateResponseSerializer(data={"pk": deployment_id})
        response_serializer.is_valid(raise_exception=True)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
