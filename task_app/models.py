from django.db import models
from auth_app.models import User
from boards_app.models import Board


class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    board = models.ForeignKey(Board, related_name="tasks", on_delete=models.CASCADE)
    assignee = models.ForeignKey(User, null=True, blank=True, related_name="assigned_tasks", on_delete=models.SET_NULL)
    reviewer = models.ForeignKey(User, null=True, blank=True, related_name="reviewed_tasks", on_delete=models.SET_NULL)
    done = models.BooleanField(default=False)
    due_date = models.DateField(null=True, blank=True)
    priority = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=50, blank=True)

class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)