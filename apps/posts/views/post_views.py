from typing import Any, Dict, List, Optional, Type

from django.db.models import F, QuerySet
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


class PostOrderingFilter(filters.OrderingFilter):
    ordering_param: str = "sort"

    def get_ordering(self, request: Request, queryset: QuerySet[Post], view: Any) -> Optional[List[str]]:
        params = request.query_params.get(self.ordering_param)

        if params:
            mapping: Dict[str, str] = {
                "latest": "-created_at",
                "most_views": "-view_count",
                "most_likes": "-like_count",
                "most_comments": "-comment_count",
            }
            sort_field = mapping.get(params)
            if sort_field:
                return [sort_field]

        return ["-created_at"]


class PostSearchFilter(filters.SearchFilter):
    search_type_param = "search_type"

    def get_search_fields(self, view: Any, request: Request) -> List[str]:
        search_type: Optional[str] = request.query_params.get(self.search_type_param)

        mapping: Dict[str, List[str]] = {
            "author": ["author__nickname"],
            "title": ["title"],
            "content": ["content"],
            "title_or_content": ["title", "content"],
        }

        if search_type and search_type in mapping:
            return mapping[search_type]

        return ["title", "content", "author__nickname"]


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
        responses={200: inline_serializer(name="PostDeleteResponse", fields={"detail": CharField()})},
    ),
)
@extend_schema(tags=["posts"])
class PostViewSet(viewsets.ModelViewSet[Post]):
    queryset = Post.objects.all()
    filter_backends = [PostSearchFilter, PostOrderingFilter]
    search_fields = ["title", "content", "author__nickname"]

    ordering_fields = ["latest", "most_views", "most_likes", "most_comments"]
    ordering = ["latest"]

    http_method_names = ["get", "post", "put", "delete", "head", "options"]

    def get_queryset(self) -> QuerySet[Post]:
        return Post.objects.select_related("author").all()

    def handle_exception(self, exc: Exception) -> Response:
        """
        PostViewSet 내에서 발생하는 404, 401, 403 등 모든 예외를
        {"error_detail": "메시지"} 형식으로 변환합니다.
        """
        response = super().handle_exception(exc)

        if response is not None:
            if isinstance(response.data, dict):
                detail = response.data.get("detail", response.data)
            else:
                detail = response.data

            response.data = {"error_detail": detail}

        return response

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

        instance.view_count = F("view_count") + 1
        instance.save(update_fields=["view_count"])

        instance.refresh_from_db()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)
