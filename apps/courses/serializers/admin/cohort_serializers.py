from rest_framework import serializers

from apps.courses.models import Cohort


class CohortCreateRequestSerializer(serializers.Serializer):
    course_id = serializers.IntegerField(required=True)
    number = serializers.IntegerField(required=True)
    max_student = serializers.IntegerField(required=True)
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    status = serializers.ChoiceField(choices=Cohort.StatusChoices.choices, required=False)

    def validate(self, attrs: dict) -> dict:
        if attrs["end_date"] <= attrs["start_date"]:
            raise serializers.ValidationError({"end_date": ["종료일은 시작일 이후여야 합니다."]})
        return attrs


class CohortUpdateRequestSerializer(serializers.Serializer):
    number = serializers.IntegerField(required=False)
    max_student = serializers.IntegerField(required=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    status = serializers.ChoiceField(choices=Cohort.StatusChoices.choices, required=False)

    def validate(self, attrs: dict) -> dict:
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")

        if self.instance:
            start_date = start_date or self.instance.start_date
            end_date = end_date or self.instance.end_date

        if start_date and end_date and end_date <= start_date:
            raise serializers.ValidationError({"end_date": ["종료일은 시작일 이후여야 합니다."]})

        return attrs


class CohortUpdateResponseSerializer(serializers.ModelSerializer[Cohort]):
    course_id = serializers.IntegerField(source="course.id", read_only=True)

    class Meta:
        model = Cohort
        fields = ["id", "course_id", "number", "max_student", "start_date", "end_date", "status", "updated_at"]


class CohortAvgScoreSerializer(serializers.Serializer):
    name = serializers.CharField()
    score = serializers.IntegerField()


class CohortStudentSerializer(serializers.Serializer):
    value = serializers.CharField()
    label = serializers.CharField()
