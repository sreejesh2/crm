from rest_framework.permissions import BasePermission
from .models import RolePermission, Module, Action

class HasModuleActionPermission(BasePermission):
    def has_permission(self, request, view):
        # Retrieve the module name and action value from the view
        module_name = getattr(view, 'module_name', None)
        action_value = getattr(view, 'action_value', None)

        if not module_name or not action_value:
            return False

        # Check if the user is a superuser
        if request.user.is_superuser:
            return True

        # Check if the user has the appropriate role and permission
        if request.user.role:
            role_permissions = RolePermission.objects.filter(
                role=request.user.role,
                module_action__module__name=module_name,
                module_action__action__value=action_value
            )
            return role_permissions.exists()

        return False

    def has_object_permission(self, request, view, obj):
        # Retrieve the module name and action value from the view
        module_name = getattr(view, 'module_name', None)
        action_value = getattr(view, 'action_value', None)

        if not module_name or not action_value:
            return False

        # Check if the user is a superuser
        if request.user.is_superuser:
            return True

        # Check if the user has the appropriate role and permission for the specific object
        if request.user.role:
            role_permissions = RolePermission.objects.filter(
                role=request.user.role,
                module_action__module__name=module_name,
                module_action__action__value=action_value
            )

            # Custom logic to determine if the user has permission to access the specific object
            # For example, you might want to check if the user owns the object or has some specific relationship with it
            if hasattr(obj, 'owner') and obj.owner == request.user:
                return True

            return role_permissions.exists()

        return False
