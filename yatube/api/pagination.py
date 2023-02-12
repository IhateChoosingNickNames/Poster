from rest_framework import pagination
from rest_framework.response import Response


class CustomPagination(pagination.PageNumberPagination):
    """Пагинация в виде списка."""

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 10000

    def get_paginated_response(self, data):
        return Response(data)
