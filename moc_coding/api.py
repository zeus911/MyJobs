from tastypie.authentication import ApiKeyAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie.resources import ModelResource

from .models import CustomCareer


class CustomCareerResource(ModelResource):
    class Meta:
        resource_name = 'customcareer'
        queryset = CustomCareer.objects.all()
        authentication = ApiKeyAuthentication()
        authorization = DjangoAuthorization()
    
    
