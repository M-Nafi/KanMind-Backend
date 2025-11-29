from django.db import models
from auth_app.models import User
from boards_app.models import Board


class Task(models.Model):
    """
    Model representing a task within a board.

    Fields:
    - title: Short title of the task.
    - description: Optional detailed description.
    - board: Foreign key to the Board the task belongs to.
    - assignee: User assigned to work on the task (nullable).
    - reviewer: User assigned to review the task (nullable).
    - done: Boolean flag indicating completion status.
    - due_date: Optional deadline for the task.
    - priority: Priority level (low, medium, high).
    - status: Workflow status (to-do, in-progress, review, done).
    - created_by: User who created the task.

    Meta:
    - verbose_name: "Task"
    - verbose_name_plural: "Tasks"
    - ordering: newest tasks first (descending id).

    __str__:
    - Returns the task title.
    """
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
    board = models.ForeignKey(
        Board,
        related_name="tasks",
        on_delete=models.CASCADE)
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
    """
    Model representing a comment on a task.

    Fields:
    - task: Foreign key to the related Task.
    - author: User who wrote the comment.
    - text: Content of the comment.
    - created_at: Timestamp when the comment was created.

    Meta:
    - verbose_name: "Comment"
    - verbose_name_plural: "Comments"
    - ordering: oldest comments first (ascending created_at).

    __str__:
    - Returns a string in the format: "Comment by <author> on <task>".
    """
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author} on {self.task}"
