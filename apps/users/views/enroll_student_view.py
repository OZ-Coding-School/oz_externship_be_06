from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.enroll_student_serializer import (
    EnrollStudentRequestSerializer,
    EnrollStudentResponseSerializer,
)
from apps.users.services.enroll_student_service import (
    AlreadyEnrolledError,
    CohortNotFoundError,
    NotUserRoleError,
    enroll_student,
)


# 수강생 등록 신청
class EnrollStudentAPIView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["accounts"],
        summary="수강생 등록 신청 API",
        description="""
수강생 등록을 신청합니다. 일반 회원(`USER`)만 신청 가능하며, 운영진 검토 후 수강생 권한이 부여됩니다.

## 플로우

1. `GET /api/v1/accounts/courses/available` - 수강신청 가능한 기수 목록 조회
2. `POST /api/v1/accounts/enroll-student` - 원하는 기수에 수강 신청 (현재 API)
3. 운영진 검토 후 승인 시 수강생(`STUDENT`) 권한 부여

## 주의사항
- 동일한 기수에 중복 신청은 불가능합니다.
- 신청 후 승인 전까지는 대기 상태입니다.
- 승인/거절 결과는 별도로 안내됩니다.
        """,
        request=EnrollStudentRequestSerializer,
        responses={
            201: EnrollStudentResponseSerializer,
            400: OpenApiResponse(description="유효하지 않은 요청"),
            401: OpenApiResponse(description="인증 실패"),
            403: OpenApiResponse(description="일반 회원만 신청 가능"),
            409: OpenApiResponse(description="이미 신청한 기수"),
        },
    )
    def post(self, request: Request) -> Response:
        serializer = EnrollStudentRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cohort_id = serializer.validated_data["cohort_id"]

        try:
            enroll_student(user=request.user, cohort_id=cohort_id)  # type: ignore[arg-type]
        except NotUserRoleError as e:
            return Response(
                {"error_detail": str(e)},
                status=status.HTTP_403_FORBIDDEN,
            )
        except CohortNotFoundError as e:
            return Response(
                {"error_detail": {"cohort_id": [str(e)]}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except AlreadyEnrolledError as e:
            return Response(
                {"error_detail": str(e)},
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            {"detail": "수강생 등록 신청완료."},
            status=status.HTTP_201_CREATED,
        )
