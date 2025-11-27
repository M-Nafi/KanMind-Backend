from rest_framework import serializers
from boards_app.models import Board
from auth_app.models import User
from task_app.api.serializers import TaskReadSerializer
from auth_app.api.serializers import MemberSerializer


class BoardSerializer(serializers.ModelSerializer):
    owner = MemberSerializer(read_only=True)
    members = MemberSerializer(many=True, read_only=True)
    tasks = TaskReadSerializer(many=True, read_only=True)
    member_emails = serializers.ListField(
        child=serializers.EmailField(allow_null=True),
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner', 'members', 'member_emails', 'tasks']
        read_only_fields = ['owner', 'members', 'tasks']
