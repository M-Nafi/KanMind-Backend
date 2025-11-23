from rest_framework import generics, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from auth_app.models import User
from .serializers import RegisterSerializer
from rest_framework.views import APIView
from rest_framework import viewsets
from task_app.api.serializers import MemberSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user = User.objects.get(id=response.data['id'])
        token, _ = Token.objects.get_or_create(user=user)
        response.data['token'] = token.key
        return Response(response.data, status=201)

class EmailAuthTokenView(ObtainAuthToken):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'email and password are required'}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Invalid email or password'}, status=400)

        if not user.check_password(password):
            return Response({'error': 'Invalid email or password'}, status=400)

        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token.key, 'fullname': user.fullname, 'email': user.email})
    
class EmailCheckView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        email = request.query_params.get('email')
        if not email:
            return Response({'error': 'Email parameter is required'}, status=400)

        try:
            user = User.objects.get(email=email)
            return Response({
                'email': email,
                'exists': True,
                'fullname': user.fullname
            })
        except User.DoesNotExist:
            return Response({'email': email, 'exists': False})
        

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = MemberSerializer