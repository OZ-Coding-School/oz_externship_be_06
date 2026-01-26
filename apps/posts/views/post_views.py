from rest_framework import viewsets, filters, permissions
from django.db.models import Count, Q
from drf_spectacular.utils import extend_schema, OpenApiParameter, extend_schema_view

from .post_permissions import IsAuthorOrReadOnly
from ..models.post import Post
from ..serializers.post_serializers import PostListSerializer, PostDetailSerializer, PostCreateUpdateSerializer


@extend_schema_view(
    list=extend_schema(summary="게시글 목록 조회", description="모든 게시글을 조회하며, 필터링 및 정렬 기능을 지원합니다."),
    retrieve=extend_schema(summary="게시글 상세 조회", description="특정 ID의 게시글 상세 정보를 조회하며, 조회수가 1 증가합니다."),
    create=extend_schema(summary="게시글 작성", description="새로운 게시글을 작성합니다. 작성자는 현재 로그인한 사용자로 설정됩니다."),
    update=extend_schema(summary="게시글 전체 수정", description="게시글의 모든 필드를 수정합니다. 작성자만 가능합니다."),
    partial_update=extend_schema(summary="게시글 일부 수정", description="게시글의 특정 필드만 수정합니다. 작성자만 가능합니다."),
    destroy=extend_schema(summary="게시글 삭제", description="게시글을 삭제합니다. 작성자만 가능합니다."),
)
@extend_schema(tags=["posts"]) # 그룹명을 "posts"로 통일
class PostViewSet(viewsets.ModelViewSet):
    # comment_count와 like_count를 DB에서 미리 계산해서 가져옴 (성능 최적화)
    queryset = Post.objects.annotate(
        comment_count=Count('comments', distinct=True),
        like_count=Count('likes', filter=Q(likes__is_liked=True), distinct=True)
    )

    # 2. 기본 권한 설정 (기본적으로 누구나 읽을 수 있음)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    serializer_class = PostListSerializer

    # 필터링 및 정렬 기능 활성화
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]

    # ?search= 키워드로 검색할 필드 지정
    search_fields = ['title', 'content', 'author__nickname']

    # ?ordering= 키워드로 정렬할 필드 지정 (기본값: 최신순)
    ordering_fields = ['created_at', 'view_count', 'like_count', 'comment_count']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()

        # 1. 카테고리 필터링 (?category_id=1)
        category_id = self.request.query_params.get('category_id')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        # 2. 정렬 조건 커스텀 매핑 (?sort=most_views 등)
        sort_param = self.request.query_params.get('sort')
        if sort_param == 'latest':
            queryset = queryset.order_by('-created_at')
        elif sort_param == 'oldest':
            queryset = queryset.order_by('created_at')
        elif sort_param == 'most_views':
            queryset = queryset.order_by('-view_count')
        elif sort_param == 'most_likes':
            queryset = queryset.order_by('-like_count')
        elif sort_param == 'most_comments':
            queryset = queryset.order_by('-comment_count')

        # 3. 검색 필터 상세 구현 (?search_filter=title 등)
        search_keyword = self.request.query_params.get('search')
        search_filter = self.request.query_params.get('search_filter')

        if search_keyword and search_filter:
            if search_filter == 'title':
                queryset = queryset.filter(title__icontains=search_keyword)
            elif search_filter == 'content':
                queryset = queryset.filter(content__icontains=search_keyword)
            elif search_filter == 'author':
                queryset = queryset.filter(author__nickname__icontains=search_keyword)
            elif search_filter == 'title_or_content':
                queryset = queryset.filter(Q(title__icontains=search_keyword) | Q(content__icontains=search_keyword))

        return queryset

    def get_serializer_class(self):
        if self.action in ['retrieve', 'update', 'partial_update']:
            return PostDetailSerializer
        return PostListSerializer

    def get_permissions(self):
        """
        액션별로 세밀하게 권한을 제어합니다.
        """
        # 수정(update, partial_update) 및 삭제(destroy) 시에만 작성자 체크를 수행합니다.
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsAuthorOrReadOnly()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return PostCreateUpdateSerializer
        if self.action == 'retrieve':
            return PostDetailSerializer
        return PostListSerializer

    def perform_create(self, serializer):
        # 현재 로그인한 사용자를 작성자로 저장합니다.
        serializer.save(author=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        # 상세 조회 시 조회수를 증가시킵니다.
        instance = self.get_object()
        instance.view_count += 1
        instance.save()
        return super().retrieve(request, *args, **kwargs)