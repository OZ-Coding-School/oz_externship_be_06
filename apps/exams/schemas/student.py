from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)

from apps.exams.constants import ErrorMessages
from apps.exams.serializers import (
    CheckCodeRequestSerializer,
    ExamSubmissionCreateResponseSerializer,
    ExamSubmissionCreateSerializer,
    TakeExamResponseSerializer,
)
from apps.exams.serializers.error_serializers import ErrorResponseSerializer
from apps.exams.serializers.student.deployments_cheating import (
    ExamCheatingRequestSerializer,
    ExamCheatingResponseSerializer,
)
from apps.exams.serializers.student.deployments_list import ExamDeploymentListSerializer
from apps.exams.serializers.student.deployments_status import ExamStatusResponseSerializer
from apps.exams.serializers.student.submissions_result import ExamSubmissionSerializer


exam_status_check_schema = extend_schema(
    tags=["exams"],
    summary="시험 상태 확인",
    description="응시 세션의 현재 시험 상태를 조회합니다.",
    responses={
        200: ExamStatusResponseSerializer,
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
                    value={"error_detail": ErrorMessages.FORBIDDEN.value},
                ),
            ],
        ),
        404: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Not Found",
            examples=[
                OpenApiExample(
                    "시험 정보 없음",
                    value={"error_detail": ErrorMessages.EXAM_NOT_FOUND.value},
                ),
            ],
        ),
    },
)

exam_submission_create_schema = extend_schema(
    tags=["exams"],
    summary="쪽지시험 제출 API",
    description="""
    로그인한 사용자가 쪽지시험 답안을 제출합니다.
    제출 후 즉시 채점이 수행되며 점수와 정답 개수가 반환됩니다.
    """,
    request=ExamSubmissionCreateSerializer,
    responses={
        201: ExamSubmissionCreateResponseSerializer,
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Bad Request",
            examples=[
                OpenApiExample(
                    "유효하지 않은 시험 응시 세션",
                    value={"error_detail": ErrorMessages.INVALID_EXAM_SESSION.value},
                ),
                OpenApiExample(
                    "주관식 단답형 타입 오류",
                    value={"error_detail": ErrorMessages.INVALID_SHORT_ANSWER_TYPE.value},
                ),
                OpenApiExample(
                    "주관식 단답형 길이 초과",
                    value={"error_detail": ErrorMessages.INVALID_SHORT_ANSWER_LENGTH.value},
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
                    value={"error_detail": ErrorMessages.FORBIDDEN.value},
                ),
            ],
        ),
        404: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Not Found",
            examples=[
                OpenApiExample(
                    "시험 정보 없음",
                    value={"error_detail": ErrorMessages.EXAM_NOT_FOUND.value},
                ),
            ],
        ),
        409: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Conflict",
            examples=[
                OpenApiExample(
                    "이미 제출됨",
                    value={"error_detail": ErrorMessages.SUBMISSION_ALREADY_SUBMITTED.value},
                ),
            ],
        ),
    },
)

take_exam_schema = extend_schema(
    tags=["exams"],
    summary="시험 응시 문제 조회",
    description="시험 응시 화면에서 필요한 문제 및 상태 정보를 조회합니다.",
    responses={
        200: TakeExamResponseSerializer,
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
                    value={"error_detail": ErrorMessages.FORBIDDEN.value},
                ),
            ],
        ),
        404: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Not Found",
            examples=[
                OpenApiExample(
                    "시험 정보 없음",
                    value={"error_detail": ErrorMessages.EXAM_NOT_FOUND.value},
                ),
            ],
        ),
        410: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Gone",
            examples=[
                OpenApiExample(
                    "시험 종료",
                    value={"error_detail": ErrorMessages.EXAM_CLOSED.value},
                ),
            ],
        ),
    },
)

check_code_schema = extend_schema(
    tags=["exams"],
    summary="시험 참가 코드 검증",
    description="시험 응시를 위한 참가 코드를 검증합니다.",
    request=CheckCodeRequestSerializer,
    responses={
        204: OpenApiResponse(description="No Content"),
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Bad Request",
            examples=[
                OpenApiExample(
                    "코드 불일치",
                    value={"error_detail": ErrorMessages.INVALID_CHECK_CODE_REQUEST.value},
                ),
                OpenApiExample(
                    "필드 누락",
                    value={"error_detail": {"code": "이 필드는 필수 항목입니다."}},
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
                    value={"error_detail": ErrorMessages.NO_EXAM_TAKE_PERMISSION.value},
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
        423: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Locked",
            examples=[
                OpenApiExample(
                    "응시 불가",
                    value={"error_detail": ErrorMessages.EXAM_NOT_AVAILABLE.value},
                ),
            ],
        ),
    },
)

exam_cheating_update_schema = extend_schema(
    tags=["exams"],
    summary="부정행위 횟수 갱신",
    description="부정행위 횟수를 증가시키고 강제 제출 여부를 판단합니다.",
    request=ExamCheatingRequestSerializer,
    responses={
        200: ExamCheatingResponseSerializer,
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
                    value={"error_detail": ErrorMessages.FORBIDDEN.value},
                ),
            ],
        ),
        404: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Not Found",
            examples=[
                OpenApiExample(
                    "시험 정보 없음",
                    value={"error_detail": ErrorMessages.EXAM_NOT_FOUND.value},
                ),
            ],
        ),
        409: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Conflict",
            examples=[
                OpenApiExample(
                    "이미 제출됨",
                    value={"error_detail": ErrorMessages.SUBMISSION_ALREADY_SUBMITTED.value},
                ),
            ],
        ),
        410: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Gone",
            examples=[
                OpenApiExample(
                    "시험 종료",
                    value={"error_detail": ErrorMessages.EXAM_ALREADY_CLOSED.value},
                ),
            ],
        ),
    },
)

exam_submission_detail_schema = extend_schema(
    tags=["exams"],
    summary="시험 제출 결과 상세 조회",
    description="submission_id로 시험 제출(결과) 상세 정보를 조회합니다.",
    responses={
        200: ExamSubmissionSerializer,
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Bad Request",
            examples=[
                OpenApiExample(
                    "유효하지 않은 시험 응시 세션",
                    value={"error_detail": ErrorMessages.INVALID_EXAM_SESSION.value},
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
                    value={"error_detail": ErrorMessages.FORBIDDEN.value},
                ),
            ],
        ),
        404: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Not Found",
            examples=[
                OpenApiExample(
                    "시험 정보 없음",
                    value={"error_detail": ErrorMessages.SUBMISSION_DETAIL_NOT_FOUND.value},
                ),
            ],
        ),
    },
)

exam_deployment_list_schema = extend_schema(
    tags=["exams"],
    summary="시험 배포 목록 조회",
    description="현재 로그인한 사용자의 코호트 기준으로 시험 목록을 조회합니다.",
    parameters=[
        OpenApiParameter(
            name="status",
            description="시험 상태 필터",
            required=False,
            type=str,
            enum=["all", "done", "pending"],
            default="all",
        ),
    ],
    responses={
        200: ExamDeploymentListSerializer,
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
                    value={"error_detail": ErrorMessages.FORBIDDEN.value},
                )
            ],
        ),
        404: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Not Found",
            examples=[
                OpenApiExample(
                    "코호트 없음/잘못된 요청",
                    value={"error_detail": ErrorMessages.USER_NOT_FOUND.value},
                ),
                OpenApiExample(
                    "잘못된 status",
                    value={"error_detail": ErrorMessages.INVALID_EXAM_LIST_REQUEST.value},
                ),
            ],
        ),
    },
)
