from rest_framework import serializers
from boards_app.models import Board
from auth_app.models import User
from task_app.api.serializers import TaskSerializer

class MemberSerializer(serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'fullname', 'email']

    def get_fullname(self, obj):
        if hasattr(obj, "fullname"):
            return obj.fullname
        return f"{obj.first_name} {obj.last_name}".strip()

class BoardSerializer(serializers.ModelSerializer):
    members = MemberSerializer(many=True, read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner', 'members', 'tasks']
        read_only_fields = ['owner', 'members', 'tasks']