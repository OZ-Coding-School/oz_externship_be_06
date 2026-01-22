# mypy: ignore-errors
from __future__ import annotations

from typing import Any, ClassVar

from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from apps.core.models import TimeStampModel


class UserManager(BaseUserManager["User"]):
    use_in_migrations = True

    def create_user(
        self,
        email: str,
        password: str | None = None,
        **extra_fields: Any,
    ) -> "User":
        if not email:
            raise ValueError("The Email must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(
        self,
        email: str,
        password: str,
        **extra_fields: Any,
    ) -> "User":
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email=email, password=password, **extra_fields)


class User(TimeStampModel, AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        USER = "USER", "일반회원"
        ADMIN = "ADMIN", "관리자"
        TA = "TA", "조교"
        OM = "OM", "운영매니저"
        LC = "LC", "러닝코치"
        STUDENT = "STUDENT", "수강생"

    class Gender(models.TextChoices):
        MALE = "MALE", "남성"
        FEMALE = "FEMALE", "여성"

    email = models.EmailField(unique=True)

    name = models.CharField(max_length=30)
    nickname = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=20)

    gender = models.CharField(
        max_length=6,
        choices=Gender.choices,
    )
    birthday = models.DateField()

    profile_img_url = models.CharField(max_length=255, null=True, blank=True)

    is_active: bool = models.BooleanField(default=True)
    is_staff: bool = models.BooleanField(default=False)

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.USER,
    )

    objects: ClassVar[UserManager] = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        db_table = "user"
