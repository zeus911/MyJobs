import sys
import urllib2
import os
import time
import logging
from django.conf import settings
import hotshot
import json
from functools import wraps

from django.contrib.auth import login
from django.http import HttpResponse
from django.shortcuts import redirect, render_to_response
from django.template import RequestContext
from django.views.decorators.cache import cache_page

from seo.cache import cache_page_prefix, get_site_config
from myjobs.models import Ticket, User


def home_page_check(view_func):
    @wraps(view_func)
    def decorator(request, *args, **kwargs):
        config = get_site_config(request)
        if config.home_page_template == 'home_page/home_page_dns_settings.html':
            data_dict = {
                'item_type': 'home',
                'facet_blurb': False,
                'site_name': settings.SITE_NAME,
                'site_title': settings.SITE_TITLE,
                'site_heading': settings.SITE_HEADING,
                'site_tags': settings.SITE_TAGS,
                'site_description': settings.SITE_DESCRIPTION,
                'host': str(request.META.get("HTTP_HOST", "localhost")),
                'site_config': config,
                'build_num': settings.BUILD,
                'filters': {},
                'view_source': settings.VIEW_SOURCE
            }

            return render_to_response(config.home_page_template, data_dict,
                                      context_instance=RequestContext(request))

        return view_func(request, *args, **kwargs)
    return decorator


def protected_site(view_func):
    @wraps(view_func)
    def decorator(request, *args, **kwargs):
        if settings.SITE_ID in settings.PROTECTED_SITES:
            if request.REQUEST.get('key') == settings.SEARCH_API_KEY:
                    return view_func(request, *args, **kwargs)
            groups = settings.PROTECTED_SITES[settings.SITE_ID]
            if request.user.is_authenticated():
                if list(set(groups) &
                        set(request.user.groups.values_list('id', flat=True))):
                    return view_func(request, *args, **kwargs)
                else:
                    # If the user is logged in but not in the group,
                    # they're never going to be able to access the site.
                    return redirect('http://www.my.jobs/')
            else:
                # If the user isn't authenticated, the first step is to try
                # to see if they were just authenticated by myjobs.
                ticket = request.GET.get('ticket', None)
                guid = request.GET.get('uid', None)
                if ticket and guid:
                    # If there's a ticket and guid, that means that myjobs
                    # should've just authenticated them.
                    try:
                        the_ticket = Ticket.objects.get(user__user_guid=guid,
                                                        ticket=ticket)
                    except Ticket.DoesNotExist:
                        # If this failed, there's probably some url hacking
                        # going on.
                        url = 'https://secure.my.jobs/?next=%s' % \
                              request.build_absolute_uri()
                        return redirect(url)

                    user = User.objects.get(user_guid=guid)
                    # Fake the authentication backed for the login, since
                    # we're assuming that myjobs authenticated the user if
                    # they've gotten this far.
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    login(request, user)

                    # Make the ticket one time use.
                    the_ticket.delete()

                    if list(set(groups) &
                            set(request.user.groups.values_list('id',
                                                                flat=True))):
                        return view_func(request, *args, **kwargs)
                    else:
                        return redirect('http://www.my.jobs/')

                else:
                    # If there isn't a ticket + guid, redirect to the myjobs
                    # CAS view to create one.
                    url = 'https://secure.my.jobs/cas/?redirect_url=%s' % \
                          request.build_absolute_uri()
                    return redirect(url)
        else:
            return view_func(request, *args, **kwargs)
    return decorator



def custom_cache_page(view):
    """ Wrap cache_page to pass custom key_prefix.

    This is a decorator used to dynamically generate a custom cache key prefix
    for cached pages. The key prefix varies on these custom factors:
        -  hostname of site so that different sites don't get served each
           other's cached pages in our multisite setup.
        -  configuration id so that changes to a site's configuration generate a
           new cache key prefix so that changes to the site's display options
           are detected in realtime

    """
    @wraps(view)
    def decorator(request, *args, **kwargs):
        # Build the custom cache key prefix
        timeout = 60 * settings.MINUTES_TO_CACHE
        key_prefix = cache_page_prefix(request)
        # Return cache_page function normally called by @cache_page decorator
        # with our custom cache key prefix.
        return cache_page(timeout, key_prefix=key_prefix)(view)(request, *args,
                                                                **kwargs)
    return decorator


def sns_json_message(f): 
    
    def wrap(request, *args, **kwargs):      
        # check the request to see if we need to confirm subscription
        json_message = None
        res = request.body
        try:
            json_message = json.JSONDecoder().decode(res)
            if json_message["Type"] == "SubscriptionConfirmation":
                subscribeURL = json_message["SubscribeURL"]
                res = urllib2.urlopen(subscribeURL)
        except KeyError:
            # We 'pass' here because the Type attribute might not be
            # in the JSON object if we've already subscribed to the 
            # end point.
            pass
        except Exception as e:
            logging.error("%s" % e, 
                          exc_info=sys.exc_info(), 
                          extra={'request': request,
                                 'view': 'sns_json_message decorator'})
            return HttpResponse(status=500)
        finally:
            f(json_message, *args, **kwargs)
            return HttpResponse(status=200)
    
    return wrap

try:
    PROFILE_LOG_BASE = settings.PROFILE_LOG_BASE
except:
    PROFILE_LOG_BASE = "/tmp"


def profile(log_file):
    """ Profile some callable.

    This decorator uses the hotshot profiler to profile some callable (like
    a view function or method) and dumps the profile data somewhere sensible
    for later processing and examination.

    It takes one argument, the profile log name. If it's a relative path, it
    places it under the PROFILE_LOG_BASE. It also inserts a time stamp into the 
    file name, such that 'my_view.prof' become 'my_view-20100211T170321.prof', 
    where the time stamp is in UTC. This makes it easy to run and compare 
    multiple trials.
    
    """
    if not os.path.isabs(log_file):
        log_file = os.path.join(PROFILE_LOG_BASE, log_file)

    def _outer(f):
        def _inner(*args, **kwargs):
            # Add a timestamp to the profile output when the callable
            # is actually called.
            (base, ext) = os.path.splitext(log_file)
            base = base + "-" + time.strftime("%Y%m%dT%H%M%S", time.gmtime())
            final_log_file = base + ext

            prof = hotshot.Profile(final_log_file)
            try:
                ret = prof.runcall(f, *args, **kwargs)
            finally:
                prof.close()
            return ret

        return _inner
    return _outer
