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
    assignee = MemberSerializer(read_only=True)
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
        return last.text if last else None


class TaskWriteSerializer(serializers.ModelSerializer):
    assignee = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), required=False, allow_null=True
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

    def _resolve_user_by_email(self, email):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": f"User mit E-Mail '{email}' nicht gefunden."})

    def validate(self, attrs):
        board = attrs.get("board")
        if not board:
            return attrs

        assignee_email = attrs.pop("assignee_email", None)
        if assignee_email and not attrs.get("assignee"):
            attrs["assignee"] = self._resolve_user_by_email(assignee_email)

        reviewer_emails = attrs.pop("reviewer_emails", None)
        if reviewer_emails and not attrs.get("reviewers"):
            resolved = [self._resolve_user_by_email(e) for e in reviewer_emails]
            attrs["reviewers"] = resolved

        assignee = attrs.get("assignee", None)
        reviewers = attrs.get("reviewers", [])

        allowed = set(board.members.all()) | {board.owner}

        if assignee and assignee not in allowed:
            raise serializers.ValidationError({"assignee": "Assignee muss Mitglied oder Owner des Boards sein."})

        for r in reviewers:
            if r not in allowed:
                raise serializers.ValidationError({"reviewers": "Alle Reviewer müssen Mitglieder oder Owner des Boards sein."})

        return attrs

    def create(self, validated_data):
        reviewers = validated_data.pop("reviewers", [])
        task = super().create(validated_data)
        if reviewers:
            task.reviewers.set(reviewers)
        return task

    def update(self, instance, validated_data):
        reviewers = validated_data.pop("reviewers", None)
        task = super().update(instance, validated_data)
        if reviewers is not None:
            task.reviewers.set(reviewers)
        return task

class BoardSerializer(serializers.ModelSerializer):
    owner = MemberSerializer(read_only=True)
    members = MemberSerializer(many=True, read_only=True)
    tasks = TaskReadSerializer(many=True, read_only=True, source="tasks")

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner', 'members', 'tasks']
        read_only_fields = ['owner', 'members', 'tasks']