from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from apps.posts.models.post import Post
from apps.posts.models.post_comment import PostComment

User = get_user_model()

class PostCommentAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.post = Post.objects.create(author=self.user, title="test post", content="test content")
        self.client.force_authenticate(user=self.user)

    def test_comment_create_success(self):
        # 정상적으로 댓글이 등록되는 경우
        url = reverse("postcomment-list", args=[self.post.id])
        data = {"content": "@testuser2 를 태그한 댓글 작성 테스트"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("detail", response.data)
        self.assertEqual(response.data["detail"], "댓글이 등록되었습니다.")
        self.assertTrue(PostComment.objects.filter(post=self.post, author=self.user, content=data["content"]).exists())

    def test_comment_create_required_field(self):
        # content 미입력 시 400 반환 및 에러 메시지 확인
        url = reverse("postcomment-list", args=[self.post.id])
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 400)
        self.assertIn("error_detail", response.data)
        self.assertIn("content", response.data["error_detail"])
        self.assertIn("이 필드는 필수 항목입니다.", response.data["error_detail"]["content"])

    def test_comment_create_unauthorized(self):
        # 인증 없이 요청 시 401 반환 및 에러 메시지 확인
        self.client.force_authenticate(user=None)
        url = reverse("postcomment-list", args=[self.post.id])
        data = {"content": "test"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 401)
        self.assertIn("error_detail", response.data)
        self.assertEqual(response.data["error_detail"], "자격 인증 데이터가 제공되지 않았습니다.")

    def test_comment_create_post_not_found(self):
        # 존재하지 않는 게시글에 댓글 작성 시 404 반환 및 에러 메시지 확인
        url = reverse("postcomment-list", args=[999999])
        data = {"content": "test"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 404)
        self.assertIn("error_detail", response.data)
        self.assertEqual(response.data["error_detail"], "해당 게시글을 찾을 수 없습니다.")

    def test_comment_list_pagination_and_structure(self):
        PostComment.objects.create(post=self.post, author=self.user, content="comment1")
        PostComment.objects.create(post=self.post, author=self.user, content="comment2")
        url = reverse("postcomment-list", args=[self.post.id])
        response = self.client.get(url, {"page": 1, "page_size": 10})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # pagination(페이지네이션) 구조 확인
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("previous", response.data)
        self.assertIn("results", response.data)
        self.assertEqual(response.data["count"], 2)
        self.assertIsInstance(response.data["results"], list)
        self.assertEqual(len(response.data["results"]), 2)
        comment = response.data["results"][0]
        # author(작성자) 구조 확인
        self.assertIn("author", comment)
        self.assertIn("id", comment["author"])
        self.assertIn("nickname", comment["author"])
        self.assertIn("profile_img_url", comment["author"])
        # tagged_users(태그된 유저) 구조 확인
        self.assertIn("tagged_users", comment)
        self.assertIsInstance(comment["tagged_users"], list)
        # content, created_at, updated_at 필드 확인
        self.assertIn("content", comment)
        self.assertIn("created_at", comment)
        self.assertIn("updated_at", comment)

    def test_comment_list_404(self):
        url = reverse("postcomment-list", args=[999999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("error_detail", response.data)
        self.assertEqual(response.data["error_detail"], "해당 게시글을 찾을 수 없습니다.")

    def test_comment_update_success(self):
        # 본인 댓글을 정상적으로 수정하는 경우 (PUT)
        comment = PostComment.objects.create(post=self.post, author=self.user, content="old content")
        url = reverse("postcomment-detail", args=[self.post.id, comment.id])
        data = {"content": "@testuser3 을 태그한 댓글 작성 테스트"}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("id", response.data)
        self.assertIn("content", response.data)
        self.assertIn("updated_at", response.data)
        self.assertEqual(response.data["content"], data["content"])

    def test_comment_update_required_field(self):
        # content 미입력 시 400 반환 및 에러 메시지 확인
        comment = PostComment.objects.create(post=self.post, author=self.user, content="old content")
        url = reverse("postcomment-detail", args=[self.post.id, comment.id])
        response = self.client.put(url, {})
        self.assertEqual(response.status_code, 400)
        self.assertIn("error_detail", response.data)
        self.assertIn("content", response.data["error_detail"])
        self.assertIn("이 필드는 필수 항목입니다.", response.data["error_detail"]["content"])

    def test_comment_update_unauthorized(self):
        # 인증 없이 요청 시 401 반환 및 에러 메시지 확인
        comment = PostComment.objects.create(post=self.post, author=self.user, content="old content")
        self.client.force_authenticate(user=None)
        url = reverse("postcomment-detail", args=[self.post.id, comment.id])
        data = {"content": "test"}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, 401)
        self.assertIn("error_detail", response.data)
        self.assertEqual(response.data["error_detail"], "자격 인증 데이터가 제공되지 않았습니다.")

    def test_comment_update_forbidden(self):
        # 본인 외 사용자가 수정 시 403 반환 및 에러 메시지 확인
        other = User.objects.create_user(username="other", password="pass")
        comment = PostComment.objects.create(post=self.post, author=other, content="old content")
        url = reverse("postcomment-detail", args=[self.post.id, comment.id])
        data = {"content": "test"}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, 403)
        self.assertIn("error_detail", response.data)
        self.assertEqual(response.data["error_detail"], "권한이 없습니다.")

    def test_comment_update_not_found(self):
        # 존재하지 않는 댓글 수정 시 404 반환 및 에러 메시지 확인
        url = reverse("postcomment-detail", args=[self.post.id, 999999])
        data = {"content": "test"}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, 404)
        self.assertIn("error_detail", response.data)
        self.assertEqual(response.data["error_detail"], "해당 댓글을 찾을 수 없습니다.")

    def test_comment_delete_success(self):
        # 본인 댓글을 정상적으로 삭제하는 경우
        comment = PostComment.objects.create(post=self.post, author=self.user, content="to delete")
        url = reverse("postcomment-detail", args=[self.post.id, comment.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn("detail", response.data)
        self.assertEqual(response.data["detail"], "댓글이 삭제되었습니다.")
        self.assertFalse(PostComment.objects.filter(id=comment.id).exists())

    def test_comment_delete_unauthorized(self):
        # 인증 없이 삭제 시 401 반환 및 에러 메시지 확인
        comment = PostComment.objects.create(post=self.post, author=self.user, content="to delete")
        self.client.force_authenticate(user=None)
        url = reverse("postcomment-detail", args=[self.post.id, comment.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 401)
        self.assertIn("error_detail", response.data)
        self.assertEqual(response.data["error_detail"], "자격 인증 데이터가 제공되지 않았습니다.")

    def test_comment_delete_forbidden(self):
        # 본인 외 사용자가 삭제 시 403 반환 및 에러 메시지 확인
        other = User.objects.create_user(username="other", password="pass")
        comment = PostComment.objects.create(post=self.post, author=other, content="to delete")
        url = reverse("postcomment-detail", args=[self.post.id, comment.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)
        self.assertIn("error_detail", response.data)
        self.assertEqual(response.data["error_detail"], "권한이 없습니다.")

    def test_comment_delete_not_found(self):
        # 존재하지 않는 댓글 삭제 시 404 반환 및 에러 메시지 확인
        url = reverse("postcomment-detail", args=[self.post.id, 999999])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)
        self.assertIn("error_detail", response.data)
        self.assertEqual(response.data["error_detail"], "해당 댓글을 찾을 수 없습니다.")
