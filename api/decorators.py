from django.http import HttpResponseForbidden

from api.models import APIUser


def authorize_user(function):
    def wrap(request, *args, **kwargs):
        request_key = request.GET.get('key')
        try:
            api_user = APIUser.objects.get(key=request_key, disable=False)
        except APIUser.DoesNotExist:
            return HttpResponseForbidden()
        else:
            return function(request, api_user, *args, **kwargs)
    return wrap