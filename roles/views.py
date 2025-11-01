from rest_framework.response import Response
from rest_framework import status

from accounts.permissions import permission_allowed
from project.helper import paginate_query_set_list
from rest_framework.decorators import api_view
from .models import Role, Role_Permission, Module, Permission
from .serializer import RolesListSerializer, IncludedRoleSerial
from .forms import role_form
from django.utils.translation import gettext as _

@api_view(['GET',])
@permission_allowed('permissions.roles.view')
def list_roles(request):
    roles               = Role.objects.order_by('name').all() #.values('name', 'id', 'created_at', 'created_by')

    roles               = paginate_query_set_list(query_set=roles, params=request.GET,serializer=RolesListSerializer)


    return Response(
        roles,  
        status=status.HTTP_200_OK
    )
    
@api_view(['POST',])
@permission_allowed('permissions.roles.add')
def add_role(request):
    form            = role_form(data = request.POST)
    if form.is_valid():
        form.save(created_by=request.user)

        return Response({
                'message': _('Role added successfully')
            },
            status=status.HTTP_201_CREATED
        )
    return Response({
            'errors': form.errors
        },
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['PUT',])
@permission_allowed('permissions.roles.edit')
def edit_role(request, id):
    role                = Role.objects.filter(id=id).first()
    old_name            = role.name
    if not role:
        return Response(
            {
                'error': _("this role doesn't exist or may be deleted")
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    form            = role_form(data=request.POST, instance=role)
    if form.is_valid():
        form.save(created_by=request.user)

        return Response({
                'message':_('Role has benn changed successfully')
            },
            status=status.HTTP_201_CREATED
        )
    return Response({
            'errors': form.errors
        },
        status=status.HTTP_400_BAD_REQUEST
    )

@api_view(['GET',])
@permission_allowed('permissions.roles.view')
def role_details(request, id):
    role                = Role.objects.filter(id=id).first()
    if not role:
        return Response(
            {
                'error': _("this role doesn't exist or may be deleted")
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    list_permissions    = dict()
    modules             = Module.objects.filter(is_editable=True)
    role_permission     = Role_Permission.objects.filter(role=role)

    for module in modules:    
        list_permissions[module.name] = []
        for permission in  module.permissions.values('id', 'key', 'label'):
            perm_dict = dict(permission)
            if role_permission.filter(permission__id=permission['id']).exists():
                perm_dict['has_perm'] = True
            else:
                perm_dict['has_perm'] = False

            list_permissions[module.name].append(perm_dict)
        

    


    return Response(
        {
            'role'              : IncludedRoleSerial(role).data,
            'permissions'       : list_permissions,
        }, 
        status=status.HTTP_200_OK
    )

@api_view(['PUT',])
@permission_allowed('permissions.roles.edit.permissions')
def add_permission_to_role(request, id):
    permission_id       = request.data.get('permission_id', None)

    if not permission_id:
        return Response(
            {
                'error': _("invalid permission")
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    role                = Role.objects.filter(id=id).first()
    permission          = Permission.objects.filter(id=permission_id).first()


    
    if not role or not permission:
        return Response(
            {
                'error': _("wrong permission or role")
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    role_permission     = Role_Permission.objects.filter(role=role, permission=permission).first()

    if role_permission:
        role_permission.delete()
        return Response(
                status=status.HTTP_200_OK
            )
    else:
        role_permission     = Role_Permission.objects.create(role=role, permission=permission)
        role_permission.save()
        return Response({
                    'message':_('The Permission has added to  the role')
                },
                status=status.HTTP_201_CREATED
            )


@api_view(['GET',])
@permission_allowed('permissions.roles.edit')
def role_form_data(request, id):
    role                = Role.objects.filter(id=id).first()
    if not role:
        return Response(
            {
                'error': _("this role doesn't exist or may be deleted")
            },
            status=status.HTTP_400_BAD_REQUEST
        )
            
    return Response(
        {
            'role'              : IncludedRoleSerial(role).data,
        }, 
        status=status.HTTP_200_OK
    )
    

@api_view(['GET',])
@permission_allowed('permissions.roles.view')
def get_roles_as_selectlist(request):
    exclude = request.GET.get('exclude', None)
    if not exclude:
        return Response(
            {
                "roles":list(Role.objects.values('id', 'name')) 
            },
            status=status.HTTP_200_OK
        )
    return Response(
        {
            "roles":list(Role.objects.exclude(id=exclude).values('id', 'name')) 
        },
        status=status.HTTP_200_OK
    )

@api_view(['DELETE',])
@permission_allowed('permissions.roles.delete')
def delete_role(request, id):
    role        = Role.objects.filter(id=id).first()

    if 'alter_role' in request.data:
        alter_role  = request.data['alter_role']
    
    if not role:
        return Response(
            {
                'error': _("this role doesn't exist or may be deleted")
            },
            status=status.HTTP_404_NOT_FOUND
        )
    if not alter_role:
        return Response(
            {
                'error': _("you should choose alter role to move the current role users to")
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    alter_role  = Role.objects.filter(id=alter_role).first()
    if not role:
        return Response(
            {
                'error': _("the alter role doesn't exist or has been deleted")
            },
            status=status.HTTP_404_NOT_FOUND
        )
    if alter_role == role:
        return Response(
            {
                'error': _("the alter role and deleted role shouldn't be the same")
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if role.users:
        role.users.update(role=alter_role)

    role.delete()
    return Response(
            {
                'message': _("role has been deleted succssefully!")
            },
            status=status.HTTP_200_OK
        )


    