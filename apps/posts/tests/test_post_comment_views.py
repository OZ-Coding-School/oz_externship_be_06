from typing import Any

from django.db.models import QuerySet
from django.utils import timezone
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    inline_serializer,
)
from rest_framework import generics, parsers, serializers, status
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, BasePermission
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.posts.constants.post_const import PostErrorMessage
from apps.posts.models.post import Post
from apps.posts.models.post_comment import PostComment
from apps.posts.serializers.post_comment import (
    PostCommentCreateSerializer,
    PostCommentListSerializer,
    PostCommentUpdateSerializer,
)

# 닉네임 자동완성 mock 데이터
MOCK_NICKNAMES = [
    {"id": 1, "nickname": "ozstudent"},
    {"id": 2, "nickname": "ozadmin"},
    {"id": 3, "nickname": "ozmaster"},
    {"id": 4, "nickname": "ozdev"},
    {"id": 5, "nickname": "ozuser"},
]


# 댓글 페이지네이션 클래스
class PostCommentPagination(PageNumberPagination):
    page_query_param = "page"
    page_size_query_param = "page_size"
    page_size = 10
    max_page_size = 100


# 닉네임 자동완성/추천 API (mock)
class PostNicknameAutocompleteAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Posts"],
        summary="닉네임 자동완성/추천 API (mock)",
        parameters=[OpenApiParameter(name="q", type=str, required=False, description="검색할 닉네임의 일부 문자열")],
        responses={200: OpenApiResponse(description="닉네임 추천 결과 목록 (mock)")},
    )
    def get(self, request: Request) -> Response:
        q_raw = request.query_params.get("q", "")
        q = str(q_raw).lower() if q_raw is not None else ""
        if q:
            results = [n for n in MOCK_NICKNAMES if q in str(n["nickname"]).lower()]
        else:
            results = MOCK_NICKNAMES[:3]
        return Response({"results": results}, status=status.HTTP_200_OK)


# 댓글 목록/생성 API
class PostCommentListCreateAPIView(generics.ListCreateAPIView):  # type: ignore[type-arg]
    """
    댓글 목록 조회(GET) 및 댓글 작성(POST) API
    - GET: 전체 이용자(비로그인 포함) 가능, 페이지네이션 적용
    - POST: 로그인 회원만 가능, 댓글 최대 500자
    """

    pagination_class = PostCommentPagination
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser]
    permission_classes = [AllowAny]  # 메서드에서 401 포맷 직접 맞춤

    def get_permissions(self) -> list[BasePermission]:
        return [AllowAny()]

    def _get_post(self) -> Post:
        post_id = self.kwargs.get("post_id")
        try:
            return Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            raise NotFound(detail=PostErrorMessage.POST_NOT_FOUND_WITH_TARGET)

    def get_queryset(self) -> QuerySet[PostComment]:
        post = self._get_post()
        return (
            PostComment.objects.filter(post=post)
            .select_related("author")
            .prefetch_related("tags__tagged_user")
            .order_by("created_at")
        )

    def get_serializer_class(self) -> Any:
        if self.request.method == "GET":
            return PostCommentListSerializer
        return PostCommentCreateSerializer

    def get_serializer_context(self) -> dict[str, Any]:
        ctx = super().get_serializer_context()
        if self.request.method == "POST":
            ctx["post"] = self._get_post()
        return ctx

    @extend_schema(
        operation_id="v1_post_comments_list",
        tags=["Comments"],
        summary="커뮤니티 게시글 댓글 목록 조회 API",
        responses={
            200: inline_serializer(
                name="PostCommentListPaginatedResponse",
                fields={
                    "count": serializers.IntegerField(),
                    "next": serializers.CharField(allow_null=True),
                    "previous": serializers.CharField(allow_null=True),
                    "results": PostCommentListSerializer(many=True),
                },
            ),
            404: inline_serializer(name="PostCommentList404", fields={"error_detail": serializers.CharField()}),
        },
    )
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        try:
            # _get_post()가 여기서 터지면 포맷을 error_detail로 맞춰줌
            self._get_post()
            return super().get(request, *args, **kwargs)
        except NotFound as e:
            return Response({"error_detail": str(e.detail)}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        tags=["Comments"],
        summary="커뮤니티 게시글 댓글 작성 API",
        request=PostCommentCreateSerializer,
        responses={
            201: inline_serializer(name="PostCommentCreate201", fields={"detail": serializers.CharField()}),
            400: inline_serializer(name="PostCommentCreate400", fields={"error_detail": serializers.DictField()}),
            401: inline_serializer(name="PostCommentCreate401", fields={"error_detail": serializers.CharField()}),
            404: inline_serializer(name="PostCommentCreate404", fields={"error_detail": serializers.CharField()}),
        },
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        # 401 포맷 강제
        if not request.user or not request.user.is_authenticated:
            return Response({"error_detail": PostErrorMessage.UNAUTHORIZED}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            post_obj = self._get_post()
        except NotFound as e:
            return Response({"error_detail": str(e.detail)}, status=status.HTTP_404_NOT_FOUND)

        serializer = PostCommentCreateSerializer(
            data=request.data,
            context={**self.get_serializer_context(), "request": request, "post": post_obj},
        )
        if not serializer.is_valid():
            return Response({"error_detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(author=request.user, post=post_obj)

        return Response({"detail": "댓글이 등록되었습니다."}, status=status.HTTP_201_CREATED)


# 댓글 상세/수정/삭제 API
class PostCommentRetrieveUpdateDestroyAPIView(APIView):
    """
    댓글 수정/삭제 API (테스트 포맷 맞춤)
    - PUT: 본인만 수정 가능
    - DELETE: 본인만 삭제 가능
    """

    serializer_class = PostCommentUpdateSerializer
    permission_classes = [AllowAny]  # 메서드에서 401 포맷 직접 맞춤
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser]

    def _require_auth(self, request: Request) -> Response | None:
        if not request.user or not request.user.is_authenticated:
            return Response({"error_detail": PostErrorMessage.UNAUTHORIZED}, status=status.HTTP_401_UNAUTHORIZED)
        return None

    def _get_post_or_404(self) -> Post:
        post_id = self.kwargs.get("post_id")
        try:
            return Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            raise NotFound(detail=PostErrorMessage.POST_NOT_FOUND_WITH_TARGET)

    def _get_comment_or_404(self) -> PostComment:
        # post_id 먼저 검증(경로 일관성)
        post = self._get_post_or_404()

        raw_comment_id = self.kwargs.get("comment_id")
        try:
            comment_id = int(raw_comment_id)
        except (TypeError, ValueError):
            raise NotFound(detail=PostErrorMessage.COMMENT_NOT_FOUND)

        if comment_id <= 0:
            raise NotFound(detail=PostErrorMessage.COMMENT_NOT_FOUND)

        try:
            return PostComment.objects.select_related("author").get(pk=comment_id, post=post)
        except PostComment.DoesNotExist:
            raise NotFound(detail=PostErrorMessage.COMMENT_NOT_FOUND)

    def _check_owner_or_403(self, request: Request, comment: PostComment) -> Response | None:
        # 작성자만 가능
        if not hasattr(request.user, "id") or comment.author_id != request.user.id:
            return Response({"error_detail": PostErrorMessage.FORBIDDEN}, status=status.HTTP_403_FORBIDDEN)
        return None

    @extend_schema(
        tags=["Comments"],
        summary="댓글 수정 API",
        responses={
            200: inline_serializer(
                name="PostCommentUpdateResponse",
                fields={
                    "id": serializers.IntegerField(),
                    "content": serializers.CharField(),
                    "updated_at": serializers.DateTimeField(),
                },
            ),
            400: inline_serializer(name="PostCommentUpdate400", fields={"error_detail": serializers.DictField()}),
            401: inline_serializer(name="PostCommentUpdate401", fields={"error_detail": serializers.CharField()}),
            403: inline_serializer(name="PostCommentUpdate403", fields={"error_detail": serializers.CharField()}),
            404: inline_serializer(name="PostCommentUpdate404", fields={"error_detail": serializers.CharField()}),
        },
    )
    def put(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        auth_resp = self._require_auth(request)
        if auth_resp is not None:
            return auth_resp

        try:
            comment = self._get_comment_or_404()
        except NotFound as e:
            return Response({"error_detail": str(e.detail)}, status=status.HTTP_404_NOT_FOUND)

        owner_resp = self._check_owner_or_403(request, comment)
        if owner_resp is not None:
            return owner_resp

        serializer = self.serializer_class(instance=comment, data=request.data, context={"request": request})
        if not serializer.is_valid():
            return Response({"error_detail": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        serializer.save(updated_at=timezone.now())

        return Response(
            {"id": comment.id, "content": serializer.validated_data["content"], "updated_at": timezone.now()},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        tags=["Comments"],
        summary="댓글 삭제 API",
        responses={
            200: inline_serializer(name="PostCommentDelete200", fields={"detail": serializers.CharField()}),
            401: inline_serializer(name="PostCommentDelete401", fields={"error_detail": serializers.CharField()}),
            403: inline_serializer(name="PostCommentDelete403", fields={"error_detail": serializers.CharField()}),
            404: inline_serializer(name="PostCommentDelete404", fields={"error_detail": serializers.CharField()}),
        },
    )
    def delete(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        auth_resp = self._require_auth(request)
        if auth_resp is not None:
            return auth_resp

        try:
            comment = self._get_comment_or_404()
        except NotFound as e:
            return Response({"error_detail": str(e.detail)}, status=status.HTTP_404_NOT_FOUND)

        owner_resp = self._check_owner_or_403(request, comment)
        if owner_resp is not None:
            return owner_resp

        comment.delete()
        return Response({"detail": "댓글이 삭제되었습니다."}, status=status.HTTP_200_OK)
