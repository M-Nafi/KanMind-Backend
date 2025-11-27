from rest_framework import permissions


class IsTaskBoardMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        board = obj.board
        return (
            board.owner == request.user or 
            request.user in board.members.all() or
            request.user.is_superuser
        )