from django.db import models
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from boards_app.models import Board
from .serializers import BoardListSerializer, BoardDetailSerializer, BoardCreateUpdateSerializer
from .permissions import IsBoardMemberOrOwner, IsBoardOwner


class BoardViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing boards.

    - Requires authentication for all actions.
    - Queryset behavior:
        * list: returns boards where the user is owner or member.
        * other actions: returns all boards.
    - Serializer selection:
        * list: uses BoardListSerializer (summary view).
        * retrieve: uses BoardDetailSerializer (detailed view).
        * create/update/partial_update: uses BoardCreateUpdateSerializer.
    - Permission rules:
        * destroy: only board owners can delete.
        * update/partial_update/retrieve: allowed for board owners or members.
        * other actions: requires authentication only.
    - On create: automatically assigns the requesting user as the board owner.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if self.action == 'list':
            return Board.objects.filter(
                models.Q(owner=user) | models.Q(members=user)
            ).distinct()

        return Board.objects.all()

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
