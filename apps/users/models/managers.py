"""
마이그레이션 호환용 코드
- 과거 마이그레이션에서 UserManager를 참조하고 있음
- 지금 코드에서 안 써도 삭제하면 migrate/createsuperuser 깨짐
- 마이그레이션 리팩토링 전까지 절대 삭제 금지
"""

from __future__ import annotations

from django.contrib.auth.models import BaseUserManager
from django.db import models


class UserManager(BaseUserManager[models.Model]):

    use_in_migrations = True
