from typing import cast

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.posts.constants.post_const import PostLikeMessage
from apps.posts.services.post_like_service import PostLikeService
from apps.users.models import User


class PostLikeAPIView(APIView):
    """
    게시글 좋아요 관련 API
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["posts"],
        summary="게시글 좋아요 등록",
        description="인증된 사용자가 특정 게시글에 좋아요를 등록합니다.",
        responses={
            201: OpenApiResponse(description=PostLikeMessage.LIKE_REGISTER),
            400: OpenApiResponse(description="잘못된 요청"),
            401: OpenApiResponse(description="인증 자격 증명이 유효하지 않음"),
            404: OpenApiResponse(description="게시글을 찾을 수 없음"),
        },
    )
    def post(self, request: Request, post_id: int) -> Response:
        """게시글 좋아요 등록 (POST)"""
        user = cast(User, request.user)
        PostLikeService.register_like(user=user, post_id=post_id)

        return Response({"detail": PostLikeMessage.LIKE_REGISTER}, status=status.HTTP_201_CREATED)

    @extend_schema(
        tags=["posts"],
        summary="게시글 좋아요 취소",
        description="인증된 사용자가 특정 게시글의 좋아요를 취소합니다.",
        responses={
            200: OpenApiResponse(description=PostLikeMessage.LIKE_CANCEL),
            401: OpenApiResponse(description="인증 자격 증명이 유효하지 않음"),
            404: OpenApiResponse(description="게시글을 찾을 수 없음"),
        },
    )
    def delete(self, request: Request, post_id: int) -> Response:
        """게시글 좋아요 취소 (DELETE)"""
        user = cast(User, request.user)
        PostLikeService.cancel_like(user=user, post_id=post_id)

        return Response({"detail": PostLikeMessage.LIKE_CANCEL}, status=status.HTTP_200_OK)
