from rest_framework import generics, permissions, viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from auth_app.models import User
from .serializers import RegisterSerializer, MemberSerializer
from .permissions import IsSelfOrBoardMember


class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration.

    - Accepts user data via RegisterSerializer.
    - Creates a new User instance with hashed password.
    - Automatically generates and returns an authentication token.
    - Response includes: token, user_id, and the created user data.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        user = User.objects.get(id=response.data['id'])
        token, _ = Token.objects.get_or_create(user=user)
        response.data['token'] = token.key
        response.data['user_id'] = user.id
        return Response(response.data, status=201)


class EmailAuthTokenView(ObtainAuthToken):
    """
    API endpoint for authentication using email and password.

    - Validates that both email and password are provided.
    - Checks if the user exists and the password is correct.
    - Returns an authentication token along with basic user info:
      fullname, email, and user_id.
    - Returns error responses for invalid credentials or missing fields.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response(
                {'error': 'email and password are required'}, 
                status=400
            )
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'error': 'Invalid email or password'}, 
                status=400
            )
        
        if not user.check_password(password):
            return Response(
                {'error': 'Invalid email or password'}, 
                status=400
            )

        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'fullname': user.fullname,
            'email': user.email,
            'user_id': user.id
        })


class EmailCheckView(APIView):
    """
    API endpoint to check if a user with a given email exists.

    - Requires authentication.
    - Accepts 'email' as a query parameter.
    - If the user exists, returns id, email, and fullname.
    - If not found, returns a 404 error.
    - If no email parameter is provided, returns a 400 error.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        email = request.query_params.get('email')
        if not email:
            return Response(
                {'error': 'Email parameter is required'}, 
                status=400
            )
        try:
            user = User.objects.get(email=email)
            return Response({
                'id': user.id,
                'email': user.email,
                'fullname': user.fullname
            }, status=200)
        except User.DoesNotExist:
            return Response(
                {'error': 'Email not found'},
                status=404
            )