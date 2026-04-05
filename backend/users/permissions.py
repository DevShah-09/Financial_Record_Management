from rest_framework.permissions import BasePermission, SAFE_METHODS

class DenyAll(BasePermission):
    def has_permission(self, request, view):
        return False

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
    - Admins can access/edit anything.
    - Analysts can view (GET) anything but only edit their own.
    - Viewers are usually blocked at the ViewSet level, but this provides a fallback.
    """
    def has_object_permission(self, request, view, obj):
        # Admin users can access any object for oversight
        if request.user.role == 'admin':
            return True
        
        # Analysts can view all records but cannot modify them unless they own them
        if request.user.role == 'analyst' and request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
            
        return obj.user == request.user