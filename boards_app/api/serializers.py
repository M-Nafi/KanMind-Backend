from rest_framework import serializers
from boards_app.models import Board
from task_app.models import Task
from auth_app.models import User

class MemberSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'fullname', 'email']

    def get_fullname(self, obj):
        if hasattr(obj, "fullname"):
            return obj.fullname
        return f"{obj.first_name} {obj.last_name}".strip()

class TaskSerializer(serializers.ModelSerializer):
    assigned_to = MemberSerializer(read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'done', 'assigned_to']

class BoardSerializer(serializers.ModelSerializer):
    members = MemberSerializer(many=True, read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner', 'members', 'tasks']
        read_only_fields = ['owner', 'members', 'tasks']