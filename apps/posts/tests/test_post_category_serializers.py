from django.test import TestCase

from apps.posts.models.post_category import PostCategory
from apps.posts.serializers.post_category import PostCategorySerializer


class PostCategorySerializerTests(TestCase):
    def test_post_category_serializer_fields(self) -> None:
        category = PostCategory.objects.create(name="전체 게시판", status=True)

        data = PostCategorySerializer(category).data

        self.assertEqual(set(data.keys()), {"id", "name"})
        self.assertEqual(data["id"], category.id)
        self.assertEqual(data["name"], "전체 게시판")
