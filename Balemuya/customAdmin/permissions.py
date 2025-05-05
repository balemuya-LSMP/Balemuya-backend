from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.user_type == 'admin' and request.user.is_active==True
