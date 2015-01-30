from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from myjobs.decorators import user_is_allowed
from myjobs.models import User
from mymessages.models import MessageInfo


@user_is_allowed()
@user_passes_test(User.objects.not_disabled)
def read(request):
    if request.is_ajax():
        message, user = request.GET.get('name').split('-')[2:]
        m = MessageInfo.objects.get(user=user, message__id=message)
        m.mark_read()
        return HttpResponse('')
    raise Http404


@user_is_allowed()
@user_passes_test(User.objects.not_disabled)
def inbox(request):
    message_list = request.user.messages(only_new=False)
    paginator = Paginator(message_list, 10)
    page = request.GET.get('page')
    try:
        messages = paginator.page(page)
    except PageNotAnInteger:
        messages = paginator.page(1)
    except EmptyPage:
        messages = paginator.page(paginator.num_pages)
    return render_to_response('mymessages/inbox.html', {'messages': messages},
                              RequestContext(request))
