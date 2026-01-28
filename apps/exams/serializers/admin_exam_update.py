from rest_framework import serializers

from apps.exams.models import Exam
from apps.courses.models import Subject

class AdminExamUpdateRequestSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=50)
    # 모든 Subject 중, 요청으로 들어온 ID인 Subject 객체를 매핑
    subject_id = serializers.PrimaryKeyRelatedField(source="subject", queryset=Subject.objects.all())
    thumbnail_img = serializers.ImageField(required=False)

    class Meta:
        model = Exam
        fields = ["title", "subject_id", "thumbnail_img"]

    # 409 제목 중복
    def validate_title(self, value):
        if Exam.objects.filter(title=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("동일한 이름의 쪽지시험이 이미 존재합니다.")
        return value

class AdminExamUpdateResponseSerializer(serializers.ModelSerializer):
    subject_id = serializers.IntegerField(source="subject.id")

    class Meta:
        model = Exam
        fields = ["id", "title", "subject_id", "thumbnail_img_url"]
