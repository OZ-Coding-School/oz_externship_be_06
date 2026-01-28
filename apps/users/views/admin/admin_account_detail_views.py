from datetime import date
from typing import NoReturn, TypedDict

from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import User
from apps.users.permissions import IsAdminStaff


class CourseDict(TypedDict):
    id: int
    name: str
    tag: str


class CohortDict(TypedDict):
    id: int
    number: int
    status: str
    status_display: str
    start_date: str
    end_date: str


class AssignedCourseDict(TypedDict):
    course: CourseDict
    cohort: CohortDict


class MockUserDict(TypedDict):
    id: int
    email: str
    nickname: str
    name: str
    phone_number: str
    birthday: str
    gender: str
    role: str
    status: str
    profile_img_url: str
    created_at: str
    assigned_courses: list[AssignedCourseDict]


# 어드민 회원 정보 상세 조회
class AdminAccountDetailAPIView(APIView):

    permission_classes = [IsAuthenticated, IsAdminStaff]

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated(detail="자격 인증 데이터가 제공되지 않았습니다.")
        raise PermissionDenied(detail="권한이 없습니다.")

    def _get_mock_user(self, account_id: int) -> MockUserDict:
        # mock 데이터
        return {
            "id": account_id,
            "email": "mockuser@example.com",
            "nickname": "목유저",
            "name": "홍길동",
            "phone_number": "01012345678",
            "birthday": "1995-05-15",
            "gender": "MALE",
            "role": "STUDENT",
            "status": "ACTIVATED",
            "profile_img_url": "https://example.com/profile.png",
            "created_at": "2025-01-01T00:00:00+09:00",
            "assigned_courses": [
                {
                    "course": {
                        "id": 1,
                        "name": "백엔드 부트캠프",
                        "tag": "BE",
                    },
                    "cohort": {
                        "id": 1,
                        "number": 1,
                        "status": "IN_PROGRESS",
                        "status_display": "진행중",
                        "start_date": "2025-01-01",
                        "end_date": "2025-06-30",
                    },
                }
            ],
        }

    @extend_schema(
        tags=["admin_accounts"],
        summary="어드민 페이지 회원 정보 상세 조회 API",
        description="""
        스태프(조교, 러닝코치, 운영매니저) 또는 관리자가 회원 상세 정보를 조회합니다.

        조회 대상 회원의 권한에 따라 반환되는 assigned_courses 내용이 다릅니다:
        - 조교(TA): 담당 기수 목록 (과정명, 기수, 상태)
        - 러닝코치(LC), 운영매니저(OM): 담당 과정 목록 (과정명)
        - 수강생(STUDENT): 수강 기수 목록 (과정명, 기수, 상태)
        - 그 외: 빈 배열
        """,
        parameters=[
            OpenApiParameter(
                name="account_id",
                type=int,
                location=OpenApiParameter.PATH,
                required=True,
                description="회원 ID",
            ),
        ],
        responses={
            200: OpenApiResponse(description="회원 상세 정보"),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
            404: OpenApiResponse(description="사용자 정보를 찾을 수 없습니다."),
        },
    )
    def get(self, request: Request, account_id: int) -> Response:
        # Mock 데이터 반환
        mock_data = self._get_mock_user(account_id)
        return Response(mock_data, status=status.HTTP_200_OK)
