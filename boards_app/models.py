from django.db import models
from auth_app.models import User


class Board(models.Model):
    """
    Model representing a project board.

    - title: The name of the board.
    - owner: A foreign key to the User who owns the board.
      * If the owner is deleted, all owned boards are also deleted (CASCADE).
    - members: A many-to-many relationship to Users who are members of the board.
      * Can be empty (blank=True).
    - __str__: Returns the board's title as its string representation.
    """
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
