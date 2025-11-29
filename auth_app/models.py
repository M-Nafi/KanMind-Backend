from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.

    - Adds an optional 'fullname' field for storing the user's full name.
    - Retains all default fields and authentication behavior from AbstractUser
      (username, email, password, etc.).
    - The string representation (__str__) returns:
        * fullname if available,
        * otherwise username,
        * otherwise email,
        * otherwise the literal string "User".
    """
    fullname = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.fullname or self.username or self.email or "User"
