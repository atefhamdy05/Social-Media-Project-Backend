from django.db import models
import uuid
from django.conf import settings
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin
)
from roles.models import Role

class UserAccountManager(BaseUserManager):
    def create_user(self, username, **kwargs):
        if not username:
            raise ValueError('Users must have a username')

        username = username.lower()

        user = self.model(
            username=username,
            **kwargs
        )
        # user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username, password=None, **kwargs):
        user = self.create_user(
            username,
            password=password,
            **kwargs
        )
        role = Role.objects.filter(name='Admin').first()
        if not role:
            role = Role.objects.create(name='Admin')
            role.save()
        user.role  = role
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user

# class Role(models.Model):
#     name                = models.CharField(max_length=255)
#     

#     def __str__(self) -> str:
#         return self.name



class User(AbstractBaseUser, PermissionsMixin):
    id                  = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username            = models.CharField(unique=True, max_length=255)
    full_name           = models.CharField(max_length=255)
    email               = models.EmailField(max_length=254)
    role                = models.ForeignKey(Role, null=True, related_name='users', blank=True, on_delete=models.SET_NULL)

    is_active           = models.BooleanField(default=True)
    is_staff            = models.BooleanField(default=False)
    is_superuser        = models.BooleanField(default=False)

    


    created_at          = models.DateTimeField(auto_now=False, auto_now_add=True)
    last_update_at      = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    last_delete_at      = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)

    
    created_by          = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name='user_created_by', on_delete=models.SET_NULL)
    updated_by          = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='user_updated_by', on_delete=models.SET_NULL)
    deleted_by          = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name='user_deleted_by', on_delete=models.SET_NULL)
    
    objects = UserAccountManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['full_name', 'email']

    def __str__(self):
        return self.username
    

    def save(self, *args, **kwargs):
        # Save the provided password in hashed format
        user = super(User, self)
        if not (user.is_superuser):
            user.set_password(self.password)

        # Ensure the default role exists
        role, _     = Role.objects.get_or_create(name='User')

        # Assign role if not already set
        if not self.role:
            self.role = role

        super(User, self).save(*args, **kwargs)
        return user
    


