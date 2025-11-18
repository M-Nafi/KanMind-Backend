from rest_framework import serializers
from auth_app.models import User
from boards_app.models import Board
from task_app.models import Comment, Task

class MemberSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'fullname', 'email']

    def get_fullname(self, obj):
        if getattr(obj, "fullname", None):
            return str(obj.fullname).strip()
        return f"{obj.first_name} {obj.last_name}".strip()


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    content = serializers.CharField(source="text")

    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'created_at']
        extra_kwargs = {
            'text': {'required': False}
        }

    def get_author(self, obj):
        if getattr(obj.author, "fullname", None):
            return str(obj.author.fullname).strip()
        return f"{obj.author.first_name or ''} {obj.author.last_name or ''}".strip()


class TaskSerializer(serializers.ModelSerializer):
    assigned_to = MemberSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'done',
            'board', 'assigned_to',
            'due_date', 'priority', 'status', 'comments'
        ]


class BoardSerializer(serializers.ModelSerializer):
    owner = MemberSerializer(read_only=True)                    
    members = MemberSerializer(many=True, read_only=True)       
    tasks = TaskSerializer(many=True, read_only=True, source="tasks")

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner', 'members', 'tasks']
        read_only_fields = ['owner', 'members', 'tasks']