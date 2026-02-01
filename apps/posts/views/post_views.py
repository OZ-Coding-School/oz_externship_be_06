from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.posts.constants.post_const import PostSuccessMessage, PostErrorMessage
from apps.posts.exceptions.post_exceptions import PostUnauthorizedException
from apps.posts.serializers.post_serializers import PostCreateSerializer
from apps.posts.services.post_services import PostService


class PostCreateView(APIView):
    permission_classes = [IsAuthenticated]

    # 401 명세서와 일치
    def permission_denied(self, request, message = None, code = None):
        raise PostUnauthorizedException()

    @extend_schema(
        summary="게시글 생성",
        request=PostCreateSerializer,
        tags=["posts"],
    )
    def post(self, request: Request) -> Response:
        serializer = PostCreateSerializer(data=request.data)

        # 400 : Bad Request
        if not serializer.is_valid():
            return Response(
                {"error_detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            post = PostService.create_post(
                user=request.user,
                **serializer.validated_data,
            )

            # 201 : Created
            return Response(
                {
                    "detail": PostSuccessMessage.POST_CREATE_SUCCESS,
                    "pk": post.id
                },
                status=status.HTTP_201_CREATED
            )
        except Exception:
            # 500 : Internal Server Error
            return Response(
                {"error_detail": PostErrorMessage.SERVER_ERROR},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )