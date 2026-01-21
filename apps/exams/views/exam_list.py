from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from rest_framework.generics import ListAPIView
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.exams.models.exam_submissions import ExamSubmission
from apps.exams.pagination import SimplePagePagination
from apps.exams.serializers.exam_list import ExamListSerializer
from apps.exams.serializers.error import ErrorDetailSerializer


class ExamListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ExamListSerializer
    pagination_class = SimplePagePagination

    @extend_schema(
        summary="시험 목록",
        parameters=[],
        responses={
            200: ExamListSerializer,
            401: OpenApiResponse(
                response=ErrorDetailSerializer,
                description="Unauthorized",
                examples=[
                    OpenApiExample(
                        "401 Unauthorized",
                        value={"error_detail": "자격 인증 데이터가 제공되지 않았습니다."},
                    )
                ],
            ),
            403: OpenApiResponse(
                response=ErrorDetailSerializer,
                description="Forbidden",
                examples=[
                    OpenApiExample(
                        "403 Forbidden",
                        value={"error_detail": "권한이 없습니다."},
                    )
                ],
            ),
            404: OpenApiResponse(
                response=ErrorDetailSerializer,
                description="Not Found",
                examples=[
                    OpenApiExample(
                        "404 Not Found",
                        value={"error_detail": "사용자 정보를 찾을 수 없습니다."},
                    )
                ],
            ),
        },
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        status_param = self.request.query_params.get("status", "all").lower()
        if status_param not in ("all", "done", "pending"):
            raise ValidationError({"status": "status는 all/done/pending 중 하나여야 합니다."})

        qs = (
            ExamSubmission.objects
            .select_related("deployment__exam__subject")
            .order_by("-created_at")
        )

        if self.request.user.is_authenticated:
            qs = qs.filter(submitter=self.request.user)

        if status_param == "done":
            qs = qs.exclude(answers_json={})
        elif status_param == "pending":
            qs = qs.filter(answers_json={})

        return qs