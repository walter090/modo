from rest_framework.pagination import CursorPagination


class UserPaginator(CursorPagination):
    page_size = 50
    ordering = '-registered_since'
