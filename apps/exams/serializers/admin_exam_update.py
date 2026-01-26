from rest_framework import serializers
from apps.exams.models import ExamDeployment

class AdminExamUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamDeployment
        fields = ['title', 'subject_id', 'thumbnail_img']
        extra_kwargs = {
            'title': {'required': True},
            'subject_id': {'required': True},
        }

    def validate_title(self, value):
        # 이름 중복 체크 예시
        if ExamDeployment.objects.filter(title=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("동일한 이름의 쪽지시험이 이미 존재합니다.")
        return value