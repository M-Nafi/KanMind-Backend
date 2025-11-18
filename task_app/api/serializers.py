from rest_framework import serializers
from auth_app.models import User
from boards_app.models import Board
from task_app.models import Task

class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'fullname', 'email']


class TaskSerializer(serializers.ModelSerializer):
    assigned_to = MemberSerializer(read_only=True)

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