from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, EmailAuthTokenView, EmailCheckView, UserViewSet


router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('registration/', RegisterView.as_view(), name='registration'),
    path('login/', EmailAuthTokenView.as_view(), name='login'),
    path('email-check/', EmailCheckView.as_view(), name='email-check'),
    path('', include(router.urls)),
]