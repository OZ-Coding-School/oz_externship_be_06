from __future__ import annotations

from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.exams.serializers import TakeExamRequestSerializer, TakeExamResponseSerializer
from apps.exams.services import build_take_exam_response, take_exam


class TakeExamAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        req_serializer = TakeExamRequestSerializer(data=request.data)
        req_serializer.is_valid(raise_exception=True)

        if not request.user.is_authenticated or not hasattr(request.user, "role"):
            from rest_framework.exceptions import AuthenticationFailed

            raise AuthenticationFailed("인증이 필요합니다.")

        result = take_exam(user=request.user, access_code=req_serializer.validated_data["access_code"])
        payload = build_take_exam_response(result=result)

        res_serializer = TakeExamResponseSerializer(data=payload)
        res_serializer.is_valid(raise_exception=True)
        return Response(res_serializer.data, status=200)
