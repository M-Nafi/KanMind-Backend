from rest_framework import permissions


class IsBoardMemberOrOwner(permissions.BasePermission):
    """
    Permission class that grants access if the user is either:

    - The owner of the board, or
    - A member of the board.

    Used to restrict object-level access to board resources
    based on ownership or membership.
    """
    def has_object_permission(self, request, view, obj):
        return (
            obj.owner == request.user or 
            request.user in obj.members.all()
        )


class IsBoardOwner(permissions.BasePermission):
    """
    Permission class that grants access only if the user
    is the owner of the board.

    Used to enforce stricter object-level access control
    where only board owners are allowed.
    """
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user