from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from task_app.models import Task, Comment
from task_app.api.serializers import (
    TaskReadSerializer,
    TaskWriteSerializer,
    CommentSerializer,
)


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TaskWriteSerializer
        return TaskReadSerializer

    @action(detail=True, methods=['get', 'post'])
    def comments(self, request, pk=None):
        task = self.get_object()
        if request.method == 'GET':
            serializer = CommentSerializer(task.comments.all(), many=True)
            return Response(serializer.data)
        elif request.method == 'POST':
            serializer = CommentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(task=task, author=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='assigned-to-me')
    def assigned_to_me(self, request):
        tasks = Task.objects.filter(assignee=request.user)
        serializer = TaskReadSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='reviewing')
    def reviewing(self, request):
        tasks = Task.objects.filter(reviewer=request.user)
        serializer = TaskReadSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        task_id = self.kwargs.get("task_pk")
        return Comment.objects.filter(task_id=task_id)

    def perform_create(self, serializer):
        task_id = self.kwargs.get("task_pk")
        task = Task.objects.get(pk=task_id)
        serializer.save(task=task, author=self.request.user)