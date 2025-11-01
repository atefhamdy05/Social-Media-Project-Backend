from django.core.management.base import BaseCommand
from roles.models import Permission, Role, Role_Permission, Module
from accounts.models import User
permissions_list = [
    {'module':'Users', 'key':'permissions.users.view', 'label':'View Users'},
    {'module':'Users', 'key':'permissions.users.add', 'label':'Add User'},
    {'module':'Users', 'key':'permissions.users.edit', 'label':'Edit User'},
    {'module':'Users', 'key':'permissions.users.delete', 'label':'Delete User'},

    {'module':'Roles', 'key':'permissions.roles.view', 'label':'View Roles'},
    {'module':'Roles', 'key':'permissions.roles.add', 'label':'Add Role'},
    {'module':'Roles', 'key':'permissions.roles.edit', 'label':'Edit Role'},
    {'module':'Roles', 'key':'permissions.roles.delete', 'label':'Delete Role'},
    {'module':'Roles', 'key':'permissions.roles.edit.permissions', 'label':'Edit Role Permissions'},
    
    
    {'module':'Customers', 'key':'permissions.customers.view', 'label':'View Customers'},
    {'module':'Customers', 'key':'permissions.customers.add', 'label':'Add Customer'},
    {'module':'Customers', 'key':'permissions.customers.edit', 'label':'Edit Customer'},
    {'module':'Customers', 'key':'permissions.customers.delete', 'label':'Delete Customer'},
    
    
    

    
]

notificaions_channels = [
    {'name': 'sms'},
    {'name': 'whatsapp'},
    {'name': 'email'},
]

class Command(BaseCommand):
    help = "seed database for testing and development."


    def handle(self, *args, **options):
        try:
            run_seed(self)
        except Exception as e:
            print('an error occurred', e)


def run_seed(self):

    ########################################
    print('_'*100, "\n\n", "-"*20, 'seeding Roles and each one permissions',"-"*20)
    
    seed_roles()
    
    #########################################
    print("\n", "-"*35, 'finished',"-"*35, '\n', '_'*100)
    print("\n"*5)
    print('_'*100, "\n\n", "-"*20, 'seeding Notificaions Channels',"-"*20)




    
    #########################################
    print("\n", "-"*35, 'finished',"-"*35, '\n', '_'*100)



    
        
def seed_roles():
    role, _ = Role.objects.get_or_create(name='Admin')

    user    = User.objects.filter(username='admin').first()
    if not user:
        
        user = User.objects.create(
            username        =   'admin',
            full_name       =   'admin',
            role            =   role,
            is_staff        =   True,
            is_superuser    =   True
        )

        user.set_password('123')
        user.save()
    else:
        user.set_password('123')
        user.save()

    if not Role_Permission.objects.filter(role=role).exists():
        for per in permissions_list:
            module, _       = Module.objects.get_or_create(name=per['module'])

            permission, _   = Permission.objects.get_or_create(key=per['key'], label=per['label'], module=module)
            
            

            Role_Permission.objects.get_or_create(role=role, permission=permission)


