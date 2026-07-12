from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow Admin users to write (create, edit, delete).
    Others can read.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'admin'
        )

class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow Admin role users to execute the action.
    """
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role == 'admin'
        )

class IsTeamManagerOrAdmin(permissions.BasePermission):
    """
    Custom permission to allow Managers and Admins to register a team.
    Only the assigned team manager or an Admin can edit/delete it.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            request.user and
            request.user.is_authenticated and
            request.user.role in ['manager', 'admin']
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.role == 'admin':
            return True
        return obj.manager == request.user
