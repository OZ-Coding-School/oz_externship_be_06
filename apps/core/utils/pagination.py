from __future__ import annotations

from rest_framework.pagination import CursorPagination, PageNumberPagination


class ChatbotSessionCursorPagination(CursorPagination):
    page_size = 10
    ordering = "-created_at"
    cursor_query_param = "cursor"


class SimplePagePagination(PageNumberPagination):
    page_size = 10
    page_query_param = "page"
