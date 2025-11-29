from rest_framework import permissions


class IsTaskBoardMember(permissions.BasePermission):
    """
    Permission class that grants access if the requesting user
    is either the board owner or a member of the board
    associated with the task.
    """

    def has_object_permission(self, request, view, obj):
        board = obj.board
        return (
            board.owner == request.user or
            request.user in board.members.all()
        )


class IsTaskCreatorOrBoardOwner(permissions.BasePermission):
    """
    Permission class that grants access if the requesting user
    is either the creator of the task or the owner of the board
    to which the task belongs.
    """

    def has_object_permission(self, request, view, obj):
        return (
            obj.created_by == request.user or
            obj.board.owner == request.user
        )


class IsCommentAuthor(permissions.BasePermission):
    """
    Permission class that grants access only if the requesting user
    is the author of the comment.
    """

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
