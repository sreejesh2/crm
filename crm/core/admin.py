from django.contrib import admin
from . import models
from .models import RolePermission, Role, ModuleAction
from django.core.exceptions import ValidationError
# Register your models here.

admin.site.register(models.Action)
admin.site.register(models.ModuleAction)
admin.site.register(models.Role)
admin.site.register(models.Module)
admin.site.register(models.RolePermission)
admin.site.register(models.User)