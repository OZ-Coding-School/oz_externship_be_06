from datetime import datetime
from typing import Any

from django.conf import settings
from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.qna.exceptions.question_exception import qna_exception_handler
from apps.qna.models import (
    Answer,
    AnswerComment,
    Question,
    QuestionCategory,
    QuestionImage,
)
from apps.qna.serializers.question import request as ser_q_req
from apps.qna.serializers.question import response as ser_q_res
from apps.qna.services.question import command as svc_q_cmd
from apps.qna.services.question import query as svc_q_qry
from apps.qna.utils.permissions import IsStudent
from apps.qna.utils.question_list_pagination import QnAPaginator


class QnaBaseAPIView(APIView):
    """
    QnA 앱의 모든 View가 상속받을 베이스 뷰.
    이 뷰를 상속받으면 settings.py를 건드리지 않고도 QnA 전용 에러 규격이 적용됩니다.
    """

    def handle_exception(self, exc: Exception) -> Response:
        response = qna_exception_handler(exc, self.get_renderer_context())
        if response is None:
            raise exc
        response.exception = True
        return response


class QuestionCreateListAPIView(QnaBaseAPIView):
    """
    질문 등록 및 목록 조회 API View
    """

    def get_permissions(self) -> list[Any]:
        if self.request.method == "POST":
            return [IsAuthenticated(), IsStudent()]
        return [AllowAny()]

    # 질의응답 목록 조회
    # [GET] /api/v1/qna/questions
    @extend_schema(
        summary="질문 목록 조회 API",
        description="""
        ### 등록된 모든 질문 목록을 최신순으로 조회합니다.
        **질의응답 목록에서 조회가능한 항목**
        - 질의응답 카테고리 (대분류 > 중분류 > 소분류 형태)
        - 작성자 정보
            - 프로필 이미지
            - 닉네임
        - 질의응답 제목
        - 질문 내용
        - 답변 수
        - 조회수
        - 질문 작성일시
        - 질문 내용에 포함된 이미지의 썸네일 이미지
        """,
        parameters=[ser_q_res.QuestionQuerySerializer],
        responses={
            200: ser_q_res.QuestionListSerializer(many=True),
            400: OpenApiResponse(
                description="Bad Request",
                response=dict,
                examples=[
                    OpenApiExample(
                        name="잘못된 요청 예시",
                        value={"error_detail": "유효하지 않은 목록 조회 요청입니다."},
                        description="잘못된 요청 예시",
                    ),
                ],
            ),
            404: OpenApiResponse(
                description="Not Found",
                response=dict,
                examples=[
                    OpenApiExample(
                        name="데이터 없음 예시",
                        value={"error_detail": "조회 가능한 질문이 존재하지 않습니다."},
                        description="데이터 없음 예시",
                    ),
                ],
            ),
        },
        tags=["qna"],
    )
    def get(self, request: Request) -> Response:
        """필터링 및 검색된 질문 목록 반환"""
        # 쿼리 파라미터 검증
        query_serializer = ser_q_res.QuestionQuerySerializer(data=request.query_params)
        query_serializer.is_valid(raise_exception=True)

        # Mock Data 생성
        if settings.USE_EXAM_MOCK:
            User = get_user_model()
            mock_user = User(
                id=1,
                nickname="MockUser",
                profile_img_url="https://ssl.pstatic.net/static/pwe/address/img_profile.png",
            )

            cat_root = QuestionCategory(id=1, name="개발")
            cat_mid = QuestionCategory(id=2, name="백엔드", parent=cat_root)
            cat_leaf = QuestionCategory(id=3, name="Django", parent=cat_mid)

            queryset: Any = []
            for i in range(1, 11):
                q = Question(
                    id=i,
                    author=mock_user,
                    category=cat_leaf,
                    title=f"Mock 질문 제목 {i}",
                    content=f"Mock 질문 내용입니다. {i} ![image](https://via.placeholder.com/150)",
                    view_count=i * 10,
                    created_at=datetime.now(),
                )
                # Annotate field manual injection
                setattr(q, "answer_count", i % 3)
                queryset.append(q)
        else:
            queryset = svc_q_qry.QuestionQueryService.get_question_list(query_serializer.validated_data)

        # Response 생성
        return QnAPaginator.get_paginated_data_response(
            queryset=queryset, request=request, serializer_class=ser_q_res.QuestionListSerializer, view=self
        )

    # 질문 등록
    # [POST] /api/v1/qna/questions
    @extend_schema(
        summary="질문 등록 API",
        description="""
        ### 수강생 권한을 가진 로그인 유저가 질문을 등록합니다.
        **질문 등록 시 입력 항목**
        - 제목: 질문의 핵심 요약
        - 질문내용: 마크다운 문법 사용 가능, 이미지 첨부 가능
        - 카테고리: 대분류 > 중분류 > 소분류
        - 내용에 포함된 이미지들의 PK 리스트
        """,
        request=ser_q_req.QuestionCreateSerializer,
        responses={
            201: OpenApiResponse(response=ser_q_res.QuestionCreateResponseSerializer, description="질문 등록 성공"),
            400: OpenApiResponse(
                description="Bad Request",
                response=dict,
                examples=[
                    OpenApiExample(
                        name="잘못된 요청 예시",
                        value={"error_detail": "유효하지 않은 질문 등록 요청입니다."},
                        description="잘못된 요청 예시",
                    ),
                ],
            ),
            401: OpenApiResponse(
                description="Unauthorized",
                response=dict,
                examples=[
                    OpenApiExample(
                        name="인증 실패 예시",
                        value={"error_detail": "로그인한 수강생만 질문을 등록할 수 있습니다."},
                        description="인증 실패 예시",
                    ),
                ],
            ),
            403: OpenApiResponse(
                description="Forbidden",
                response=dict,
                examples=[
                    OpenApiExample(
                        name="권한 없음 예시",
                        value={"error_detail": "질문 등록 권한이 없습니다."},
                        description="권한 없음 예시",
                    ),
                ],
            ),
        },
        tags=["qna"],
    )
    def post(self, request: Request) -> Response:
        """질문 생성"""
        serializer = ser_q_req.QuestionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 서비스 호출
        question = svc_q_cmd.QuestionCommandService.create_question(author=request.user, data=serializer.validated_data)

        # 응답 출력
        response_serializer = ser_q_res.QuestionCreateResponseSerializer(question)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class QuestionDetailAPIView(QnaBaseAPIView):
    """
    질문 상세 조회 API View
    """

    permission_classes = [AllowAny]

    # 질의응답 상세 조회
    # GET /api/v1/qna/questions/{question_id}
    @extend_schema(
        summary="질문 상세 조회 API",
        description="""
    ### 특정 항목을 클릭 시 상세조회 페이지로 이동합니다.
    **상세 조회 페이지에서 확인 가능한 항목**
    - 질문 제목
    - 질문 내용
    - 질문 내용에 첨부된 이미지
    - 질문 작성자 정보
        - 프로필 썸네일 이미지
        - 닉네임
    - 질문 카테고리 정보
        - 대, 중, 소분류 카테고리 이름
    - 질문 조회수
    - 질문 작성일시
    - 답변 목록
        - 답변 작성자 정보
            - 프로필 썸네일 이미지
            - 닉네임
        - 답변 내용
        - 답변 작성일시
        - 답변 채택 여부
        - 답변에 대한 댓글 목록
            - 댓글 작성자 정보
                - 프로필 썸네일 이미지
                - 유저 닉네임
            - 댓글 내용
            - 댓글 작성일시
        """,
        responses={
            200: ser_q_res.QuestionDetailSerializer,
            400: OpenApiResponse(
                description="Bad Request",
                response=dict,
                examples=[
                    OpenApiExample(
                        name="잘못된 요청 예시",
                        value={"error_detail": "유효하지 않은 질문 상세 조회 요청입니다."},
                        description="잘못된 요청 예시",
                    ),
                ],
            ),
            404: OpenApiResponse(
                description="Not Found",
                response=dict,
                examples=[
                    OpenApiExample(
                        name="존재하지 않는 질문 예시",
                        value={"error_detail": "해당 질문을 찾을 수 없습니다."},
                        description="존재하지 않는 질문 예시",
                    ),
                ],
            ),
        },
        tags=["qna"],
    )
    def get(self, request: Request, question_id: int) -> Response:
        # Mock Data 생성
        if settings.USE_EXAM_MOCK:
            User = get_user_model()
            mock_user = User(
                id=1,
                nickname="MockUser",
                profile_img_url="https://ssl.pstatic.net/static/pwe/address/img_profile.png",
            )

            cat_root = QuestionCategory(id=1, name="개발")
            cat_mid = QuestionCategory(id=2, name="백엔드", parent=cat_root)
            cat_leaf = QuestionCategory(id=3, name="Django", parent=cat_mid)

            question = Question(
                id=question_id,
                author=mock_user,
                category=cat_leaf,
                title=f"Mock 상세 질문 제목 {question_id}",
                content=f"Mock 상세 질문 내용입니다.\n\n![img](https://via.placeholder.com/200)",
                view_count=123,
                created_at=datetime.now(),
            )

            # Mock Images
            setattr(
                question,
                "images",
                [
                    QuestionImage(id=1, img_url="https://via.placeholder.com/200"),
                    QuestionImage(id=2, img_url="https://via.placeholder.com/201"),
                ],
            )

            # Mock Answers
            ans1 = Answer(
                id=1,
                question=question,
                author=mock_user,
                content="Mock 답변 내용 1",
                created_at=datetime.now(),
                is_adopted=False,
            )

            # Mock Comments for Answer
            setattr(
                ans1,
                "comments",
                [
                    AnswerComment(
                        id=1,
                        answer=ans1,
                        author=mock_user,
                        content="Mock 댓글 1",
                        created_at=datetime.now(),
                    )
                ],
            )

            setattr(question, "answers", [ans1])

        else:
            question = svc_q_qry.QuestionQueryService.get_question_detail(question_id)

        serializer = ser_q_res.QuestionDetailSerializer(question)
        return Response(serializer.data, status=status.HTTP_200_OK)
