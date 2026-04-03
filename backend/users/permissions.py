from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'admin'


class IsAnalystOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role in ['analyst', 'admin']


class IsViewer(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == 'viewer'


class IsOwner(BasePermission):
    """
    Object-level permission to only allow owners of an object to access or edit it.
    Assumes the model instance has a `user` attribute.
    """
    def has_object_permission(self, request, view, obj):
        # Admin users can access any object for oversight
        if request.user.role == 'admin':
            return True
        return obj.user == request.user