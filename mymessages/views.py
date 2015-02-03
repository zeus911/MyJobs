import json

from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404, HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.template.loader import render_to_string

from myjobs.decorators import user_is_allowed
from myjobs.models import User
from mymessages.models import MessageInfo


@user_is_allowed()
@user_passes_test(User.objects.not_disabled)
def read(request):
    if request.is_ajax():
        message, user = request.GET.get('name').split('-')[2:]
        try:
            m = MessageInfo.objects.get(user=user, message__id=message)
        except MessageInfo.DoesNotExist:
            pass
        else:
            m.mark_read()
        return HttpResponse('')
    raise Http404


def get_message_page(request):
    message_list = request.user.messages(only_new=False)
    paginator = Paginator(message_list, 10)
    page = request.GET.get('page')
    try:
        messages = paginator.page(page)
    except PageNotAnInteger:
        messages = paginator.page(1)
    except EmptyPage:
        messages = paginator.page(paginator.num_pages)
    return messages


@user_is_allowed()
@user_passes_test(User.objects.not_disabled)
def delete(request):
    if request.is_ajax():
        message_id, user = request.GET.get('name').split('-')[2:]
        try:
            info = MessageInfo.objects.get(user=user, message__id=message_id)
        except MessageInfo.DoesNotExist:
            pass
        else:
            if info.message.messageinfo_set.count() > 1:
                info.delete()
            else:
                info.message.delete()
        messages = get_message_page(request)
        response = render_to_string('mymessages/includes/messages.html',
                                    {'messages': messages},
                                     RequestContext(request))
        return HttpResponse(json.dumps(response))
    raise Http404


@user_is_allowed()
@user_passes_test(User.objects.not_disabled)
def inbox(request):
    messages = get_message_page(request)
    return render_to_response('mymessages/inbox.html', {'messages': messages},
                              RequestContext(request))
