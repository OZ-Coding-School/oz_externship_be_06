from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.posts.models.post import Post
from apps.posts.models.post_category import PostCategory
from apps.posts.models.post_comment import PostComment
from apps.posts.models.post_comment_tags import PostCommentTag

User = get_user_model()


class CommentTaggingTests(APITestCase):
    """댓글 유저 태깅 기능 테스트"""

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            email="test@example.com",
            password="password",
            nickname="testuser",
            phone_number="010-1111-2222",
            gender="MALE",
            birthday="1990-01-01",
        )
        self.other_user = User.objects.create_user(
            email="other@example.com",
            password="password",
            nickname="taggeduser",
            phone_number="010-3333-4444",
            gender="FEMALE",
            birthday="1992-02-02",
        )
        self.category = PostCategory.objects.create(name="test category")
        self.post = Post.objects.create(
            author=self.user,
            title="test post",
            content="test content",
            category=self.category,
        )
        self.client.force_authenticate(user=self.user)
        self.list_url = reverse("posts:post-comment-list-create", args=[self.post.id])

    def test_create_comment_with_tag(self) -> None:
        """댓글 작성 시 유저 태그가 정상적으로 저장되는지 테스트"""
        content = "@taggeduser 안녕하세요!"
        data = {"content": content}
        response = self.client.post(self.list_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 댓글 및 태그 생성 확인
        comment = PostComment.objects.get(post=self.post, content=content)
        tags = PostCommentTag.objects.filter(comment=comment)
        self.assertEqual(tags.count(), 1)
        tag = tags.first()
        self.assertIsNotNone(tag)
        if tag:
            self.assertEqual(tag.tagged_user, self.other_user)

    def test_update_comment_tag(self) -> None:
        """댓글 수정 시 유저 태그가 갱신되는지 테스트"""
        comment = PostComment.objects.create(post=self.post, author=self.user, content="기존 내용")
        detail_url = reverse("posts:post-comment-detail", args=[self.post.id, comment.id])

        # 새로운 태그로 수정
        new_content = "@taggeduser 수정된 내용"
        response = self.client.put(detail_url, {"content": new_content})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        comment.refresh_from_db()
        self.assertEqual(comment.content, new_content)

        tags = PostCommentTag.objects.filter(comment=comment)
        self.assertEqual(tags.count(), 1)
        tag = tags.first()
        self.assertIsNotNone(tag)
        if tag:
            self.assertEqual(tag.tagged_user, self.other_user)

    def test_invalid_user_tag_ignored(self) -> None:
        """존재하지 않는 유저 태그 시 무시되는지 테스트"""
        content = "@noneuser 존재하지 않는 유저"
        data = {"content": content}
        response = self.client.post(self.list_url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        comment = PostComment.objects.get(post=self.post, content=content)
        self.assertFalse(PostCommentTag.objects.filter(comment=comment).exists())
