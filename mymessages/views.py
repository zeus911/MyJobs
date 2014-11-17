from django.contrib.auth.decorators import user_passes_test
from django.http import Http404, HttpResponse

from myjobs.decorators import user_is_allowed
from myjobs.models import User
from mymessages.models import MessageInfo


@user_is_allowed()
@user_passes_test(User.objects.not_disabled)
def read(request):
    if request.is_ajax():
        message, user = request.GET.get('name').split('-')[1:]
        m = MessageInfo.objects.get(user=user, message__id=message)
        m.mark_read()
        return HttpResponse('')
    raise Http404
