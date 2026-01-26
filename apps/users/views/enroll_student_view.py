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

#수강생 등록 신청
class EnrollStudentAPIView(APIView):

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["accounts"],
        summary="수강생 등록 신청 API",
        description="""
로그인 유저 중 일반 회원 권한을 가진 유저들은 수강생 등록 신청을 통해 수강생 권한을 얻을 수 있습니다.
추후 운영진의 검토 후에 수강생 권한을 부여합니다.
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
