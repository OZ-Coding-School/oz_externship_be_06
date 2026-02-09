from typing import Optional

from django.db.models import BooleanField, Count, Exists, OuterRef, Q, QuerySet, Value

from apps.posts.exceptions.post_exceptions import PostNotFoundException
from apps.posts.models.post import Post
from apps.posts.models.post_likes import PostLike


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
        user_id: Optional[int] = None,
    ) -> QuerySet[Post]:
        """
        검색, 필터, 정렬 및 N+1 최적화가 적용된 게시글 목록을 반환합니다.
        """
        queryset: QuerySet[Post] = Post.objects.select_related("author", "category").prefetch_related("images")
        queryset = queryset.annotate(
            like_count=Count("likes", filter=Q(likes__is_liked=True), distinct=True),
            comment_count=Count("comments", distinct=True),
        )

        # 현재 유저의 좋아요 여부
        if user_id:
            queryset = queryset.annotate(
                is_like=Exists(PostLike.objects.filter(post=OuterRef("pk"), user_id=user_id, is_liked=True))
            )
        else:
            queryset = queryset.annotate(is_like=Value(False, output_field=BooleanField()))

        if category_id:
            queryset = queryset.filter(category_id=category_id)
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
        sort_map = {
            "latest": "-created_at",
            "likes": "-like_count",
            "comments": "-comment_count",
            "oldest": "created_at",
        }

        order_by = sort_map.get(sort or "latest", "-created_at")

        return queryset.order_by(order_by)

    @staticmethod
    def get_post_detail(post_id: int, user_id: Optional[int] = None) -> Post:
        """
        게시글 상세 정보 조회
        카테고리는 JOIN, 좋아요 개수만 집계
        """

        queryset = Post.objects.select_related("author", "category").annotate(
            likes_count=Count("likes", filter=Q(likes__is_liked=True), distinct=True)
        )

        # 현재 유저의 좋아요 여부
        if user_id:
            queryset = queryset.annotate(
                is_like=Exists(PostLike.objects.filter(post=OuterRef("pk"), user_id=user_id, is_liked=True))
            )
        else:
            queryset = queryset.annotate(is_like=Value(False, output_field=BooleanField()))

        try:
            return queryset.get(id=post_id)
        except Post.DoesNotExist:
            raise PostNotFoundException()

    @staticmethod
    def get_post_by_id(post_id: int) -> Post | None:
        """
        ID를 통해 특정 게시글을 조회
        """
        try:
            return Post.objects.select_related("author", "category").get(id=post_id)
        except Post.DoesNotExist:
            return None
