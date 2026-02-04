from typing import NoReturn

from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.utils.permissions import IsStaffRole
from apps.exams.constants import ErrorMessages
from apps.exams.serializers.admin.deployments_delete import (
    AdminExamDeploymentDeleteResponseSerializer,
)
from apps.exams.serializers.error_serializers import ErrorResponseSerializer
from apps.exams.services.admin.deployments_delete import (
    ExamDeploymentDeleteConflictError,
    ExamDeploymentDeleteNotFoundError,
    delete_exam_deployment,
)


class AdminExamDeploymentDeleteAPIView(APIView):
    permission_classes = [IsStaffRole]

    @extend_schema(
        tags=["admin_exams"],
        summary="쪽지시험 배포 삭제 API",
        description="관리자/스태프가 쪽지시험 배포 내역을 삭제합니다.",
        responses={
            200: AdminExamDeploymentDeleteResponseSerializer,
            400: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Bad Request",
                examples=[
                    OpenApiExample(
                        "유효하지 않은 배포 삭제 요청",
                        value={"error_detail": ErrorMessages.INVALID_DEPLOYMENT_DELETE_REQUEST.value},
                    ),
                ],
            ),
            401: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Unauthorized",
                examples=[
                    OpenApiExample(
                        "인증 실패",
                        value={"error_detail": ErrorMessages.UNAUTHORIZED.value},
                    ),
                ],
            ),
            403: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Forbidden",
                examples=[
                    OpenApiExample(
                        "권한 없음",
                        value={"error_detail": ErrorMessages.NO_DEPLOYMENT_DELETE_PERMISSION.value},
                    ),
                ],
            ),
            404: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Not Found",
                examples=[
                    OpenApiExample(
                        "배포 정보 찾을 수 없음",
                        value={"error_detail": ErrorMessages.DEPLOYMENT_DELETE_NOT_FOUND.value},
                    ),
                ],
            ),
            409: OpenApiResponse(
                response=ErrorResponseSerializer,
                description="Conflict",
                examples=[
                    OpenApiExample(
                        "배포 삭제 충돌",
                        value={"error_detail": ErrorMessages.DEPLOYMENT_DELETE_CONFLICT.value},
                    ),
                ],
            ),
        },
    )
    def permission_denied(
        self,
        request: Request,
        message: str | None = None,
        code: str | None = None,
    ) -> NoReturn:
        # 401
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated(detail=ErrorMessages.UNAUTHORIZED.value)
        # 403
        raise PermissionDenied(detail=ErrorMessages.NO_DEPLOYMENT_DELETE_PERMISSION.value)

    def delete(self, _request: Request, deployment_id: int) -> Response:
        # 400
        if deployment_id <= 0:

            return Response(
                {"error_detail": ErrorMessages.INVALID_DEPLOYMENT_DELETE_REQUEST.value},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            result = delete_exam_deployment(deployment_id=deployment_id)
        # 404
        except ExamDeploymentDeleteNotFoundError:
            return Response(
                {"error_detail": ErrorMessages.DEPLOYMENT_DELETE_NOT_FOUND.value},
                status=status.HTTP_404_NOT_FOUND,
            )
        # 409
        except ExamDeploymentDeleteConflictError:
            return Response(
                {"error_detail": ErrorMessages.DEPLOYMENT_DELETE_CONFLICT.value},
                status=status.HTTP_409_CONFLICT,
            )

        serializer = AdminExamDeploymentDeleteResponseSerializer(result)
        return Response(serializer.data, status=status.HTTP_200_OK)
