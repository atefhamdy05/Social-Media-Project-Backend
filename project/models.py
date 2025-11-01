from django.db import models
from django.conf import settings
import uuid

class BaseModel(models.Model):
    id                  = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_deleted          = models.BooleanField(default=False)


    created_at          = models.DateTimeField(auto_now=False, auto_now_add=True)
    last_update_at      = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    last_delete_at      = models.DateTimeField(auto_now=False, auto_now_add=False, null=True, blank=True)
    


    created_by          = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name="%(class)s_created_by", on_delete=models.SET_NULL)
    updated_by          = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name="%(class)s_updated_by", on_delete=models.SET_NULL)
    deleted_by          = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, related_name="%(class)s_deleted_by", on_delete=models.SET_NULL)

    class Meta:
        abstract = True

    def soft_delete(self):
        self.is_deleted = True
        self.save()
    def restore(self):
        self.is_deleted = False
        self.save()

class BaseModelManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)
    
    def get_deleted(self):
        return super().get_queryset().filter(is_deleted=True)
    
    def get_all(self):
        return super().get_queryset().all()