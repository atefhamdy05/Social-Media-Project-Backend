from roles.models import Role_Permission
from rest_framework import response, status 
from django.utils.translation import gettext as _



def permission_allowed(name):
    
    def decorator(view_func):
        def wrapper_func(request,*args,**kwargs):
            if request.user and request.user.role and Role_Permission.objects.filter(role=request.user.role, permission__key=name).exists():
                    return view_func(request,*args,**kwargs)
            else:
                return response.Response({'error':_("you don't have permission to complete this request")}, status=status.HTTP_403_FORBIDDEN) 
        return wrapper_func
    return decorator 


def has_permission_or_none(role, permission):
    return Role_Permission.objects.filter(role=role, permission__key=permission).exists()