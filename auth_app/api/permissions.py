from rest_framework import permissions


class IsSelfOrBoardMember(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj == request.user:
            return True
        
        user_boards = request.user.member_boards.all() | request.user.owned_boards.all()
        target_boards = obj.member_boards.all() | obj.owned_boards.all()
        
        return bool(user_boards & target_boards)