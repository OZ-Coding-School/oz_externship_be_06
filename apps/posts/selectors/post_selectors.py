from typing import Optional

from django.db.models import Count, Q, QuerySet

from apps.posts.models.post import Post


class PostSelector:
    """
    게시글 조회 및 데이터 추출을 담당하는 셀렉터 클래스입니다.
    """

    @staticmethod
    def get_post_list(
        category_id: Optional[int] = None,
        search: Optional[str] = None,
        search_filter: Optional[str] = "all",
        sort: Optional[str] = "latest",
    ) -> QuerySet[Post]:
        """
        검색, 필터, 정렬 및 N+1 최적화가 적용된 게시글 목록을 반환합니다.
        """
        queryset: QuerySet[Post] = Post.objects.select_related("author", "category").prefetch_related("images")

        # 에러 해결: 'postlike' -> 'likes', 'postcomment' -> 'comments'로 수정
        queryset = queryset.annotate(
            likes_count=Count("likes", distinct=True), comments_count=Count("comments", distinct=True)
        )

        # 1. 카테고리 필터링
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        # 2. 검색 필터링
        if search:
            if search_filter == "title":
                queryset = queryset.filter(title__icontains=search)
            elif search_filter == "content":
                queryset = queryset.filter(content__icontains=search)
            elif search_filter == "nickname":
                queryset = queryset.filter(author__nickname__icontains=search)
            else:
                queryset = queryset.filter(
                    Q(title__icontains=search) | Q(content__icontains=search) | Q(author__nickname__icontains=search)
                )

        # 3. 정렬 로직 (Mypy 에러 방지를 위해 sort or "latest" 적용)
        sort_map = {
            "latest": "-created_at",
            "likes": "-likes_count",
            "comments": "-comments_count",
            "oldest": "created_at",
        }

        order_by = sort_map.get(sort or "latest", "-created_at")

        return queryset.order_by(order_by)
