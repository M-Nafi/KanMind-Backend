from django.db import models
from auth_app.models import User
from boards_app.models import Board

class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    done = models.BooleanField(default=False)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="tasks")
    assignee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks", null=True, blank=True)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviewed_tasks", null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    priority = models.CharField(max_length=20, default="low")
    status = models.CharField(max_length=20, default="open")

class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)