from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from task_app.models import Task, Comment
from task_app.api.serializers import TaskReadSerializer, TaskWriteSerializer, CommentSerializer
from task_app.api.permissions import IsTaskBoardMember, IsTaskCreatorOrBoardOwner, IsCommentAuthor


class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tasks.

    - Requires authentication and board membership for most actions.
    - Serializer selection:
        * create/update/partial_update: TaskWriteSerializer
        * other actions: TaskReadSerializer
    - Permission rules:
        * destroy: only task creator or board owner can delete
        * other actions: board members or owner
    - On create: automatically sets the requesting user as task creator.
    - Custom actions:
        * assigned-to-me: returns tasks assigned to the requesting user.
        * reviewing: returns tasks where the requesting user is the reviewer.
    """
    queryset = Task.objects.all()
    permission_classes = [IsAuthenticated, IsTaskBoardMember]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TaskWriteSerializer
        return TaskReadSerializer

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAuthenticated(), IsTaskCreatorOrBoardOwner()]
        return [IsAuthenticated(), IsTaskBoardMember()]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

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
    """
    ViewSet for managing comments on tasks.

    - Requires authentication for all actions.
    - Queryset is restricted to comments belonging to the given task (task_pk).
    - Permission rules:
        * destroy: only the comment author can delete
        * other actions: any authenticated user
    - On create: automatically assigns the requesting user as author
      and links the comment to the specified task.
    """
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        task_id = self.kwargs.get("task_pk")
        return Comment.objects.filter(task_id=task_id)

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAuthenticated(), IsCommentAuthor()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        task_id = self.kwargs.get("task_pk")
        task = Task.objects.get(pk=task_id)
        serializer.save(task=task, author=self.request.user)
