from typing import Any

from rest_framework import serializers


class AdminExamSubmissionDetailExamSerializer(serializers.Serializer[Any]):
    exam_title = serializers.CharField()
    subject_name = serializers.CharField()
    duration_time = serializers.IntegerField()
    open_at = serializers.DateTimeField()
    close_at = serializers.DateTimeField()


class AdminExamSubmissionDetailStudentSerializer(serializers.Serializer[Any]):
    nickname = serializers.CharField()
    name = serializers.CharField()
    course_name = serializers.CharField()
    cohort_number = serializers.IntegerField()


class AdminExamSubmissionDetailResultSerializer(serializers.Serializer[Any]):
    score = serializers.IntegerField()
    correct_answer_count = serializers.IntegerField()
    total_question_count = serializers.IntegerField()
    cheating_count = serializers.IntegerField()
    elapsed_time = serializers.IntegerField()


class AdminExamSubmissionDetailQuestionSerializer(serializers.Serializer[Any]):
    id = serializers.IntegerField()
    number = serializers.IntegerField()
    type = serializers.CharField()
    question = serializers.CharField()
    prompt = serializers.CharField(allow_null=True, required=False)
    options = serializers.ListField(child=serializers.CharField(), allow_null=True, required=False)
    point = serializers.IntegerField()
    answer = serializers.JSONField(allow_null=True)
    submitted_answer = serializers.JSONField(allow_null=True)
    is_correct = serializers.BooleanField()
    explanation = serializers.CharField(allow_blank=True, required=False)


class AdminExamSubmissionDetailResponseSerializer(serializers.Serializer[Any]):
    exam = AdminExamSubmissionDetailExamSerializer()
    student = AdminExamSubmissionDetailStudentSerializer()
    result = AdminExamSubmissionDetailResultSerializer()
    questions = AdminExamSubmissionDetailQuestionSerializer(many=True)
