from rest_framework import serializers
from auth_app.models import User
from boards_app.models import Board
from task_app.models import Comment, Task
from auth_app.api.serializers import MemberSerializer


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



class TaskReadSerializer(serializers.ModelSerializer):
    assignee = MemberSerializer(source="assigned_to", read_only=True)
    reviewer = MemberSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    comments_count = serializers.SerializerMethodField()
    last_comment = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'done',
            'board', 'assignee', 'reviewer',
            'due_date', 'priority', 'status',
            'comments', 'comments_count', 'last_comment'
        ]

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_last_comment(self, obj):
        last = obj.comments.order_by('-created_at').first()
        if last:
            return last.text
        return None


class TaskWriteSerializer(serializers.ModelSerializer):
    assignee = serializers.PrimaryKeyRelatedField(
        source="assigned_to", queryset=User.objects.all(),
        required=False, allow_null=True
    )
    reviewer = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Task
        fields = [
            'title', 'description', 'done',
            'board', 'assignee', 'reviewer',
            'due_date', 'priority', 'status'
        ]


class BoardSerializer(serializers.ModelSerializer):
    owner = MemberSerializer(read_only=True)
    members = MemberSerializer(many=True, read_only=True)
    tasks = TaskReadSerializer(many=True, read_only=True, source="tasks")

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner', 'members', 'tasks']
        read_only_fields = ['owner', 'members', 'tasks']