from django.db import models
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from boards_app.models import Board
from .serializers import BoardListSerializer, BoardDetailSerializer, BoardCreateUpdateSerializer
from .permissions import IsBoardMemberOrOwner, IsBoardOwner


class BoardViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(
            models.Q(owner=user) | models.Q(members=user)
        ).distinct()

    def get_serializer_class(self):
        if self.action == 'list':
            return BoardListSerializer
        elif self.action == 'retrieve':
            return BoardDetailSerializer
        else:
            return BoardCreateUpdateSerializer

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAuthenticated(), IsBoardOwner()]
        elif self.action in ['update', 'partial_update', 'retrieve']:
            return [IsAuthenticated(), IsBoardMemberOrOwner()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)