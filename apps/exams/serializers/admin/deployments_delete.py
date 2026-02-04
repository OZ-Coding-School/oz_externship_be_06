from typing import Any
from rest_framework import serializers

class AdminExamDeploymentDeleteResponseSerializer(serializers.Serializer[Any]):
    deployment_id = serializers.IntegerField()
    is_deleted = serializers.BooleanField()
