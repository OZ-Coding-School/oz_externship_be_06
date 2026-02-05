from typing import cast

from django.test import TestCase

from apps.posts.models.post import Post
from apps.posts.models.post_category import PostCategory
from apps.posts.models.post_comment import PostComment
from apps.posts.selectors.comment_selectors import CommentSelector


class CommentSelectorTests(TestCase):
    def setUp(self) -> None:
        """테스트용 카테고리, 게시글, 댓글 생성"""
        self.category = PostCategory.objects.create(name="cat")
        self.post = Post.objects.create(author_id=1, title="t", content="c", category=self.category)
        self.comment = PostComment.objects.create(post=self.post, author_id=1, content="cc")

    def test_get_comment_by_id_not_found(self) -> None:
        """없는 댓글 PK로 조회 시 예외 발생"""
        from apps.posts.models.post_comment import PostComment

        with self.assertRaises(PostComment.DoesNotExist):
            CommentSelector.get_comment_by_id(99999999)

    def test_get_comments_for_post_not_found(self) -> None:
        """없는 게시글 PK로 댓글 목록 조회 시 예외 발생"""
        from apps.posts.models.post import Post

        with self.assertRaises(Post.DoesNotExist):
            CommentSelector.get_comments_for_post(99999999)

    def test_get_comment_by_id_success(self) -> None:
        """존재하는 댓글 PK로 정상 조회"""
        comment = CommentSelector.get_comment_by_id(self.comment.pk)
        self.assertEqual(comment.pk, self.comment.pk)
        self.assertEqual(comment.content, self.comment.content)

    def test_get_comments_for_post_success(self) -> None:
        """존재하는 게시글 PK로 댓글 목록 정상 조회"""
        comments = CommentSelector.get_comments_for_post(self.post.pk)
        self.assertEqual(comments.count(), 1)
        from typing import cast

        first_comment = comments.first()
        self.assertIsNotNone(first_comment)
        first_comment = cast(PostComment, first_comment)
        self.assertEqual(first_comment.pk, self.comment.pk)
