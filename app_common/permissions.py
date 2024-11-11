from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow users to edit only their own objects.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            if request.user.is_authenticated:
                return True

        return (obj.user == request.user) or request.user.is_superuser


class IsItsOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow users to edit only their own objects.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            if request.user.is_authenticated:
                return True

        return obj == request.user or request.user.is_superuser
