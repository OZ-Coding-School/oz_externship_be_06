from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)

from apps.core.serializers.presigned_url import (
    PresignedUrlRequestSerializer,
    PresignedUrlResponseSerializer,
)
from apps.exams.constants import ErrorMessages
from apps.exams.serializers.admin.deployments_create import (
    AdminExamDeploymentCreateRequestSerializer,
    AdminExamDeploymentCreateResponseSerializer,
)
from apps.exams.serializers.admin.deployments_delete import (
    AdminExamDeploymentDeleteResponseSerializer,
)
from apps.exams.serializers.admin.deployments_detail import (
    AdminExamDeploymentDetailResponseSerializer,
)
from apps.exams.serializers.admin.deployments_status import (
    AdminExamDeploymentStatusRequestSerializer,
    AdminExamDeploymentStatusResponseSerializer,
)
from apps.exams.serializers.admin.deployments_update import (
    AdminExamDeploymentUpdateRequestSerializer,
    AdminExamDeploymentUpdateResponseSerializer,
)
from apps.exams.serializers.admin.exams_create import (
    AdminExamCreateRequestSerializer,
    AdminExamCreateResponseSerializer,
)
from apps.exams.serializers.admin.exams_delete import AdminExamDeleteResponseSerializer
from apps.exams.serializers.admin.exams_update import (
    AdminExamUpdateRequestSerializer,
    AdminExamUpdateResponseSerializer,
)
from apps.exams.serializers.admin.questions_create import (
    AdminExamQuestionCreateRequestSerializer,
    AdminExamQuestionCreateResponseSerializer,
)
from apps.exams.serializers.admin.questions_delete import (
    AdminExamQuestionDeleteResponseSerializer,
)
from apps.exams.serializers.admin.questions_update import (
    AdminExamQuestionUpdateRequestSerializer,
    AdminExamQuestionUpdateResponseSerializer,
)
from apps.exams.serializers.admin.submissions_delete import (
    AdminExamSubmissionDeleteResponseSerializer,
)
from apps.exams.serializers.admin.submissions_detail import (
    AdminExamSubmissionDetailResponseSerializer,
)
from apps.exams.serializers.admin.submissions_list import (
    AdminExamSubmissionListResponseSerializer,
)
from apps.exams.serializers.error_serializers import ErrorResponseSerializer

admin_exam_deployment_status_schema = extend_schema(
    tags=["admin_exams"],
    summary="어드민 배포 상태 변경",
    description="쪽지시험 배포 상태를 변경합니다.",
    request=AdminExamDeploymentStatusRequestSerializer,
    responses={
        200: AdminExamDeploymentStatusResponseSerializer,
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Bad Request",
            examples=[
                OpenApiExample(
                    "유효하지 않은 배포 상태 요청",
                    value={"error_detail": ErrorMessages.INVALID_DEPLOYMENT_STATUS_REQUEST.value},
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
                    value={"error_detail": ErrorMessages.NO_DEPLOYMENT_STATUS_PERMISSION.value},
                ),
            ],
        ),
        404: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Not Found",
            examples=[
                OpenApiExample(
                    "배포 정보 없음",
                    value={"error_detail": ErrorMessages.DEPLOYMENT_NOT_FOUND.value},
                ),
            ],
        ),
        409: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Conflict",
            examples=[
                OpenApiExample(
                    "상태 변경 충돌",
                    value={"error_detail": ErrorMessages.DEPLOYMENT_CONFLICT.value},
                ),
            ],
        ),
    },
)

admin_exam_question_create_schema = extend_schema(
    tags=["admin_exams"],
    summary="어드민 문제 등록",
    description="쪽지시험 문제를 등록합니다.",
    request=AdminExamQuestionCreateRequestSerializer,
    responses={
        201: AdminExamQuestionCreateResponseSerializer,
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Bad Request",
            examples=[
                OpenApiExample(
                    "유효하지 않은 문제 등록 요청",
                    value={"error_detail": ErrorMessages.INVALID_QUESTION_CREATE_REQUEST.value},
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
                    value={"error_detail": ErrorMessages.NO_QUESTION_CREATE_PERMISSION.value},
                ),
            ],
        ),
        404: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Not Found",
            examples=[
                OpenApiExample(
                    "시험 정보 없음",
                    value={"error_detail": ErrorMessages.EXAM_ADMIN_NOT_FOUND.value},
                ),
            ],
        ),
        409: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Conflict",
            examples=[
                OpenApiExample(
                    "문제 등록 제한 초과",
                    value={"error_detail": ErrorMessages.QUESTION_CREATE_CONFLICT.value},
                ),
            ],
        ),
    },
)

admin_exam_submission_list_schema = extend_schema(
    tags=["admin_exams"],
    summary="어드민 응시 내역 목록 조회",
    description="쪽지시험 응시 내역을 조회합니다.",
    responses={
        200: AdminExamSubmissionListResponseSerializer,
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Bad Request",
            examples=[
                OpenApiExample(
                    "유효하지 않은 조회 요청",
                    value={"error_detail": ErrorMessages.INVALID_SUBMISSION_LIST_REQUEST.value},
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
                    value={"error_detail": ErrorMessages.NO_SUBMISSION_LIST_PERMISSION.value},
                ),
            ],
        ),
        404: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Not Found",
            examples=[
                OpenApiExample(
                    "응시 내역 없음",
                    value={"error_detail": ErrorMessages.SUBMISSION_LIST_NOT_FOUND.value},
                ),
            ],
        ),
    },
)

admin_exam_deployment_router_list_schema = extend_schema(
    tags=["admin_exams"],
    summary="어드민 배포 목록 조회",
    description="쪽지시험 배포 내역을 페이지네이션/검색/필터/정렬로 조회합니다.",
    parameters=[
        OpenApiParameter(name="page", required=False, type=int, description="페이지(1부터)"),
        OpenApiParameter(name="size", required=False, type=int, description="페이지 크기"),
        OpenApiParameter(name="search_keyword", required=False, type=str, description="검색어(시험 제목)"),
        OpenApiParameter(name="subject_id", required=False, type=int, description="과목 ID"),
        OpenApiParameter(name="cohort_id", required=False, type=int, description="기수 ID"),
        OpenApiParameter(
            name="sort",
            required=False,
            type=str,
            description="정렬 기준",
            enum=["created_at", "submit_count", "avg_score"],
        ),
        OpenApiParameter(name="order", required=False, type=str, description="정렬 방향", enum=["asc", "desc"]),
    ],
    responses={
        200: OpenApiResponse(description="OK"),
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Bad Request",
            examples=[
                OpenApiExample(
                    "유효하지 않은 조회 요청",
                    value={"error_detail": ErrorMessages.INVALID_DEPLOYMENT_LIST_REQUEST.value},
                )
            ],
        ),
        401: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Unauthorized",
            examples=[OpenApiExample("인증 실패", value={"error_detail": ErrorMessages.UNAUTHORIZED.value})],
        ),
        403: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Forbidden",
            examples=[
                OpenApiExample(
                    "권한 없음",
                    value={"error_detail": ErrorMessages.NO_DEPLOYMENT_LIST_PERMISSION.value},
                )
            ],
        ),
    },
)

admin_exam_deployment_router_create_schema = extend_schema(
    tags=["admin_exams"],
    summary="어드민 배포 생성",
    description="쪽지시험 배포를 생성합니다.",
    request=AdminExamDeploymentCreateRequestSerializer,
    responses={
        201: AdminExamDeploymentCreateResponseSerializer,
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Bad Request",
            examples=[
                OpenApiExample(
                    "유효하지 않은 배포 생성 요청",
                    value={"error_detail": ErrorMessages.INVALID_DEPLOYMENT_CREATE_REQUEST.value},
                )
            ],
        ),
        401: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Unauthorized",
            examples=[
                OpenApiExample(
                    "인증 실패",
                    value={"error_detail": ErrorMessages.UNAUTHORIZED.value},
                )
            ],
        ),
        403: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Forbidden",
            examples=[
                OpenApiExample(
                    "권한 없음",
                    value={"error_detail": ErrorMessages.NO_DEPLOYMENT_CREATE_PERMISSION.value},
                )
            ],
        ),
        404: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Not Found",
            examples=[
                OpenApiExample(
                    "배포 대상 없음",
                    value={"error_detail": ErrorMessages.DEPLOYMENT_TARGET_NOT_FOUND.value},
                )
            ],
        ),
        409: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Conflict",
            examples=[
                OpenApiExample(
                    "중복 배포",
                    value={"error_detail": ErrorMessages.DUPLICATE_DEPLOYMENT.value},
                )
            ],
        ),
    },
)

admin_exam_deployment_detail_schema = extend_schema(
    tags=["admin_exams"],
    operation_id="admin_exam_deployments_detail",
    summary="어드민 배포 상세 조회",
    description="쪽지시험 배포 상세 정보를 조회합니다.",
    responses={
        200: AdminExamDeploymentDetailResponseSerializer,
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Bad Request",
            examples=[
                OpenApiExample(
                    "유효하지 않은 배포 상세 조회 요청",
                    value={"error_detail": ErrorMessages.INVALID_DEPLOYMENT_DETAIL_REQUEST.value},
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
                    value={"error_detail": ErrorMessages.NO_DEPLOYMENT_DETAIL_PERMISSION.value},
                ),
            ],
        ),
        404: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Not Found",
            examples=[
                OpenApiExample(
                    "배포 정보 없음",
                    value={"error_detail": ErrorMessages.DEPLOYMENT_NOT_FOUND.value},
                ),
            ],
        ),
    },
)

admin_exam_deployment_update_schema = extend_schema(
    tags=["admin_exams"],
    operation_id="admin_exam_deployment_update",
    summary="어드민 배포 수정",
    description="쪽지시험 배포 정보(시작/종료 일시, 시험 시간)를 수정합니다.",
    request=AdminExamDeploymentUpdateRequestSerializer,
    responses={
        200: AdminExamDeploymentUpdateResponseSerializer,
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Bad Request",
            examples=[
                OpenApiExample(
                    "유효하지 않은 배포 수정 요청",
                    value={"error_detail": ErrorMessages.INVALID_DEPLOYMENT_UPDATE_REQUEST.value},
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
                    value={"error_detail": ErrorMessages.NO_DEPLOYMENT_UPDATE_PERMISSION.value},
                ),
            ],
        ),
        404: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Not Found",
            examples=[
                OpenApiExample(
                    "배포 정보 없음",
                    value={"error_detail": ErrorMessages.DEPLOYMENT_UPDATE_NOT_FOUND.value},
                ),
            ],
        ),
    },
)

admin_exam_deployment_delete_schema = extend_schema(
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

admin_exam_question_delete_schema = extend_schema(
    tags=["admin_exams"],
    summary="어드민 문제 삭제",
    description="쪽지시험 문제를 삭제합니다.",
    responses={
        200: AdminExamQuestionDeleteResponseSerializer,
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Bad Request",
            examples=[
                OpenApiExample(
                    "유효하지 않은 문제 삭제 요청",
                    value={"error_detail": ErrorMessages.INVALID_QUESTION_DELETE_REQUEST.value},
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
                    value={"error_detail": ErrorMessages.NO_QUESTION_DELETE_PERMISSION.value},
                ),
            ],
        ),
        404: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Not Found",
            examples=[
                OpenApiExample(
                    "문제 정보 없음",
                    value={"error_detail": ErrorMessages.QUESTION_NOT_FOUND.value},
                ),
            ],
        ),
        409: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Conflict",
            examples=[
                OpenApiExample(
                    "문제 삭제 충돌",
                    value={"error_detail": ErrorMessages.QUESTION_DELETE_CONFLICT.value},
                ),
            ],
        ),
    },
)

admin_exam_question_update_schema = extend_schema(
    tags=["admin_exams"],
    summary="쪽지시험 문제 수정 API",
    description="관리자/스태프가 쪽지시험 문제를 수정합니다.",
    request=AdminExamQuestionUpdateRequestSerializer,
    responses={
        200: AdminExamQuestionUpdateResponseSerializer,
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Bad Request",
            examples=[
                OpenApiExample(
                    "유효하지 않은 문제 수정 데이터",
                    value={"error_detail": ErrorMessages.INVALID_QUESTION_UPDATE_REQUEST.value},
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
                    value={"error_detail": ErrorMessages.NO_QUESTION_UPDATE_PERMISSION.value},
                ),
            ],
        ),
        404: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Not Found",
            examples=[
                OpenApiExample(
                    "문제 정보 찾을 수 없음",
                    value={"error_detail": ErrorMessages.QUESTION_UPDATE_NOT_FOUND.value},
                ),
            ],
        ),
        409: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Conflict",
            examples=[
                OpenApiExample(
                    "문제 수 제한 또는 총 배점을 초과하여 문제를 수정할 수 없음",
                    value={"error_detail": ErrorMessages.QUESTION_UPDATE_CONFLICT.value},
                ),
            ],
        ),
    },
)

admin_exam_submission_detail_schema = extend_schema(
    tags=["admin_exams"],
    summary="어드민 응시 내역 상세 조회",
    description="쪽지시험 응시 내역 상세 정보를 조회합니다.",
    responses={
        200: AdminExamSubmissionDetailResponseSerializer,
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Bad Request",
            examples=[
                OpenApiExample(
                    "유효하지 않은 상세 조회 요청",
                    value={"error_detail": ErrorMessages.INVALID_SUBMISSION_DETAIL_REQUEST.value},
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
                    value={"error_detail": ErrorMessages.NO_SUBMISSION_DETAIL_PERMISSION.value},
                ),
            ],
        ),
        404: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Not Found",
            examples=[
                OpenApiExample(
                    "응시 내역 없음",
                    value={"error_detail": ErrorMessages.SUBMISSION_DETAIL_NOT_FOUND.value},
                ),
            ],
        ),
    },
)

admin_exam_submission_delete_schema = extend_schema(
    tags=["admin_exams"],
    summary="어드민 응시 내역 삭제",
    description="쪽지시험 응시 내역을 삭제합니다.",
    responses={
        200: AdminExamSubmissionDeleteResponseSerializer,
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Bad Request",
            examples=[
                OpenApiExample(
                    "유효하지 않은 응시 내역 삭제 요청",
                    value={"error_detail": ErrorMessages.INVALID_SUBMISSION_DELETE_REQUEST.value},
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
                    value={"error_detail": ErrorMessages.NO_SUBMISSION_DELETE_PERMISSION.value},
                ),
            ],
        ),
        404: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Not Found",
            examples=[
                OpenApiExample(
                    "응시 내역 없음",
                    value={"error_detail": ErrorMessages.SUBMISSION_DELETE_NOT_FOUND.value},
                ),
            ],
        ),
        409: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Conflict",
            examples=[
                OpenApiExample(
                    "응시 내역 삭제 충돌",
                    value={"error_detail": ErrorMessages.SUBMISSION_DELETE_CONFLICT.value},
                ),
            ],
        ),
    },
)

admin_exam_list_schema = extend_schema(
    tags=["admin_exams"],
    summary="어드민 시험 목록 조회",
    description="어드민 시험 목록을 페이지네이션/검색/과목필터/정렬로 조회합니다.",
    parameters=[
        OpenApiParameter(name="page", required=False, type=int, description="페이지(1부터)"),
        OpenApiParameter(name="size", required=False, type=int, description="페이지 크기"),
        OpenApiParameter(name="search_keyword", required=False, type=str, description="검색어(시험 제목)"),
        OpenApiParameter(name="subject_id", required=False, type=int, description="과목 ID"),
        OpenApiParameter(
            name="sort",
            required=False,
            type=str,
            description="정렬 기준",
            enum=["created_at", "updated_at", "title"],
        ),
        OpenApiParameter(
            name="order",
            required=False,
            type=str,
            description="정렬 방향",
            enum=["asc", "desc"],
        ),
    ],
    responses={
        200: OpenApiResponse(
            description="OK",
            examples=[
                OpenApiExample(
                    "성공",
                    value={
                        "page": 1,
                        "size": 10,
                        "total_count": 42,
                        "exams": [
                            {
                                "id": 101,
                                "title": "Python 기본 문법 테스트",
                                "subject_name": "Python",
                                "question_count": 20,
                                "submit_count": 65,
                                "created_at": "2025-02-01 13:20:33",
                                "updated_at": "2025-02-05 15:10:20",
                                "detail_url": "/admin/exams/101",
                            }
                        ],
                    },
                )
            ],
        ),
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Bad Request",
            examples=[
                OpenApiExample(
                    "유효하지 않은 조회 요청",
                    value={"error_detail": ErrorMessages.INVALID_EXAM_LIST_REQUEST.value},
                )
            ],
        ),
        401: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Unauthorized",
            examples=[
                OpenApiExample(
                    "인증 실패",
                    value={"error_detail": ErrorMessages.UNAUTHORIZED.value},
                )
            ],
        ),
        403: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Forbidden",
            examples=[
                OpenApiExample(
                    "권한 없음",
                    value={"error_detail": ErrorMessages.NO_EXAM_LIST_PERMISSION.value},
                )
            ],
        ),
    },
)

admin_exam_create_schema = extend_schema(
    tags=["admin_exams"],
    summary="어드민 시험 생성",
    description="관리자/스태프 권한으로 쪽지시험을 생성합니다. 썸네일 이미지는 선택 입력입니다.",
    request=AdminExamCreateRequestSerializer,
    responses={
        201: AdminExamCreateResponseSerializer,
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Bad Request",
            examples=[
                OpenApiExample(
                    "유효하지 않은 시험 생성 요청",
                    value={"error_detail": ErrorMessages.INVALID_EXAM_CREATE_REQUEST.value},
                )
            ],
        ),
        401: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Unauthorized",
            examples=[
                OpenApiExample(
                    "인증 실패",
                    value={"error_detail": ErrorMessages.UNAUTHORIZED.value},
                )
            ],
        ),
        403: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Forbidden",
            examples=[
                OpenApiExample(
                    "권한 없음",
                    value={"error_detail": ErrorMessages.NO_EXAM_CREATE_PERMISSION.value},
                )
            ],
        ),
        404: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Not Found",
            examples=[
                OpenApiExample(
                    "과목 정보 없음",
                    value={"error_detail": ErrorMessages.SUBJECT_NOT_FOUND.value},
                )
            ],
        ),
        409: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Conflict",
            examples=[
                OpenApiExample(
                    "시험 이름 중복",
                    value={"error_detail": ErrorMessages.EXAM_CONFLICT.value},
                )
            ],
        ),
    },
)

admin_exam_deployment_create_schema = extend_schema(
    tags=["admin_exams"],
    summary="어드민 배포 생성",
    description="쪽지시험 배포를 생성합니다.",
    request=AdminExamDeploymentCreateRequestSerializer,
    responses={
        201: AdminExamDeploymentCreateResponseSerializer,
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Bad Request",
            examples=[
                OpenApiExample(
                    "유효하지 않은 배포 생성 요청",
                    value={"error_detail": ErrorMessages.INVALID_DEPLOYMENT_CREATE_REQUEST.value},
                )
            ],
        ),
        401: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Unauthorized",
            examples=[
                OpenApiExample(
                    "인증 실패",
                    value={"error_detail": ErrorMessages.UNAUTHORIZED.value},
                )
            ],
        ),
        403: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Forbidden",
            examples=[
                OpenApiExample(
                    "권한 없음",
                    value={"error_detail": ErrorMessages.NO_DEPLOYMENT_CREATE_PERMISSION.value},
                )
            ],
        ),
        404: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Not Found",
            examples=[
                OpenApiExample(
                    "배포 대상 없음",
                    value={"error_detail": ErrorMessages.DEPLOYMENT_TARGET_NOT_FOUND.value},
                )
            ],
        ),
        409: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Conflict",
            examples=[
                OpenApiExample(
                    "중복 배포",
                    value={"error_detail": ErrorMessages.DUPLICATE_DEPLOYMENT.value},
                )
            ],
        ),
    },
)

admin_exam_deployment_list_schema = extend_schema(
    tags=["admin_exams"],
    operation_id="admin_exam_deployments_list",
    summary="어드민 배포 목록 조회",
    description="쪽지시험 배포 내역을 페이지네이션/검색/필터/정렬로 조회합니다.",
    parameters=[
        OpenApiParameter(name="page", required=False, type=int, description="페이지(1부터)"),
        OpenApiParameter(name="size", required=False, type=int, description="페이지 크기"),
        OpenApiParameter(name="search_keyword", required=False, type=str, description="검색어(시험 제목)"),
        OpenApiParameter(name="subject_id", required=False, type=int, description="과목 ID"),
        OpenApiParameter(name="cohort_id", required=False, type=int, description="기수 ID"),
        OpenApiParameter(
            name="sort",
            required=False,
            type=str,
            description="정렬 기준",
            enum=["created_at", "submit_count", "avg_score"],
        ),
        OpenApiParameter(name="order", required=False, type=str, description="정렬 방향", enum=["asc", "desc"]),
    ],
    responses={
        200: OpenApiResponse(description="OK"),
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Bad Request",
            examples=[
                OpenApiExample(
                    "유효하지 않은 조회 요청",
                    value={"error_detail": ErrorMessages.INVALID_DEPLOYMENT_LIST_REQUEST.value},
                )
            ],
        ),
        401: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Unauthorized",
            examples=[OpenApiExample("인증 실패", value={"error_detail": ErrorMessages.UNAUTHORIZED.value})],
        ),
        403: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Forbidden",
            examples=[
                OpenApiExample(
                    "권한 없음",
                    value={"error_detail": ErrorMessages.NO_DEPLOYMENT_LIST_PERMISSION.value},
                )
            ],
        ),
    },
)

admin_exam_update_schema = extend_schema(
    tags=["admin_exams"],
    summary="쪽지시험 수정 API",
    description="스태프/관리자 권한을 가진 사용자가 쪽지시험 정보를 수정합니다.",
    request=AdminExamUpdateRequestSerializer,
    responses={
        200: AdminExamUpdateResponseSerializer,
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Bad Request",
            examples=[
                OpenApiExample(
                    "유효하지 않은 요청",
                    value={"error_detail": ErrorMessages.INVALID_EXAM_UPDATE_REQUEST.value},
                )
            ],
        ),
        401: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Unauthorized",
            examples=[
                OpenApiExample(
                    "인증 실패",
                    value={"error_detail": ErrorMessages.UNAUTHORIZED.value},
                )
            ],
        ),
        403: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Forbidden",
            examples=[
                OpenApiExample(
                    "권한 없음",
                    value={"error_detail": ErrorMessages.NO_EXAM_UPDATE_PERMISSION.value},
                )
            ],
        ),
        404: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Not Found",
            examples=[
                OpenApiExample(
                    "쪽지시험 정보 없음",
                    value={"error_detail": ErrorMessages.EXAM_UPDATE_NOT_FOUND.value},
                )
            ],
        ),
        409: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Conflict",
            examples=[
                OpenApiExample(
                    "시험 이름 중복",
                    value={"error_detail": ErrorMessages.EXAM_UPDATE_CONFLICT.value},
                )
            ],
        ),
    },
)

admin_exam_delete_schema = extend_schema(
    tags=["admin_exams"],
    summary="쪽지시험 삭제 API",
    description="스태프/관리자 권한을 가진 사용자가 단일 시험을 삭제합니다.",
    responses={
        200: AdminExamDeleteResponseSerializer,
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Bad Request",
            examples=[
                OpenApiExample(
                    "유효하지 않은 요청",
                    value={"error_detail": ErrorMessages.INVALID_EXAM_DELETE_REQUEST.value},
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
                    value={"error_detail": ErrorMessages.NO_EXAM_DELETE_PERMISSION.value},
                ),
            ],
        ),
        404: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Not Found",
            examples=[
                OpenApiExample(
                    "시험 정보 없음",
                    value={"error_detail": ErrorMessages.EXAM_DELETE_NOT_FOUND.value},
                ),
            ],
        ),
        409: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Conflict",
            examples=[
                OpenApiExample(
                    "삭제 충돌",
                    value={"error_detail": ErrorMessages.EXAM_DELETE_CONFLICT.value},
                ),
            ],
        ),
    },
)

admin_exam_presigned_url_schema = extend_schema(
    summary="시험 썸네일 업로드 URL 발급",
    description="""
    S3의 exams 경로로 시험 썸네일을 업로드하기 위한 presigned URL을 발급합니다.
    스태프/관리자 권한만 사용 가능합니다.
    """,
    request=PresignedUrlRequestSerializer,
    responses={
        200: OpenApiResponse(
            description="OK",
            response=PresignedUrlResponseSerializer,
        ),
        400: OpenApiResponse(description="Bad Request"),
        401: OpenApiResponse(description="Unauthorized"),
        403: OpenApiResponse(description="Forbidden"),
    },
    tags=["admin_exams"],
)
