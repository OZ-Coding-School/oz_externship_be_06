from typing import NoReturn, TypedDict

from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.permissions import IsAdminStaff


class StudentCohortDict(TypedDict):
    id: int
    number: int


class StudentCourseDict(TypedDict):
    id: int
    name: str
    tag: str


class InProgressCourseDict(TypedDict):
    cohort: StudentCohortDict
    course: StudentCourseDict


class MockStudentDict(TypedDict):
    id: int
    email: str
    nickname: str
    name: str
    phone_number: str
    birthday: str
    status: str
    role: str
    in_progress_course: InProgressCourseDict
    created_at: str


# 어드민 수강생 목록 조회 api
class AdminStudentListAPIView(APIView):

    permission_classes = [IsAuthenticated, IsAdminStaff]

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated(detail="자격 인증 데이터가 제공되지 않았습니다.")
        raise PermissionDenied(detail="권한이 없습니다.")

    def _get_mock_students(self) -> list[MockStudentDict]:
        # mock 데이터
        return [
            {
                "id": 1,
                "email": "student1@example.com",
                "nickname": "수강생1",
                "name": "김수강",
                "phone_number": "01011111111",
                "birthday": "2000-01-01",
                "status": "ACTIVATED",
                "role": "STUDENT",
                "in_progress_course": {
                    "cohort": {"id": 1, "number": 1},
                    "course": {"id": 1, "name": "백엔드 부트캠프", "tag": "BE"},
                },
                "created_at": "2025-01-01T00:00:00+09:00",
            },
            {
                "id": 2,
                "email": "student2@example.com",
                "nickname": "수강생2",
                "name": "이수강",
                "phone_number": "01022222222",
                "birthday": "2001-02-02",
                "status": "ACTIVATED",
                "role": "STUDENT",
                "in_progress_course": {
                    "cohort": {"id": 2, "number": 2},
                    "course": {"id": 1, "name": "백엔드 부트캠프", "tag": "BE"},
                },
                "created_at": "2025-01-02T00:00:00+09:00",
            },
            {
                "id": 3,
                "email": "student3@example.com",
                "nickname": "수강생3",
                "name": "박수강",
                "phone_number": "01033333333",
                "birthday": "2002-03-03",
                "status": "DEACTIVATED",
                "role": "STUDENT",
                "in_progress_course": {
                    "cohort": {"id": 3, "number": 1},
                    "course": {"id": 2, "name": "프론트엔드 부트캠프", "tag": "FE"},
                },
                "created_at": "2025-01-03T00:00:00+09:00",
            },
        ]

    @extend_schema(
        tags=["admin_accounts"],
        summary="어드민 페이지 수강생 목록 조회 API",
        description="""
        스태프(조교, 러닝코치, 운영매니저) 또는 관리자가 수강생 목록을 조회합니다.

        페이지네이션, 검색, 필터링 기능을 제공
        기본적으로 ID 순으로 정렬
        """,
        parameters=[
            OpenApiParameter(
                name="page",
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description="페이지 번호",
            ),
            OpenApiParameter(
                name="page_size",
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description="페이지 크기 (기본: 10, 최대: 100)",
            ),
            OpenApiParameter(
                name="search",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="검색어 (이름, 이메일, 닉네임, 연락처)",
            ),
            OpenApiParameter(
                name="status",
                type=str,
                location=OpenApiParameter.QUERY,
                required=False,
                description="상태 필터 (activated, deactivated, withdrew)",
                enum=["activated", "deactivated", "withdrew"],
            ),
            OpenApiParameter(
                name="course_id",
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description="과정 ID 필터",
            ),
            OpenApiParameter(
                name="cohort_id",
                type=int,
                location=OpenApiParameter.QUERY,
                required=False,
                description="기수 ID 필터",
            ),
        ],
        responses={
            200: OpenApiResponse(description="수강생 목록"),
            401: OpenApiResponse(description="자격 인증 데이터가 제공되지 않았습니다."),
            403: OpenApiResponse(description="권한이 없습니다."),
        },
    )
    def get(self, request: Request) -> Response:
        # Mock 데이터 반환
        mock_students = self._get_mock_students()

        # 페이지네이션 형식으로 응답
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))

        start = (page - 1) * page_size
        end = start + page_size
        paginated_data = mock_students[start:end]

        return Response(
            {
                "count": len(mock_students),
                "next": None,
                "previous": None,
                "results": paginated_data,
            }
        )
