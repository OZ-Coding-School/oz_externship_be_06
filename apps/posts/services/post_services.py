from apps.posts.models import Post
from apps.users.models import User


class PostService:
    @staticmethod
    def create_post(user: User, title: str, content: str, category_id: int) -> Post:
        """
        새로운 게시글을 생성합니다.
        """

        post = Post.objects.create(
            author = user,
            title = title,
            content = content,
            category_id = category_id,
        )
        return post