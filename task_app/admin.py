from django.contrib import admin
from task_app.models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'board', 'done')
    list_filter = ('done', 'board')
    search_fields = ('title', 'description')