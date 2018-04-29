from rest_framework.permissions import BasePermission


class IsAuthenticatedSelf(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Check if the user owns the account
        authenticated_user_id = request.user.identifier

        if obj.identifier == authenticated_user_id:
            return True
        else:
            return False
