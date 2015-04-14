import json
import urllib2

from django.http import HttpResponse, HttpResponseForbidden

from api.models import APIUser


def sns_json_message(f):

    def wrap(request, *args, **kwargs):
        # check the request to see if we need to confirm subscription
        json_message = None
        res = request.body
        try:
            json_message = json.JSONDecoder().decode(res)
            if json_message["Type"] == "SubscriptionConfirmation":
                subscribe_url = json_message["SubscribeURL"]
                urllib2.urlopen(subscribe_url)
        except KeyError:
            # We 'pass' here because the Type attribute might not be
            # in the JSON object if we've already subscribed to the
            # end point.
            pass
        except Exception as e:
            print e
            return HttpResponse(status=500)
        finally:
            f(json_message, *args, **kwargs)
            return HttpResponse(status=200)

    return wrap


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