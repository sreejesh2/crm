from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Module, Action, Role, RolePermission,User,AuditLogs
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
            return Response({"status":0,"message": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email, is_deleted=False)
        except User.DoesNotExist:
            return Response({"status":0,"message":"User not found"}, status=status.HTTP_401_UNAUTHORIZED)

        user = authenticate(request, username=user.uid, password=password)

        if user is None:
            return Response({"status":0,"message":"Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)

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

        return Response({"status":1,"data":response_data }, status=status.HTTP_200_OK)
    

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
            return Response({"status":1,"data":serializer.data})
        except Exception as e:
            return Response({"status":1,'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ModuleCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, HasModuleActionPermission]
    module_name = 'module'
    action_value = 'CREATE'

    def post(self, request):
        serializer = ModuleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            AuditLogs.objects.create(resource='module',action='CREATE',user= request.user.full_name,body=serializer.data)
            return Response({"status": 1, "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"status": 0, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ModuleUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, HasModuleActionPermission]
    module_name = 'module'
    action_value = 'UPDATE'

    def put(self, request, pk):
        try:
            module = Module.objects.get(pk=pk)
        except Module.DoesNotExist:
            return Response({"status": 0, "message": "Module not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ModuleSerializer(module, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            AuditLogs.objects.create(resource='module',action='UPDATE',user= request.user.full_name,body=serializer.data)
            return Response({"status": 1, "data": serializer.data}, status=status.HTTP_200_OK)
        return Response({"status": 0, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)    
    

class ModuleDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated, HasModuleActionPermission]

    def delete(self, request, pk):
        try:
            module = Module.objects.get(pk=pk)
        except Module.DoesNotExist:
            return Response({"status": 0, "message": "Module not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ModuleSerializer(module)
        serialized_data = serializer.data
        module.delete()

        AuditLogs.objects.create(resource='module',action='DELETE',user= request.user.full_name,body=serialized_data)
        return Response({"status": 1, "message": "Module deleted successfully"}, status=status.HTTP_202_ACCEPTED)
    
