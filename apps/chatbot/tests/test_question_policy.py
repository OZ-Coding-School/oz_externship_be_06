from typing import Any, Dict, Optional, Type, TypeVar, cast

from django.db import models
from django.utils import timezone

T = TypeVar("T", bound=models.Model)


def _build_required_kwargs(
    model_cls: Type[models.Model],
    *,
    depth: int = 0,
) -> Dict[str, Any]:
    kwargs: Dict[str, Any] = {}

    for field in model_cls._meta.get_fields():
        if not isinstance(field, models.Field):
            continue
        if getattr(field, "auto_created", False):
            continue
        if field.primary_key:
            continue

        name = field.name
        has_default = field.has_default()
        required = not field.null and not field.blank and not has_default

        if not required:
            continue

        if isinstance(field, models.ForeignKey):
            if depth >= 1:
                raise RuntimeError(f"Nested FK too deep: {model_cls.__name__}.{name}")
            kwargs[name] = _create_instance(
                field.remote_field.model,
                depth=depth + 1,
            )
            continue

        if isinstance(field, models.CharField):
            kwargs[name] = field.choices[0][0] if field.choices else "test"
        elif isinstance(field, models.TextField):
            kwargs[name] = "test"
        elif isinstance(field, models.BooleanField):
            kwargs[name] = False
        elif isinstance(field, models.IntegerField):
            kwargs[name] = 1
        elif isinstance(field, models.DateTimeField):
            kwargs[name] = timezone.now()
        else:
            kwargs[name] = "test"

    return kwargs


def _create_instance(
    model_cls: Type[T],
    *,
    depth: int = 0,
    overrides: Optional[Dict[str, Any]] = None,
) -> T:
    overrides = overrides or {}
    kwargs = _build_required_kwargs(model_cls, depth=depth)
    kwargs.update(overrides)

    manager = cast(Any, model_cls).objects
    return cast(T, manager.create(**kwargs))
