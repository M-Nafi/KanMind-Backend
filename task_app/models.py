from django.db import models
from auth_app.models import User
from boards_app.models import Board

class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    done = models.BooleanField(default=False)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="tasks")
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tasks", null=True, blank=True)

    def __str__(self):
        return self.title