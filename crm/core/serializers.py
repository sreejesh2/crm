# serializers.py

from rest_framework import serializers
from .models import Module, Action, ModuleAction, Role, RolePermission,User


from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import AccessToken

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = "__all__"

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
        )
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        # Add user data to the token
        data['user'] = {
            'id': self.user.id,
            'email': self.user.email,
        }

        # Blacklist old token if it exists
        if self.user.current_token:
            try:
                token = AccessToken(self.user.current_token)
                token.blacklist()
            except Exception as e:
                pass

        # Save the new token
        self.user.current_token = data['access']
        self.user.save()

        return data



class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        fields = '__all__'

class ModuleActionSerializer(serializers.ModelSerializer):
    action = ActionSerializer()  # Nested serializer for Action

    class Meta:
        model = ModuleAction
        fields = '__all__'


class ModuleSerializer(serializers.ModelSerializer):
    actions = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = '__all__'

    def get_actions(self, obj):
        module_actions = ModuleAction.objects.filter(module=obj)
        return ModuleActionSerializer(module_actions, many=True).data

class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        fields = '__all__'

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'

class RolePermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolePermission
        fields = '__all__'

