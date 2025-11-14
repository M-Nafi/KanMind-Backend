from django.urls import path
from .views import RegisterView, EmailAuthTokenView

urlpatterns = [
    path('registration/', RegisterView.as_view(), name='registration'),
    path('login/', EmailAuthTokenView.as_view(), name='login'),
]