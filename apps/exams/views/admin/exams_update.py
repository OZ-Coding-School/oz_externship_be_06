# from typing import NoReturn
#
# from drf_spectacular.utils import OpenApiResponse, extend_schema, OpenApiExample
# from rest_framework import status
# from rest_framework.exceptions import NotAuthenticated, PermissionDenied
# from rest_framework.request import Request
# from rest_framework.response import Response
# from rest_framework.views import APIView
#
# from apps.exams.constants import ErrorMessages
# from apps.core.utils.permissions import IsStaffRole
# from apps.exams.serializers import (
#     AdminExamUpdateRequestSerializer,
#     AdminExamUpdateResponseSerializer,
#     ErrorResponseSerializer,
# )
# from apps.exams.services.admin.exams_update import update_exam
#
#
# @extend_schema(
#     tags=["admin_exams"],
#     summary="쪽지시험 수정 API",
#     description="스태프/관리자 권한을 가진 사용자가 쪽지시험 정보를 수정합니다.",
#     request=AdminExamUpdateRequestSerializer,
#     responses={
#         200: AdminExamUpdateResponseSerializer,
#         400: OpenApiResponse(
#             response=ErrorResponseSerializer,
#             description="Bad Request",
#             examples=[
#                 OpenApiExample(
#                 "유효하지 않은 요청", value={"error_detail": ErrorMessages.INVALID_EXAM_UPDATE_REQUEST.value}
#                 )
#             ],
#         ),
#         401: OpenApiResponse(
#             response=ErrorResponseSerializer,
#             description="Unauthorized",
#             examples=[
#                 OpenApiExample(
#                 "인증 실패", value={"error_detail": ErrorMessages.UNAUTHORIZED.value}
#                 )
#             ],
#         ),
#         403: OpenApiResponse(
#             response=ErrorResponseSerializer,
#             description="Forbidden",
#             examples=[
#                 OpenApiExample(
#                 "권한 없음", value={"error_detail": ErrorMessages.NO_EXAM_UPDATE_PERMISSION.value}
#                 )
#             ],
#         ),
#         404: OpenApiResponse(
#             response=ErrorResponseSerializer,
#             description="Not Found",
#             examples=[
#                 OpenApiExample(
#                 "쪽지시험 정보 없음", value={"error_detail": ErrorMessages.EXAM_UPDATE_NOT_FOUND.value}
#                 )
#             ],
#         ),
#         409: OpenApiResponse(
#             response=ErrorResponseSerializer,
#             description="Conflict",
#             examples=[
#                 OpenApiExample(
#                 "시험 이름 중복", value={"error_detail": ErrorMessages.EXAM_UPDATE_CONFLICT.value}
#                 )
#             ],
#         ),
#     },
# )
# class AdminExamUpdateAPIView(APIView):
#     permission_classes = [IsStaffRole]  # 스태프/관리자 권한 (403 권한 체크)
#
#     # 401/403
#     def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> NoReturn:
#         if not request.user or not request.user.is_authenticated:
#             raise NotAuthenticated(detail=ErrorMessages.UNAUTHORIZED.value)
#         raise PermissionDenied(detail=ErrorMessages.NO_EXAM_UPDATE_PERMISSION.value)
#
#     def put(self, request: Request, exam_id: int) -> Response:
#         # 400 Serializer 검증
#         serializer = AdminExamUpdateRequestSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#
#         # 404/409 Service 호출
#         exam = update_exam(
#             exam_id=exam_id,
#             **serializer.validated_data,
#         )
#
#         response_serializer = AdminExamUpdateResponseSerializer(exam)
#         return Response(response_serializer.data, status=status.HTTP_200_OK)
