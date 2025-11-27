from django.contrib import admin
from auth_app.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'fullname', 'email', 'is_staff', 'is_superuser')
    search_fields = ('fullname', 'email')