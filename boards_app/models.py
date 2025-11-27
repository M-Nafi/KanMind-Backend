from django.db import models
from auth_app.models import User


class Board(models.Model):
    title = models.CharField(max_length=255)
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="owned_boards"
    )
    members = models.ManyToManyField(
        User,
        related_name="member_boards",
        blank=True
    )

    def __str__(self):
        return self.title