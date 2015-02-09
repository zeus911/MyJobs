import datetime
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
    """
    Retrieves the list of messages that should be displayed on the inbox,
    paginates it, and selects the proper page based on the presence of
    a "message" or "page" query string.
    """
    message_list = request.user.messages(only_new=False)
    items_per_page = 10
    paginator = Paginator(message_list, items_per_page)

    # User clicked on this message in their topbar.
    message_clicked = request.GET.get('message')
    page = None
    if message_clicked is not None:
        try:
            message_clicked = int(message_clicked)
        except ValueError:
            # This isn't an integer somehow; ignore it.
            message_clicked = None
        else:
            try:
                # Determine the clicked message's place in the full list
                # of messages.
                index = [message.message.pk
                         for message in message_list].index(message_clicked)
            except ValueError:
                # The message clicked has either been deleted, is not associated
                # with this user, or otherwise doesn't exist.
                message_clicked = None
            else:
                # index // items_per_page is the desired page; The paginator is
                # 1-indexed, so increment it.
                page = (index // items_per_page) + 1

    if page is None:
        # Only check for the page query string if all of the above failed
        # to produce a page number.
        page = request.GET.get('page')
    try:
        messages = paginator.page(page)
    except PageNotAnInteger:
        messages = paginator.page(1)
    except EmptyPage:
        messages = paginator.page(paginator.num_pages)
    return messages, message_clicked


@user_is_allowed()
@user_passes_test(User.objects.not_disabled)
def delete(request):
    if request.is_ajax():
        message_id, user = request.GET.get('name').split('-')[2:]
        MessageInfo.objects.filter(user=user, message__id=message_id).update(
            deleted_on=datetime.datetime.now())
        messages, _ = get_message_page(request)
        response = render_to_string('mymessages/includes/messages.html',
                                    {'messages': messages},
                                    RequestContext(request))
        return HttpResponse(json.dumps(response))
    raise Http404


@user_is_allowed()
@user_passes_test(User.objects.not_disabled)
def inbox(request):
    messages, clicked = get_message_page(request)
    return render_to_response('mymessages/inbox.html', {'messages': messages,
                                                        'clicked': clicked},
                              RequestContext(request))
