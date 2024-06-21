from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Module, Action, Role, RolePermission,User
from .serializers import ModuleSerializer, ActionSerializer, RoleSerializer, RolePermissionSerializer
from rest_framework_simplejwt.tokens import AccessToken
from .serializers import UserSerializer,CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from .permissions import HasModuleActionPermission

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({"detail": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email, is_deleted=False)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_401_UNAUTHORIZED)

        user = authenticate(request, username=user.uid, password=password)

        if user is None:
            return Response({"detail": "Invalid email or password."}, status=status.HTTP_401_UNAUTHORIZED)

        # Create a mutable copy of request.data
        mutable_data = request.data.copy()
        mutable_data['uid'] = str(user.uid) if hasattr(user, 'uid') else None

        serializer = self.get_serializer(data=mutable_data)
        serializer.is_valid(raise_exception=True)
        tokens = serializer.validated_data

        response_data = {
            'refresh': tokens['refresh'],
            'access': tokens['access'],
            'user': {
                'id': user.id,
                'email': user.email,
                'uid': str(user.uid) if hasattr(user, 'uid') else None,
            }
        }

        return Response(response_data, status=status.HTTP_200_OK)
    

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            token = AccessToken(request.data['access'])
            token.blacklist()
            user = request.user
            user.current_token = None
            user.save()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)    
        

class ModuleListAPIView(APIView):
    permission_classes = [IsAuthenticated, HasModuleActionPermission]
    module_name = 'module'  
    action_value = 'LIST'

    def get(self, request):
        try:
            modules = Module.objects.all()
            serializer = ModuleSerializer(modules, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

