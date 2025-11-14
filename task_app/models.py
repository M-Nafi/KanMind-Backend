from django.db import models
from boards_app.models import Board

class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='tasks')
    done = models.BooleanField(default=False)

    def __str__(self):
        return self.title
