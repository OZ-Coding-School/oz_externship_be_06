from rest_framework import serializers

from apps.courses.models import Subject
from apps.exams.constants import ErrorMessages
from apps.exams.models import Exam


class AdminExamUpdateRequestSerializer(serializers.ModelSerializer[Exam]):
    title = serializers.CharField(max_length=50, required=False)
    # 모든 Subject 중, 요청으로 들어온 ID인 Subject 객체를 매핑
    subject_id = serializers.PrimaryKeyRelatedField(source="subject", queryset=Subject.objects.all(), required=False)
    thumbnail_img = serializers.ImageField(required=False)

    class Meta:
        model = Exam
        fields = ["title", "subject_id", "thumbnail_img"]

    # 409 제목 중복
    def validate_title(self, value: str) -> str:
        if isinstance(self.instance, Exam):
            if Exam.objects.filter(title=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError(ErrorMessages.EXAM_UPDATE_CONFLICT.value)
        return value

    # payload가 아예 비었을 때
    def validate(self, data: dict[str, object]) -> dict[str, object]:
        if not data:
            raise serializers.ValidationError(ErrorMessages.INVALID_EXAM_UPDATE_REQUEST.value)
        return data


class AdminExamUpdateResponseSerializer(serializers.ModelSerializer[Exam]):
    subject_id = serializers.IntegerField(source="subject.id")

    class Meta:
        model = Exam
        fields = ["id", "title", "subject_id", "thumbnail_img_url"]
