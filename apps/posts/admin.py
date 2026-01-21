from django.contrib import admin

from .models import Post, PostCategory, PostComment, PostLike

admin.site.register(Post)
admin.site.register(PostCategory)
admin.site.register(PostComment)
admin.site.register(PostLike)
