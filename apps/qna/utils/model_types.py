from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model

# Mypy가 이 모듈의 User를 명시적인 내보내기(Export)로 인식하도록 __all__을 정의
__all__ = ["User"]

# TYPE_CHECKING 블록을 통해 IDE 자동 완성(Static Analysis)을 지원하면서도
# 런타임의 순환 참조(Circular Import) 문제를 원천 차단합니다.
if TYPE_CHECKING:
    # 정적 분석 시에는 실제 모델 클래스를 참조하여 자동 완성을 지원받습니다.
    from apps.users.models import User
else:
    # 런타임에는 get_user_model()을 통해 동적으로 유저 모델을 가져와 순환 참조를 방지합니다.
    User = get_user_model()
