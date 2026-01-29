from rest_framework import serializers

from apps.courses.models import Cohort


class CohortListSerializer(serializers.ModelSerializer[Cohort]):
    course_id = serializers.IntegerField(source="course.id", read_only=True)

    class Meta:
        model = Cohort
        fields = ["id", "course_id", "number", "status"]
