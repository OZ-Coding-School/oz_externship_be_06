from typing import Any, Never, cast

from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.posts.constants.post_const import PostErrorMessage, PostSuccessMessage
from apps.posts.exceptions.post_exceptions import (
    PostPermissionDeniedException,
    PostUnauthorizedException,
)
from apps.posts.models import Post
from apps.posts.selectors.post_selectors import PostSelector
from apps.posts.serializers.post_serializers import (
    PostCreateSerializer,
    PostDetailSerializer,
    PostFilterSerializer,
    PostListSerializer,
    PostUpdateSerializer,
)
from apps.posts.services.post_services import PostService
from apps.posts.utils.pagination import PostPagination
from apps.users.models import User


class PostListCreateView(APIView):

    def permission_denied(self, request: Request, message: str | None = None, code: str | None = None) -> Never:
        raise PostUnauthorizedException()

    def get_permissions(self) -> list[Any]:
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return [AllowAny()]

    @extend_schema(
        summary="게시글 목록 조회",
        description=(
            "다양한 필터링 및 정렬 조건을 사용하여 게시글 목록을 조회합니다.\n"
            "- **Pagination**: 기본적으로 페이징 처리가 적용되어 반환됩니다.\n"
            "- **Filtering**: 카테고리별, 검색어별 필터링을 지원합니다.\n"
            "- **Sorting**: 최신순, 좋아요순, 댓글순, 오래된순 정렬을 지원합니다."
        ),
        parameters=[
            OpenApiParameter(
                name="category_id", type=int, description="특정 카테고리의 게시글만 필터링합니다. (ID 값)"
            ),
            OpenApiParameter(name="search", type=str, description="검색 키워드를 입력합니다."),
            OpenApiParameter(
                name="search_filter",
                type=str,
                enum=["author", "title", "content", "title_or_content"],
                default="title_or_content",
                description="검색 범위 설정",
            ),
            OpenApiParameter(
                name="sort",
                type=str,
                enum=["latest", "oldest", "most_views", "most_likes", "most_comments"],
                default="latest",
                description="데이터 정렬 기준",
            ),
        ],
        responses={
            200: PostListSerializer(many=True),
            400: OpenApiResponse(description="잘못된 쿼리 파라미터 요청 (유효성 검사 실패)"),
            401: OpenApiResponse(description="인증 정보 유효하지 않음 (게시글 작성 시 발생 가능)"),
        },
        tags=["posts"],
    )
    def get(self, request: Request) -> Response:
        filter_serializer = PostFilterSerializer(data=request.query_params)

        if not filter_serializer.is_valid():
            return Response({"error_detail": filter_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        validated_data = filter_serializer.validated_data

        posts = PostSelector.get_post_list(
            category_id=validated_data.get("category_id"),
            search=validated_data.get("search"),
            search_filter=validated_data.get("search_filter"),
            sort=validated_data.get("sort"),
            user_id=request.user.id if request.user.is_authenticated else None,
        )

        paginator = PostPagination()
        page = paginator.paginate_queryset(posts, request, view=self)

        if page is not None:
            serializer = PostListSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="게시글 생성",
        request=PostCreateSerializer,
        responses={
            201: OpenApiResponse(
                description="게시글 생성 성공",
                response={
                    "type": "object",
                    "properties": {
                        "detail": {"type": "string", "example": PostSuccessMessage.POST_CREATE_SUCCESS},
                        "pk": {"type": "integer", "example": 1},
                    },
                },
            ),
            400: OpenApiResponse(
                description="입력값 유효성 검증 실패 (필드 누락, 잘못된 타입 등)",
                response={
                    "type": "object",
                    "properties": {
                        "error_detail": {
                            "type": "object",
                            "example": {
                                "title": ["이 필드는 필수 항목입니다."],
                                "category_id": ["유효한 정수를 입력하십시오."],
                            },
                        }
                    },
                },
            ),
            401: OpenApiResponse(description="인증 자격 증명이 유효하지 않음"),
            500: OpenApiResponse(
                description="서버 내부 오류",
                response={
                    "type": "object",
                    "properties": {"error_detail": {"type": "string", "example": PostErrorMessage.SERVER_ERROR}},
                },
            ),
        },
        tags=["posts"],
    )
    def post(self, request: Request) -> Response:
        user = cast(User, request.user)
        serializer = PostCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({"error_detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        try:
            post = PostService.create_post(user=user, **serializer.validated_data)
            return Response(
                {"detail": PostSuccessMessage.POST_CREATE_SUCCESS, "pk": post.id}, status=status.HTTP_201_CREATED
            )
        except Exception:
            return Response(
                {"error_detail": PostErrorMessage.SERVER_ERROR}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PostDetailView(APIView):
    """
    GET: 게시글 상세 조회 및 조회수 증가 (AllowAny)
    POST: 게시글 삭제 (IsAuthenticated)
    """

    def get_permissions(self) -> list[Any]:
        if self.request.method in ["PUT", "DELETE"]:
            return [IsAuthenticated()]
        return [AllowAny()]

    @extend_schema(
        summary="게시글 상세 조회",
        responses={200: PostDetailSerializer},
        tags=["posts"],
    )
    def get(self, request: Request, post_id: int) -> Response:
        user_id = request.user.id if request.user.is_authenticated else None

        post = PostSelector.get_post_detail(post_id=post_id, user_id=user_id)
        PostService.increment_view_count(post)

        post = PostSelector.get_post_detail(post_id=post_id, user_id=user_id)

        serializer = PostDetailSerializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="게시글 수정", request=PostUpdateSerializer, responses={200: PostDetailSerializer}, tags=["posts"]
    )
    def put(self, request: Request, post_id: int) -> Response:
        user: User = cast(User, request.user)

        post = PostSelector.get_post_detail(post_id=post_id)

        serializer: PostUpdateSerializer = PostUpdateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({"error_detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        updated_post: Post = PostService.update_post(user=user, post=post, **serializer.validated_data)
        return Response(
            PostUpdateSerializer(updated_post).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="게시글 삭제",
        tags=["posts"],
    )
    def delete(self, request: Request, post_id: int) -> Response:
        """
        게시글 삭제
        """
        user = cast(User, request.user)

        PostService.delete_post(post_id=post_id, user=user)

        return Response({"detail": PostSuccessMessage.POST_DELETE_SUCCESS}, status=status.HTTP_200_OK)
