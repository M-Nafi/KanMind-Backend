from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from boards_app.models import Board
from auth_app.models import User
from .serializers import BoardSerializer
from .permissions import IsBoardOwner, IsBoardOwnerOrReadOnly
from auth_app.api.views import PENDING_MEMBERS


class BoardViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['add_member', 'remove_member']:
            return [IsAuthenticated(), IsBoardOwner()]
        return super().get_permissions()

    @action(detail=False, methods=['get'], url_path='owned-by-me')
    def owned_by_me(self, request):
        boards = Board.objects.filter(owner=request.user)
        serializer = BoardSerializer(boards, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        board = serializer.save(owner=self.request.user)
        user_id = self.request.user.id
        email = PENDING_MEMBERS.pop(user_id, None)
        if email:
            try:
                user = User.objects.get(email=email)
                board.members.add(user)
            except User.DoesNotExist:
                pass

    @action(detail=True, methods=['post'], url_path='add-member')
    def add_member(self, request, pk=None):
        board = self.get_object()
        
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        board.members.add(user)
        serializer = BoardSerializer(board)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='remove-member')
    def remove_member(self, request, pk=None):
        board = self.get_object()
        
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        board.members.remove(user)
        serializer = BoardSerializer(board)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='members')
    def list_members(self, request, pk=None):
        board = self.get_object()
        
        if board.owner != request.user and request.user not in board.members.all():
            return Response({'error': 'Not allowed'}, status=status.HTTP_403_FORBIDDEN)

        members = board.members.all()
        data = [{'fullname': m.fullname, 'email': m.email} for m in members]
        return Response({'board': board.title, 'members': data}, status=status.HTTP_200_OK)