from typing import Any, Dict, List, Optional, Type

from django.db.models import Count, Q, QuerySet
from drf_spectacular.utils import extend_schema, extend_schema_view, inline_serializer
from rest_framework import filters, permissions, status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import (
    BaseSerializer,
    CharField,
    IntegerField,
    JSONField,
)

from ..models.post import Post
from ..serializers.post_serializers import (
    PostCreateUpdateSerializer,
    PostDetailSerializer,
    PostListSerializer,
)
from .post_permissions import IsAuthorOrReadOnly


@extend_schema_view(
    list=extend_schema(
        summary="게시글 목록 조회", description="모든 게시글을 조회하며, 필터링 및 정렬 기능을 지원합니다."
    ),
    retrieve=extend_schema(
        summary="게시글 상세 조회", description="특정 ID의 게시글 상세 정보를 조회하며, 조회수가 1 증가합니다."
    ),
    create=extend_schema(
        summary="게시글 작성",
        responses={
            201: inline_serializer(name="PostCreateResponse", fields={"detail": CharField(), "pk": IntegerField()}),
            400: inline_serializer(name="PostErrorResponse", fields={"error_detail": JSONField()}),
        },
    ),
    update=extend_schema(
        summary="게시글 수정",
        responses={
            200: inline_serializer(
                name="PostUpdateResponse",
                fields={
                    "id": IntegerField(),
                    "title": CharField(),
                    "content": CharField(),
                    "category_id": IntegerField(),
                },
            ),
            400: inline_serializer(name="PostUpdateErrorResponse", fields={"error_detail": JSONField()}),
        },
    ),
    destroy=extend_schema(
        summary="게시글 삭제",
        responses={
            200: inline_serializer(name="PostDeleteResponse", fields={"detail": CharField()}),
            401: inline_serializer(name="Error401Response", fields={"error_detail": CharField()}),
            403: inline_serializer(name="Error403Response", fields={"error_detail": CharField()}),
            404: inline_serializer(name="Error404Response", fields={"error_detail": CharField()}),
        },
    ),
)
@extend_schema(tags=["posts"])
class PostViewSet(viewsets.ModelViewSet[Post]):
    queryset = Post.objects.annotate(
        comment_count=Count("comments", distinct=True),
        like_count=Count("likes", filter=Q(likes__is_liked=True), distinct=True),
    )
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "content", "author__nickname"]
    ordering_fields = ["created_at", "view_count", "like_count", "comment_count"]
    ordering = ["-created_at"]
    http_method_names = ["get", "post", "put", "delete", "head", "options"]

    def handle_exception(self, exc: Exception) -> Response:
        """
        이 ViewSet 내에서 발생하는 예외만 가공합니다.
        타 앱(exams, qna 등)에는 전혀 영향을 주지 않습니다.
        """
        response = super().handle_exception(exc)

        if response is not None and isinstance(response.data, dict):
            detail = response.data.get("detail", response.data)
            response.data = {"error_detail": detail}

        return response

    def get_queryset(self) -> QuerySet[Post]:
        queryset: QuerySet[Post] = super().get_queryset()
        category_id = self.request.query_params.get("category_id")
        if category_id:
            queryset = queryset.filter(category_id=int(category_id))
        return queryset

    def get_permissions(self) -> List[permissions.BasePermission]:
        if self.action in ["create", "update", "destroy"]:
            return [permissions.IsAuthenticated(), IsAuthorOrReadOnly()]
        return [permissions.AllowAny()]

    def get_serializer_class(self) -> Type[BaseSerializer[Post]]:
        if self.action in ["create", "update"]:
            return PostCreateUpdateSerializer
        if self.action == "retrieve":
            return PostDetailSerializer
        return PostListSerializer

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        instance = serializer.instance
        if instance is None:
            return Response(
                {"error_detail": "데이터 생성에 실패했습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        return Response(
            {"detail": "게시글이 성공적으로 등록되었습니다.", "pk": instance.id}, status=status.HTTP_201_CREATED
        )

    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        if not serializer.is_valid():
            return Response({"error_detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        self.perform_update(serializer)
        return Response(
            {
                "id": instance.id,
                "title": str(serializer.data.get("title")),
                "content": str(serializer.data.get("content")),
                "category_id": int(serializer.data.get("category_id", 0)),
            },
            status=status.HTTP_200_OK,
        )

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"detail": "게시글이 삭제되었습니다."}, status=status.HTTP_200_OK)

    def perform_create(self, serializer: BaseSerializer[Post]) -> None:
        serializer.save(author=self.request.user)

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        instance = self.get_object()
        instance.view_count += 1
        instance.save()
        return super().retrieve(request, *args, **kwargs)
