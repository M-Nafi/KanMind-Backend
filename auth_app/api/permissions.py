from rest_framework import permissions


class IsSelfOrBoardMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        """
        Check if the request.user has permission to access the object.

        - If the object is the request.user itself, return True.
        - Otherwise, return True if the request.user and the object
        share at least one board (either as members or owners).
        """
        if obj == request.user:
            return True
        
        user_boards = request.user.member_boards.all() | request.user.owned_boards.all()
        target_boards = obj.member_boards.all() | obj.owned_boards.all()
        
        return bool(user_boards & target_boards)