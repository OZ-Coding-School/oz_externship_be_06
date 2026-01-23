from rest_framework import serializers

class PostSerializer(serializers.Serializer):
    id = serializers.IntegerField()              # 게시글 ID
    title = serializers.CharField()              # 제목
    content = serializers.CharField()            # 본문 내용