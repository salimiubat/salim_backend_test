from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'OWNER')
        return self.create_user(email, username, password, **extra_fields)

class UserTypes(models.TextChoices):
    EMPLOYEE = "EMPLOYEE", "Employee"
    OWNER = "OWNER", "Owner"

class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, unique=True)
    role = models.CharField(max_length=20, choices=UserTypes.choices, default=UserTypes.EMPLOYEE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    def save(self, *args, **kwargs):
        if self.role == UserTypes.OWNER:
            self.is_staff = True
            self.is_superuser = True
        if self.role == UserTypes.EMPLOYEE:
            self.is_staff = False
            self.is_superuser = False
        else:
            self.is_staff = True
            self.is_superuser = True

        super().save(*args, **kwargs)