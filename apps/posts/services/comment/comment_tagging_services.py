import re
from typing import Set

from django.contrib.auth import get_user_model
from django.db import transaction

from apps.posts.models.post_comment import PostComment

UserModel = get_user_model()


def process_comment_tagging(comment: PostComment, content: str) -> None:
    """
    댓글 본문에서 유저 태깅(@닉네임) 패턴을 분석하여 처리하는 서비스 함수입니다.

    작동 원리:
    1. 정규표현식을 이용해 본문 내 모든 '@닉네임' 형태를 추출합니다.
    2. 기존에 저장된 태그 정보가 있다면 데이터 정합성을 위해 모두 삭제합니다(갱신 로직).
    3. 추출된 닉네임 중 실제 DB에 존재하는 유저들을 조회하여 매핑합니다.
    4. 대량의 태그가 발생할 경우를 대비하여 bulk_create로 성능을 최적화합니다.

    Args:
        comment (PostComment): 태그가 연결될 댓글 객체
        content (str): 분석할 댓글 본문 텍스트
    """
    # [단계 1] 본문에서 @닉네임 패턴 추출
    # - r"@([^\s@]+)": @로 시작하고, 그 뒤에 공백(\s)이나 @가 아닌 문자들을 하나 이상(+) 캡처합니다.
    # - set()을 사용하여 중복된 닉네임 언급은 한 번만 처리하도록 합니다.
    nicknames: Set[str] = set(re.findall(r"@([^\s@]+)", content))

    # 데이터 변경 작업이므로 원자성(Atomic)을 보장합니다.
    with transaction.atomic():
        # [단계 2] 기존 태그 정보 초기화
        # 댓글 수정 시 태그가 추가되거나 삭제될 수 있으므로, 기존 데이터를 삭제하고 최신 상태로 재구축합니다.
        comment.tags.all().delete()

        # 언급된 닉네임이 없다면 처리를 종료합니다.
        if not nicknames:
            return

        # [단계 3] 실제 존재하는 유저인지 DB 확인
        # - 닉네임으로 유저 모델을 조회하며, 존재하지 않는 닉네임 언급은 무시됩니다.
        tagged_users = UserModel.objects.filter(nickname__in=nicknames)

        # [단계 4] 새로운 태그 정보 일괄 생성
        from apps.posts.models.post_comment_tags import PostCommentTag

        # 리스트 컴프리헨션을 사용하여 PostCommentTag 객체 목록을 생성합니다.
        tags = [PostCommentTag(comment=comment, tagged_user=user) for user in tagged_users]

        # 성능을 위해 여러 개의 레코드를 한 번의 쿼리로 삽입합니다.
        PostCommentTag.objects.bulk_create(tags)
