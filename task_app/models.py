from django.db import models
from auth_app.models import User
from boards_app.models import Board


class Task(models.Model):
    STATUS_CHOICES = [
        ('to-do', 'To Do'),
        ('in-progress', 'In Progress'),
        ('review', 'Review'),
        ('done', 'Done'),
    ]
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    board = models.ForeignKey(Board, related_name="tasks", on_delete=models.CASCADE)
    assignee = models.ForeignKey(
        User, 
        null=True, 
        blank=True, 
        related_name="assigned_tasks", 
        on_delete=models.SET_NULL
    )
    reviewer = models.ForeignKey(
        User, 
        null=True, 
        blank=True, 
        related_name="reviewed_tasks", 
        on_delete=models.SET_NULL
    )
    done = models.BooleanField(default=False)
    due_date = models.DateField(null=True, blank=True)
    priority = models.CharField(
        max_length=50, 
        choices=PRIORITY_CHOICES,
        blank=True
    )
    status = models.CharField(
        max_length=50, 
        choices=STATUS_CHOICES,
        default='to-do'
    )
    created_by = models.ForeignKey(
        User,
        related_name="created_tasks",
        on_delete=models.CASCADE,
        null=True
    )

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        ordering = ['-id']

    def __str__(self):
        return self.title


class Comment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author} on {self.task}"