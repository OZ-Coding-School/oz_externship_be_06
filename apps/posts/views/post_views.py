from rest_framework import viewsets, filters
from django.db.models import Count, Q
from drf_spectacular.utils import extend_schema, OpenApiParameter
from ..models.post import Post
from ..serializers.post_serializers import PostListSerializer, PostDetailSerializer


@extend_schema(tags=["Community - Post"])
class PostViewSet(viewsets.ModelViewSet):
    # comment_count와 like_count를 DB에서 미리 계산해서 가져옴 (성능 최적화)
    queryset = Post.objects.annotate(
        comment_count=Count('comments', distinct=True),
        like_count=Count('likes', filter=Q(likes__is_liked=True), distinct=True)
    )
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