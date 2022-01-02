from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class VariablePageSizePagination(PageNumberPagination):
    page_size = 25
    max_page_size = 100
    page_size_query_param = "page_size"

    def get_paginated_response(self, data) -> Response:
        if self.request.GET.get("no_pagination"):
            return Response(data)

        return super().get_paginated_response(data)
