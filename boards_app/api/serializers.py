from rest_framework import serializers
from boards_app.models import Board
from auth_app.models import User
from task_app.api.serializers import TaskReadSerializer
from auth_app.api.serializers import MemberSerializer


class BoardListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing boards with summary information.

    - Provides board id and title.
    - Includes aggregated counts:
        * member_count: number of board members
        * ticket_count: total number of tasks
        * tasks_to_do_count: tasks with status 'to-do'
        * tasks_high_prio_count: tasks with priority 'high'
    - Exposes the owner's id.
    """
    member_count = serializers.SerializerMethodField()
    ticket_count = serializers.SerializerMethodField()
    tasks_to_do_count = serializers.SerializerMethodField()
    tasks_high_prio_count = serializers.SerializerMethodField()
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)

    class Meta:
        model = Board
        fields = [
            'id',
            'title',
            'member_count',
            'ticket_count',
            'tasks_to_do_count',
            'tasks_high_prio_count',
            'owner_id'
        ]

    def get_member_count(self, obj):
        return obj.members.count()

    def get_ticket_count(self, obj):
        return obj.tasks.count()

    def get_tasks_to_do_count(self, obj):
        return obj.tasks.filter(status='to-do').count()

    def get_tasks_high_prio_count(self, obj):
        return obj.tasks.filter(priority='high').count()


class BoardDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed board representation.

    - Provides board id, title, and owner_id.
    - Includes nested member data via MemberSerializer.
    - Includes nested task data via TaskReadSerializer.
    - All related fields (owner_id, members, tasks) are read-only.
    """
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)
    members = MemberSerializer(many=True, read_only=True)
    tasks = TaskReadSerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'owner_id', 'members', 'tasks']
        read_only_fields = ['owner_id', 'members', 'tasks']


class BoardCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating boards.

    - Accepts a list of member IDs for assignment (write-only).
    - Exposes owner_data and members_data via MemberSerializer (read-only).
    - On create:
        * Creates a new board with provided title and owner.
        * Assigns members if member IDs are provided.
    - On update:
        * Updates the board title.
        * Replaces members if member IDs are provided.
    """
    members = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    owner_data = MemberSerializer(source='owner', read_only=True)
    members_data = MemberSerializer(
        source='members', many=True, read_only=True)

    class Meta:
        model = Board
        fields = ['id', 'title', 'members', 'owner_data', 'members_data']
        read_only_fields = ['owner_data', 'members_data']

    def create(self, validated_data):
        member_ids = validated_data.pop('members', [])
        board = Board.objects.create(**validated_data)

        if member_ids:
            members = User.objects.filter(id__in=member_ids)
            board.members.set(members)

        return board

    def update(self, instance, validated_data):
        member_ids = validated_data.pop('members', None)

        instance.title = validated_data.get('title', instance.title)
        instance.save()

        if member_ids is not None:
            members = User.objects.filter(id__in=member_ids)
            instance.members.set(members)

        return instance
