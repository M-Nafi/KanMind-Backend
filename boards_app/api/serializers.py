from rest_framework import serializers
from boards_app.models import Board
from auth_app.models import User
from task_app.api.serializers import TaskReadSerializer
from auth_app.api.serializers import MemberSerializer

class BoardSerializer(serializers.ModelSerializer):
    members = MemberSerializer(many=True, read_only=True)
    tasks = TaskReadSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner', 'members', 'tasks']
        read_only_fields = ['owner', 'members', 'tasks']