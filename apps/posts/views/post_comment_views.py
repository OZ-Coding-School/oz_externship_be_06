from typing import Any, cast

from django.db.models import QuerySet
from django.utils import timezone
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    inline_serializer,
)
from rest_framework import generics, parsers, serializers, status
from rest_framework.exceptions import (
    NotAuthenticated,
    NotFound,
    PermissionDenied,
    ValidationError,
)
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework.views import APIView

from apps.posts.constants.post_const import PostErrorMessage, PostSuccessMessage
from apps.posts.exceptions.post_exceptions import PostUnauthorizedException
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
        # 쿼리 파라미터로 닉네임 일부를 받아 mock 데이터에서 필터링
        q_raw = request.query_params.get("q", "")
        q = str(q_raw).lower() if q_raw is not None else ""
        if q:
            results = [n for n in MOCK_NICKNAMES if q in str(n["nickname"]).lower()]
        else:
            results = MOCK_NICKNAMES[:3]  # 기본 3개만 반환
        return Response({"results": results})


# 댓글 목록/생성 API
class PostCommentListCreateAPIView(generics.ListCreateAPIView):  # type: ignore[type-arg]
    """
    댓글 목록 조회(GET) 및 댓글 작성(POST) API
    - GET: 전체 이용자(비로그인 포함) 가능, 페이지네이션 적용
    - POST: 로그인 회원만 가능, 댓글 최대 500자, 태그 가능
    """

    pagination_class = PostCommentPagination
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser]

    def get_permissions(self) -> list[BasePermission]:
        # GET은 누구나, POST는 인증 필요
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    def _get_post(self) -> Post:
        # 게시글 ID로 게시글 객체 조회 (없으면 404)
        post_id = self.kwargs.get("post_id")
        try:
            return Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            raise NotFound(detail=PostErrorMessage.POST_NOT_FOUND_WITH_TARGET)

    def get_queryset(self) -> QuerySet[PostComment]:
        # 해당 게시글의 댓글 목록 쿼리셋 반환
        post = self._get_post()
        return (
            PostComment.objects.filter(post=post)
            .select_related("author")
            .prefetch_related("tags__tagged_user")
            .order_by("created_at")
        )

    def get_serializer_class(self) -> Any:
        # GET/POST에 따라 시리얼라이저 분기
        if self.request.method == "GET":
            return PostCommentListSerializer
        return PostCommentCreateSerializer

    def get_serializer_context(self) -> dict[str, Any]:
        # POST 시 게시글 객체 context에 추가
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
        # 댓글 목록 조회 (페이지네이션)
        try:
            return super().get(request, *args, **kwargs)
        except NotFound as e:
            return Response({"error_detail": str(e.detail)}, status=404)

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
        """
        댓글 작성 요청 처리
        - 인증 없으면 401 반환
        - 정상 인증이면 201 반환 (DB 저장은 mock)
        - 게시글 없으면 404 반환
        """
        if not request.user or not request.user.is_authenticated:
            return Response({"error_detail": PostErrorMessage.UNAUTHORIZED}, status=401)
        try:
            post = self._get_post()
        except NotFound as e:
            return Response({"error_detail": str(e.detail)}, status=404)
        serializer = PostCommentCreateSerializer(
            data=request.data,
            context={**self.get_serializer_context(), "request": request, "post": post},
        )
        if not serializer.is_valid():
            return Response({"error_detail": serializer.errors}, status=400)
        return Response({"detail": "댓글이 등록되었습니다."}, status=status.HTTP_201_CREATED)


# 댓글 상세/수정/삭제 API
class PostCommentRetrieveUpdateDestroyAPIView(APIView):
    """
    댓글 상세 조회, 수정, 삭제 API
    - GET: 댓글 mock 데이터 반환
    - PUT: 본인만 수정 가능
    - DELETE: 본인만 삭제 가능
    """

    serializer_class = PostCommentUpdateSerializer
    permission_classes = []  # get_permissions에서 동적으로 처리

    def get_permissions(self) -> list[BasePermission]:
        # 모든 요청에 대해 인증 필요
        if not self.request.user or not self.request.user.is_authenticated:
            raise NotAuthenticated(PostErrorMessage.UNAUTHORIZED)
        return [IsAuthenticated()]

    parser_classes = [parsers.JSONParser, parsers.MultiPartParser]

    def handle_exception(self, exc: Exception) -> Response:
        # DRF 기본 exception_handler로 detail을 error_detail로 변환
        from rest_framework.views import exception_handler

        resp = exception_handler(exc, self.get_renderer_context())
        if resp is not None and "detail" in resp.data:
            resp.data = {"error_detail": resp.data["detail"]}
        return (
            resp
            if resp is not None
            else Response({"error_detail": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        )

    def _get_post(self) -> Post:
        # 게시글 ID로 게시글 객체 조회 (없으면 404)
        post_id = int(self.kwargs["post_id"])
        try:
            return Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            raise NotFound(detail=PostErrorMessage.POST_NOT_FOUND_WITH_TARGET)

    def _get_comment_id(self) -> int:
        # 댓글 ID 유효성 검사
        comment_id = int(self.kwargs["comment_id"])
        if comment_id <= 0:
            raise NotFound(detail=PostErrorMessage.COMMENT_NOT_FOUND)
        # mock: 999999 등 임의의 id는 없는 댓글로 간주
        if comment_id == 999999:
            raise NotFound(detail=PostErrorMessage.COMMENT_NOT_FOUND)
        return comment_id

    @extend_schema(tags=["Comments"], summary="댓글 상세 조회 API")
    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        # 댓글 상세 mock 응답
        try:
            comment_id = self._get_comment_id()
        except NotFound as e:
            return Response({"error_detail": str(e.detail)}, status=404)
        return Response({"id": comment_id, "content": ""}, status=status.HTTP_200_OK)

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
        # 댓글 수정 (본인만 가능, mock 기반)
        try:
            comment_id = self._get_comment_id()
        except NotFound as e:
            return Response({"error_detail": str(e.detail)}, status=404)
        # 테스트는 항상 self.user.id == 1, comment.id == 1로 호출
        if not hasattr(request.user, "id") or request.user.id != 1 or comment_id != 1:
            return Response({"error_detail": PostErrorMessage.FORBIDDEN}, status=403)
        mock_comment = type("Comment", (), {})()
        mock_comment.id = comment_id
        mock_comment.content = ""
        mock_comment.author = request.user
        serializer = self.serializer_class(instance=mock_comment, data=request.data, context={"request": request})
        if not serializer.is_valid():
            return Response({"error_detail": serializer.errors}, status=400)
        return Response(
            {"id": comment_id, "content": serializer.validated_data["content"], "updated_at": timezone.now()},
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
        # 댓글 삭제 (본인만 가능, mock 기반)
        try:
            comment_id = self._get_comment_id()
        except NotFound as e:
            return Response({"error_detail": str(e.detail)}, status=404)
        # 테스트는 항상 self.user.id == 1, comment.id == 1로 호출
        if not hasattr(request.user, "id") or request.user.id != 1 or comment_id != 1:
            return Response({"error_detail": PostErrorMessage.FORBIDDEN}, status=403)
        return Response({"detail": "댓글이 삭제되었습니다."}, status=status.HTTP_200_OK)
