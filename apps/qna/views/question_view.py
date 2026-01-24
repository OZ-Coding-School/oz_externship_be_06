from typing import Any

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.qna.serializers.question_serializer import (
    QuestionCreateResponseSerializer,
    QuestionCreateSerializer,
    QuestionListSerializer,
    QuestionQuerySerializer,
)
from apps.qna.services.question_service import QuestionService
from apps.qna.utils.permissions import IsStudent
from apps.qna.utils.question_list_pagination import QnAPaginator


# 질문 등록 & 조회
class QuestionCreateListAPIView(APIView):
    """
    질의응답 질문 등록 및 목록 조회 API
    """

    def get_permissions(self) -> list[Any]:
        if self.request.method == "POST":
            return [IsStudent()]
        return [AllowAny()]

    @extend_schema(
        summary="질문 목록 조회 API",
        description="""
        등록된 모든 질문 목록을 최신순으로 조회합니다.
        질의응답 목록에서 조회가능한 항목
        - 질의응답 카테고리 (대분류 > 중분류 > 소분류 형태)
        - 작성자 정보
            프로필 이미지
            닉네임
        - 질의응답 제목
        - 질문 내용
        - 답변 수
        - 조회수
        - 질문 작성일시
        - 질문 내용에 포함된 이미지의 썸네일 이미지
        """,
        parameters=[QuestionQuerySerializer],
        responses={
            200: QuestionListSerializer(many=True),
            400: OpenApiResponse(description="Bad Request"),
            404: OpenApiResponse(description="Not Found"),
        },
        tags=["QnA"],
    )
    def get(self, request: Request) -> Response:
        """필터링 및 검색된 질문 목록 반환"""
        # 쿼리 파라미터 검증
        query_serializer = QuestionQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        # 데이터 조회
        queryset = QuestionService.get_question_list(query_serializer.validated_data)

        # Response 생성
        return QnAPaginator.get_paginated_data_response(
            queryset=queryset, request=request, serializer_class=QuestionListSerializer, view=self
        )

    @extend_schema(
        summary="질문 등록 API",
        description="""
        수강생 권한을 가진 로그인 유저가 질문을 등록합니다.
        질문 등록 시 입력 항목
        - 제목: 질문의 핵심 요약
        - 질문내용: 마크다운 문법 사용 가능, 이미지 첨부 가능
        - 카테고리: 대분류 > 중분류 > 소분류
        - 내용에 포함된 이미지들의 PK 리스트
        """,
        request=QuestionCreateSerializer,
        responses={
            201: OpenApiResponse(response=QuestionCreateResponseSerializer, description="질문 등록 성공"),
            400: OpenApiResponse(description="Bad Request"),
            401: OpenApiResponse(description="Unauthorized"),
            403: OpenApiResponse(description="Forbidden"),
        },
        tags=["QnA"],
    )
    def post(self, request: Request) -> Response:
        """질문 생성"""
        serializer = QuestionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 서비스 호출
        question = QuestionService.create_question(author=request.user, data=serializer.validated_data)

        # 응답 출력
        response_serializer = QuestionCreateResponseSerializer(question)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
