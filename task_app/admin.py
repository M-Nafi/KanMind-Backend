from django.contrib import admin
from task_app.models import Task, Comment


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'board', 'status', 'priority', 'assignee', 'reviewer', 'created_by')
    list_filter = ('status', 'priority', 'board')
    search_fields = ('title', 'description')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'task', 'author', 'created_at')
    search_fields = ('text', 'author__fullname')