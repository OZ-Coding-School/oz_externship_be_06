from django.db.models import Count, Q
from apps.posts.models.post import Post

class PostSelector:
    @staticmethod
    def get_post_list(category_id: int = None):
        queryset = Post.objects.select_related('author', 'category')
        queryset = queryset.annotate(
            comment_count=Count('comments', distinct=True),
            like_count=Count('likes', filter=Q(likes__is_liked=True), distinct=True)
        )

        if category_id:
            queryset = queryset.filter(category_id=category_id)

        return queryset.order_by('-created_at')