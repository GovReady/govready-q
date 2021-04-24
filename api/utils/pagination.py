from rest_framework import pagination
from rest_framework.pagination import _positive_int
from rest_framework.response import Response


class Pagination(pagination.PageNumberPagination):

    page_size = 20
    page_size_query_param = 'count'
    max_page_size = 100

    def get_paginated_response(self, data):

        try:
            prev_page = self.page.previous_page_number()
        except Exception:
            prev_page = None
        try:
            next_page = self.page.next_page_number()
        except Exception:
            next_page = None

        try:
            page_size = _positive_int(
                self.request.query_params[self.page_size_query_param],
                strict=True,
                cutoff=self.max_page_size
            )
        except (KeyError, ValueError):
            page_size = self.page_size

        ending_record = self.page.number * page_size
        if ending_record > self.page.paginator.count:
            ending_record = self.page.paginator.count

        starting_record = ((self.page.number - 1) * page_size)
        return Response({
            'pages': {
                'total_pages': self.page.paginator.num_pages,
                'current_page': self.page.number,
                'next_page': next_page,
                'prev_page': prev_page,
                'starting_record': starting_record + 1 if starting_record else 0,
                'ending_record': ending_record,
                'total_records': self.page.paginator.count,

            },
            'data': data
        })
