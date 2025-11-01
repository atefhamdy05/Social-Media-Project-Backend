from rest_framework import serializers
from .models import Role
import re
from datetime import datetime, timezone
from project.regex_repo import common_en_name_regex
from django.utils.translation import gettext as _

class role_form(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields=[
            'name'
        ]
    @property
    def is_update(self):
        return self.instance is not None
    
    def validate_name(self, value):
        if not self.is_update and Role.objects.filter(name=value).exists():
            raise serializers.ValidationError(_('This role already exists'))
        
        if not re.fullmatch(common_en_name_regex['pattern'], value):
            raise serializers.ValidationError(common_en_name_regex['message'])
        return value
    
    def save(self, **kwargs):
        if self.is_update:
            self.instance.last_update_at = datetime.now(tz=timezone.utc)
            self.instance.updated_by = kwargs['created_by']
        return super().save(**kwargs)