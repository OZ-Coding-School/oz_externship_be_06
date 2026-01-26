from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import permissions, status, serializers
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from django.shortcuts import get_object_or_404

from apps.exams.models import ExamDeployment
from apps.exams.serializers import AdminExamUpdateSerializer, ErrorResponseSerializer, ErrorDetailSerializer


class IsAdminOrStaffPermission(permissions.BasePermission):
    message = "쪽지시험 수정 권한이 없습니다."

    def has_permission(self, request, view):
        return bool(request.user and (request.user.is_staff or request.user.is_superuser))

@extend_schema(
    tags=["Admin Exams"],
    summary="쪽지시험 수정 API",
    description="스태프/관리자 권한을 가진 사용자가 쪽지시험 정보를 수정합니다.",
    request=AdminExamUpdateSerializer,
    responses={
        201: AdminExamUpdateSerializer,  # 수정 성공 시 반환
        400: ErrorResponseSerializer,    # 잘못된 요청 데이터
        401: ErrorDetailSerializer,      # 인증 실패
        403: ErrorDetailSerializer,      # 권한 없음
        404: ErrorResponseSerializer,    # 시험 정보 없음
        409: ErrorResponseSerializer,    # 중복 이름
    }
)
class AdminExamUpdateAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAdminUser]  # 스태프/관리자 권한

    def put(self, request, exam_id):
        if not self.has_staff_permission(request.user):
            return Response(
                {"error_detail": "쪽지시험 수정 권한이 없습니다."},
                status=status.HTTP_403_FORBIDDEN
            )

        exam = get_object_or_404(ExamDeployment, id=exam_id)

        serializer = AdminExamUpdateSerializer(exam, data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError:
            return Response(
                {"error_detail": "유효하지 않은 요청 데이터입니다."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save()

        response_data = {
            "id": exam.id,
            "title": exam.title,
            "subject_id": exam.subject_id,
            "thumbnail_img_url": exam.thumbnail_img.url if exam.thumbnail_img else None
        }
        return Response(response_data, status=status.HTTP_200_OK)
