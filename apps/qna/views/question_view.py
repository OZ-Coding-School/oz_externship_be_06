from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.qna.serializers.question_serializer import (
    QuestionCreateResponseSerializer,
    QuestionCreateSerializer,
)
from apps.qna.services.question_service import QuestionService
from apps.qna.utils.permissions import IsStudent


# 질문 등록
class QuestionCreateAPIView(APIView):
    permission_classes = [IsStudent]  # 학생만 question 등록 가능

    @extend_schema(
        summary="질문 등록 API",
        description=(
            "수강생 권한을 가진 로그인 유저가 질문을 등록합니다.\n\n"
            "질문 등록 시 입력 항목\n"
            "- 제목: 질문의 핵심 요약\n"
            "- 질문내용: 마크다운 문법 사용 가능, 이미지 첨부 가능\n"
            "- 카테고리: 대분류 > 중분류 > 소분류\n"
            "- 내용에 포함된 이미지들의 PK 리스트"
        ),
        request=QuestionCreateSerializer,
        responses={
            201: OpenApiResponse(response=QuestionCreateResponseSerializer, description="질문 등록 성공"),
            400: OpenApiResponse(description="잘못된 요청 데이터 (Bad Request)"),
            401: OpenApiResponse(description="인증 실패 (Unauthorized)"),
            403: OpenApiResponse(description="접근 권한 없음 (Forbidden)"),
        },
        tags=["QnA"],
    )
    def post(self, request: Request) -> Response:
        serializer = QuestionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 서비스 호출
        question = QuestionService.create_question(author=request.user, data=serializer.validated_data)

        # 응답 출력
        response_serializer = QuestionCreateResponseSerializer(question)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
