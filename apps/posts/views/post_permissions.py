from rest_framework import permissions

class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    객체의 작성자만 수정 및 삭제가 가능하도록 하는 커스텀 권한 클래스입니다.
    """

    def has_object_permission(self, request, view, obj):
        # GET, HEAD, OPTIONS 요청은 인증 여부에 상관없이 허용합니다.
        if request.method in permissions.SAFE_METHODS:
            return True

        # 그 외(PUT, PATCH, DELETE) 요청은 게시글의 작성자(author)가 로그인한 사용자와 같을 때만 허용합니다.
        # Post 모델의 author 필드와 비교합니다.
        return obj.author == request.user