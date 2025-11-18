from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from task_app.models import Task, Comment
from task_app.api.serializers import TaskSerializer, CommentSerializer

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

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
                return Response(serializer.data, status=201)
            return Response(serializer.errors, status=400)