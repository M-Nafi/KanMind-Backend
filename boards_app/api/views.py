from rest_framework import viewsets
from boards_app.models import Board
from .serializers import BoardSerializer

class BoardViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer