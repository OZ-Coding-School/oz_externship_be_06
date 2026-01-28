from rest_framework.pagination import PageNumberPagination


# 어드민 목록 조회용 페이지네이션
class AdminListPagination(PageNumberPagination):

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100
