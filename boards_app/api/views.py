from rest_framework import viewsets
from boards_app.models import Board
from .serializers import BoardSerializer
from rest_framework.decorators import action
from rest_framework.response import Response

class BoardViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer

    @action(detail=False, methods=['get'], url_path='owned-by-me')
    def owned_by_me(self, request):
        boards = Board.objects.filter(owner=request.user)
        serializer = BoardSerializer(boards, many=True)
        return Response(serializer.data)