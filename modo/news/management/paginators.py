from rest_framework.pagination import CursorPagination


class ArticlePaginator(CursorPagination):
    ordering = '-publish_time'
    page_size = 40
