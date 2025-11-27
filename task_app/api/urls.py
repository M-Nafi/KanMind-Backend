from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from task_app.api.views import TaskViewSet, CommentViewSet


router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')

tasks_router = NestedDefaultRouter(router, r'tasks', lookup='task')
tasks_router.register(r'comments', CommentViewSet, basename='task-comments')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(tasks_router.urls)),
]