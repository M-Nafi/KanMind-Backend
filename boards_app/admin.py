from django.contrib import admin
from boards_app.models import Board

@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'owner')
    search_fields = ('title',)