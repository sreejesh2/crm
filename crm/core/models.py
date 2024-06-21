import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
from django.utils import timezone



class Module(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    is_editable = models.BooleanField(default=True)
    is_deletable = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Action(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False)
    label = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.label

class ModuleAction(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    action = models.ForeignKey(Action, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.module.name} - {self.action.label}"

class Role(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False)
    label = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)
    is_editable = models.BooleanField(default=True)
    is_deletable = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    parent_role = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    permissions = models.ManyToManyField(ModuleAction, through='RolePermission')

    def __str__(self):
        return self.label

class RolePermission(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    module_action = models.ForeignKey(ModuleAction, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.role.label} - {self.module_action}"


    def __str__(self):
        return f"{self.role.label} - {self.module_action}"



class UserManager(BaseUserManager):
    def create_user(self, uid, email=None, password=None, **extra_fields):
        if not uid:
            raise ValueError('The UID field must be set')
        user = self.model(uid=uid, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, uid, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(uid, email, password, **extra_fields)


class User(AbstractBaseUser):
    full_name = models.CharField(max_length=60, blank=False, null=False)
    phone = models.CharField(max_length=15, blank=False, null=False)
    dob = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(max_length=200, null=True, blank=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    phone_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)  # Add this field
    is_deleted = models.BooleanField(default=False)
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, null=False, blank=False)
    fcm_token = models.CharField(max_length=1000, null=True, blank=True)
    country_code = models.CharField(max_length=10, default='+91', null=True, blank=True)
    current_token = models.CharField(max_length=255, null=True, blank=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)

    USERNAME_FIELD = 'uid'
    REQUIRED_FIELDS = ['full_name', 'phone']

    objects = UserManager()

    def __str__(self):
        return f"{self.phone} - {self.full_name}"

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser