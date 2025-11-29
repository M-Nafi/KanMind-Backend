from django.urls import path
from .views import RegisterView, EmailAuthTokenView, EmailCheckView


urlpatterns = [
    path('registration/', RegisterView.as_view(), name='registration'),
    path('login/', EmailAuthTokenView.as_view(), name='login'),
    path('email-check/', EmailCheckView.as_view(), name='email-check'),
]
