"""
Accounts app models.
"""
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from .managers import MyUserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name="email address",
        max_length=155,
        unique=True,
        db_index=True,
    )
    name = models.CharField(max_length=300)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name",]

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email

