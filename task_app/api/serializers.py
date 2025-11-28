from rest_framework import serializers
from auth_app.models import User
from task_app.models import Comment, Task
from auth_app.api.serializers import MemberSerializer


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'created_at']
        extra_kwargs = {
            'content': {'source': 'text'}
        }

    def get_author(self, obj):
        return obj.author.fullname or obj.author.username


class TaskReadSerializer(serializers.ModelSerializer):
    assignee = MemberSerializer(read_only=True)
    reviewer = MemberSerializer(read_only=True)
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'board', 'title', 'description', 'status', 'priority',
            'assignee', 'reviewer', 'due_date', 'comments_count'
        ]

    def get_comments_count(self, obj):
        return obj.comments.count()


class TaskWriteSerializer(serializers.ModelSerializer):
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
        source='assignee'
    )
    reviewer_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False,
        allow_null=True,
        source='reviewer'
    )

    class Meta:
        model = Task
        fields = [
            'board', 'title', 'description', 'status', 'priority',
            'assignee_id', 'reviewer_id', 'due_date'
        ]

    def validate(self, attrs):
        board = attrs.get("board")
        assignee = attrs.get("assignee")
        reviewer = attrs.get("reviewer")
        
        if not board and self.instance:
            board = self.instance.board
        
        if self.instance and board and board != self.instance.board:
            raise serializers.ValidationError({
                "board": "Das Ändern der Board-ID ist nicht erlaubt!"
            })
            
        if board:
            allowed = set(board.members.all()) | {board.owner}
            if assignee and assignee not in allowed:
                raise serializers.ValidationError({
                    "assignee_id": "Assignee muss Mitglied oder Owner des Boards sein."
                })
            if reviewer and reviewer not in allowed:
                raise serializers.ValidationError({
                    "reviewer_id": "Reviewer muss Mitglied oder Owner des Boards sein."
                })
        return attrs