from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import User
from roles.models import Role, Role_Permission
from django.utils.translation import gettext as _

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['id']         = str(user.id)
        token['username']   = user.username
        token['full_name']  = user.full_name
        if user.role:
            token['role']   = user.role.name
        

        return token


class BaseUserSerial(serializers.ModelSerializer):
    class Meta:
        model= User
        fields=['id', 'username', 'full_name']

class UserSerial(serializers.ModelSerializer):
    role        = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    def get_role(self, obj):
        if obj.role:
            return obj.role.name
        return None

    def get_permissions(self, obj):
        if obj.role:
            return [i.permission.key for i in Role_Permission.objects.filter(role=obj.role)]
        return []
    
    class Meta:
        model= User
        fields=['id', 'username', 'full_name', 'role', 'permissions']



# class IncludedUserPermissionsSerial(serializers.ModelSerializer):
#     permission = serializers.SerializerMethodField()

#     def get_permission(self, obj):
#         return obj.permission.key
        
#     class Meta:
#         model= Role_Permission
#         fields=['permission']

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {
        "no_active_account": _("invalid username or password")
    }
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['id']             = str(user.id)
        token['username']       = str(user.username)
        token['full_name']      = str(user.full_name)
        token['role']           = str(user.role)
        token['permissions']    = [i.permission.key for i in Role_Permission.objects.filter(role=user.role)]


        return token


class IncludedUserSerial(serializers.ModelSerializer):
    class Meta:
        model= User
        fields=['id', 'username', 'full_name']

class IncludedRoleSerial(serializers.ModelSerializer):
    class Meta:
        model= Role
        fields=['id', 'name']



class ListUserSerial(serializers.ModelSerializer):
    # role        = serializers.ReadOnlyField(source='role.name')
    class Meta:
        model= User
        fields=['id', 'full_name', 'username', 'role']
    
    def to_representation(self, instance):
    
        representation = dict()
        
        representation['id']                        = instance.id
        representation[_('FullName')]               = instance.full_name
        representation[_('Username')]               = instance.username
        representation[_('Role')]                   = instance.role.name if instance.role else ''


        return representation
    







class DetailedUserSerial(serializers.ModelSerializer):
    # role        = serializers.ReadOnlyField(source='role')
    # role        = serializers.ReadOnlyField(source='role')
    class Meta:
        model= User
        fields=['id', 'full_name', 'username', 'role']




