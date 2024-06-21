from django.contrib.auth.models import BaseUserManager
from django.utils import timezone

class UserManager(BaseUserManager):
    use_in_migrations = True
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError("The Phone number field must be set")

        now = timezone.now()
        user = self.model(phone=phone, last_login=now, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")

        return self.create_user(phone, password, **extra_fields)

      