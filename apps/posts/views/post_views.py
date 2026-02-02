from typing import Any, Never, cast

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.posts.constants.post_const import PostErrorMessage, PostSuccessMessage
from apps.posts.exceptions.post_exceptions import PostUnauthorizedException
from apps.posts.selectors.post_selectors import PostSelector
from apps.posts.serializers.post_serializers import (
    PostCreateSerializer,
    PostListSerializer,
)
from apps.posts.services.post_services import PostService
from apps.posts.utils.pagination import PostPagination
from apps.users.models import User


class PostListCreateView(APIView):
    """
    GET: 게시글 목록 조회 (AllowAny)
    POST: 게시글 작성 (IsAuthenticated)
    """

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> Never:
        raise PostUnauthorizedException()

    def get_permissions(self) -> list[Any]:
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]

    @extend_schema(
        summary="게시글 목록 조회",
        parameters=[
            OpenApiParameter(name="category_id", type=int, description="카테고리 ID 필터")
        ],
        responses={200: PostListSerializer(many=True)},
        tags=["posts"]
    )
    def get(self, request: Request) -> Response:
        category_id_param = request.query_params.get('category_id')
        category_id = int(category_id_param) if category_id_param else None

        posts = PostSelector.get_post_list(category_id=category_id)
        paginator = PostPagination()
        page = paginator.paginate_queryset(posts, request, view=self)

        if page is not None:
            serializer = PostListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(summary="게시글 생성", request=PostCreateSerializer, tags=["posts"])
    def post(self, request: Request) -> Response:
        user = cast(User, request.user)
        serializer = PostCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({"error_detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        try:
            post = PostService.create_post(user=user, **serializer.validated_data)
            return Response(
                {"detail": PostSuccessMessage.POST_CREATE_SUCCESS, "pk": post.id},
                status=status.HTTP_201_CREATED
            )
        except Exception:
            return Response(
                {"error_detail": PostErrorMessage.SERVER_ERROR},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )