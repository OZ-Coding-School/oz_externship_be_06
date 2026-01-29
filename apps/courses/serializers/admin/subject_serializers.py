from rest_framework import serializers

from apps.courses.models import Subject


class SubjectListSerializer(serializers.ModelSerializer[Subject]):
    course_id = serializers.IntegerField(source="course.id", read_only=True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = ["id", "course_id", "title", "status", "thumbnail_img_url"]

    def get_status(self, obj: Subject) -> str:
        return "activated" if obj.status else "deactivated"


class SubjectScatterSerializer(serializers.Serializer):
    time = serializers.FloatField()
    score = serializers.IntegerField()
