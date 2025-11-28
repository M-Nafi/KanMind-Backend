from rest_framework import permissions


class IsTaskBoardMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        board = obj.board
        return (
            board.owner == request.user or 
            request.user in board.members.all()
        )


class IsTaskCreatorOrBoardOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return (
            obj.created_by == request.user or
            obj.board.owner == request.user
        )


class IsCommentAuthor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user