"""
Models module for the users app.
"""
import uuid

from django.db import models
from django.core.validators import validate_email
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)


class UserManager(BaseUserManager):
    """
    Manager for users.
    """
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save new user with employee role (default user).
        """
        if not email:
            raise ValueError('User must have an email address')

        email = self.normalize_email(email)
        validate_email(email)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)

        user.save(using=self._db)

        return user

    def create_admin(self, email, password, **extra_fields):
        """
        Create and save new user with admin role.
        """
        extra_fields['is_staff'] = True

        admin = self.create_user(email, password, **extra_fields)
        return admin

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save new user with superuser role.
        """
        extra_fields['is_staff'] = True
        extra_fields['is_superuser'] = True

        superuser = self.create_user(email, password, **extra_fields)
        return superuser


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model using email.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    @property
    def role(self):
        """
        Retrieve user's role
        """
        return 'Admin' if self.is_staff else 'Employee'

    def __str__(self):
        return f"{self.name}, {self.email}"
