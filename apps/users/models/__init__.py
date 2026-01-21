from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UserManager

__all__ = ["User", "UserManager"]


class User(AbstractUser):
    nickname = models.CharField(max_length=30)

    class Meta:
        db_table = "user"
