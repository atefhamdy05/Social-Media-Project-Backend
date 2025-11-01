from django.db import models
from project.models import BaseModel, BaseModelManager


# Create your models here.
class  Role(BaseModel):
    name                = models.CharField(max_length=50)
    objects = BaseModelManager()
    
    def __str__(self):
        return self.name



    
class Module(BaseModel):
    name        = models.CharField(max_length=255, unique=True)
    is_editable = models.BooleanField(default=True)
    def __str__(self):
        return self.name
    
class Permission(BaseModel):
    key                 = models.CharField(max_length=50, unique=True)
    label               = models.CharField(max_length=50)
    module              = models.ForeignKey(Module, related_name='permissions', null=True, blank=True, on_delete=models.SET_NULL)
    
    objects = BaseModelManager()
    class Meta:
        indexes = [
            models.Index(fields=['key']),
        ]
    
    def __str__(self):
        return self.label

class Role_Permission(BaseModel):
    role                = models.ForeignKey(Role, null=True, related_name='role_permission_role', on_delete=models.CASCADE)
    permission          = models.ForeignKey(Permission, related_name='role_permission_permission', null=True, on_delete=models.CASCADE)
    

    objects = BaseModelManager()

    class Meta:
        unique_together = ('role', 'permission','is_deleted')

    def __str__(self):
        return str(self.role) + " can " + str(self.permission)


