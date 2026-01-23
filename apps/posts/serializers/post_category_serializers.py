from rest_framework import serializers

class PostCategorySerializer(serializers.Serializer):
    id = serializers.IntegerField()      # 카테고리 ID
    name = serializers.CharField()       # 카테고리 이름