from rest_framework import permissions


class IsBoardOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.owner == request.user or request.user in obj.members.all()
        
        return obj.owner == request.user


class IsBoardOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or request.user.is_superuser