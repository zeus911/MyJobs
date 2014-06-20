from datetime import date, timedelta, datetime
from itertools import chain, izip_longest
import logging
import os
import pysolr
import urlparse
import uuid

import boto
from celery import task

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.template.loader import render_to_string
from django.db.models import Q

from mydashboard.models import Company, SeoSite
from myjobs.models import EmailLog, User
from mysearches.models import SavedSearch, SavedSearchDigest
from postajob.models import Job
from registration.models import ActivationProfile
from solr import helpers
from solr.models import Update
from solr.signals import object_to_dict, profileunits_to_dict

logger = logging.getLogger(__name__)


@task(name='tasks.send_search_digest', ignore_result=True,
      default_retry_delay=180, max_retries=2)
def send_search_digest(search):
    """
    Task used by send_send_search_digests to send individual digest or search
    emails.

    Inputs:
    :search: SavedSearch or SavedSearchDigest instance to be mailed
    """
    try:
        search.send_email()
    except ValueError as e:
        if task.current.request.retries < 3:  # Try sending email three times
            raise send_search_digest.retry(arg=[search], exc=e)
        else:
            # After the initial try and two retries, disable the offending
            # saved search
            search.disable_or_fix()


@task(name='tasks.send_search_digests')
def send_search_digests():
    """
    Daily task to send saved searches. If user opted in for a digest, they
    receive it daily and do not get individual saved search emails. Otherwise,
    each active saved search is sent individually.
    """

    def filter_by_time(qs):
        """
        Filters the provided query set for emails that should be sent today

        Inputs:
        :qs: query set to be filtered

        Outputs:
        :qs: filtered query set containing today's outgoing emails
        """
        today = datetime.today()
        day_of_week = today.isoweekday()

        daily = qs.filter(frequency='D')
        weekly = qs.filter(frequency='W', day_of_week=str(day_of_week))
        monthly = qs.filter(frequency='M', day_of_month=today.day)
        return chain(daily, weekly, monthly)

    digests = SavedSearchDigest.objects.filter(is_active=True)
    digests = filter_by_time(digests)
    for obj in digests:
        try:
            send_search_digest.s(obj).apply_async()
        except send_search_digest.MaxRetriesExceededError:
            obj.disable()

    not_digest = SavedSearchDigest.objects.filter(is_active=False)
    for item in not_digest:
        saved_searches = item.user.savedsearch_set.filter(is_active=True)
        saved_searches = filter_by_time(saved_searches)
        for search_obj in saved_searches:
            send_search_digest.s(search_obj).apply_async()


@task(name='task.delete_inactive_activations')
def delete_inactive_activations():
    """
    Daily task checks if a activation keys are expired and deletes them.
    Disabled users are exempt from this check.
    """

    for profile in ActivationProfile.objects.all():
        try:
            if profile.activation_key_expired():
                user = profile.user
                if not user.is_disabled and not user.is_active:
                    user.delete()
                    profile.delete()
        except User.DoesNotExist:
            profile.delete()


@task(name='tasks.process_batch_events')
def process_batch_events():
    """
    Processes all events that have accumulated over the last day, sends emails
    to inactive users, and disables users who have been inactive for a long
    period of time.
    """
    now = date.today()
    EmailLog.objects.filter(received__lte=now-timedelta(days=60),
                            processed=True).delete()
    new_logs = EmailLog.objects.filter(processed=False)
    for log in new_logs:
        user = User.objects.get_email_owner(email=log.email)
        if not user:
            # This can happen if a user removes a secondary address or deletes
            # their account between interacting with an email and the batch
            # process being run
            # There is no course of action but to ignore that event
            continue
        if user.last_response < log.received:
            user.last_response = log.received
            user.save()
        log.processed = True
        log.save()
    # These users have not responded in a month. Send them an email if they
    # own any saved searches
    inactive = User.objects.select_related('savedsearch_set')
    inactive = inactive.filter(Q(last_response=now-timedelta(days=30)) |
                               Q(last_response=now-timedelta(days=36)))

    for user in inactive:
        if user.savedsearch_set.exists():
            time = (now - user.last_response).days
            message = render_to_string('myjobs/email_inactive.html',
                                       {'user': user,
                                        'time': time})
            user.email_user('Account Inactivity', message,
                            settings.DEFAULT_FROM_EMAIL)

    # These users have not responded in a month and a week. Stop sending emails.
    stop_sending = User.objects.filter(
        last_response__lte=now-timedelta(days=37))
    for user in stop_sending:
        user.opt_in_myjobs = False
        user.save()


@task(name="tasks.update_solr_from_model")
def update_solr_task(solr_location=None):
    """
    Deletes all items scheduled for deletion, and then adds all items
    scheduled to be added to solr.

    Inputs:
    :solr_location: Dict of separate cores to be updated
    """
    if hasattr(mail, 'outbox'):
        solr_location = settings.TEST_SOLR_INSTANCE
    elif solr_location is None:
        solr_location = settings.SOLR
    objs = Update.objects.filter(delete=True).values_list('uid', flat=True)

    if objs:
        objs = split_list(objs, 1000)
        for obj_list in objs:
            obj_list = filter(None, list(obj_list))
            uid_list = " OR ".join(obj_list)
            for location in solr_location.values():
                solr = pysolr.Solr(location)
                solr.delete(q="uid:(%s)" % uid_list)
        Update.objects.filter(delete=True).delete()

    objs = Update.objects.filter(delete=False)
    updates = []

    for obj in objs:
        content_type, key = obj.uid.split("##")
        model = ContentType.objects.get_for_id(content_type).model_class()
        if model == SavedSearch:
            updates.append(object_to_dict(model, model.objects.get(pk=key)))
        # If the user is being updated, because the user is stored on the
        # SavedSearch document, every SavedSearch belonging to that user
        # also has to be updated.
        elif model == User:
            searches = SavedSearch.objects.filter(user_id=key)
            [updates.append(object_to_dict(SavedSearch, s)) for s in searches]
            updates.append(object_to_dict(model, model.objects.get(pk=key)))
        else:
            updates.append(profileunits_to_dict(key))

    updates = split_list(updates, 1000)
    for location in solr_location.values():
        solr = pysolr.Solr(location)
        for update_subset in updates:
            update_subset = filter(None, list(update_subset))
            solr.add(list(update_subset))
    objs.delete()


def split_list(l, list_len, fill_val=None):
    """
    Splits a list into sublists.

    inputs:
    :l: The list to be split.
    :list_len: The length of the resulting lists.
    :fill_val: The value that is inserted when there are less items in the
        final list than list_len.

    outputs:
    A generator of tuples size list_len.

    """
    args = [iter(l)] * list_len
    return izip_longest(fillvalue=fill_val, *args)


@task(name="tasks.reindex_solr")
def task_reindex_solr(solr_location=None):
    """
    Adds all ProfileUnits, Users, and SavedSearches to solr.

    Inputs:
    :solr_location: Dict of separate cores to be updated (Optional);
        defaults to the default instance from settings
    """
    if solr_location is None:
        solr_location = settings.SOLR
    l = []

    u = User.objects.all().values_list('id', flat=True)
    for x in u:
        l.append(profileunits_to_dict(x))

    s = SavedSearch.objects.all()
    for x in s:
        saved_search_dict = object_to_dict(SavedSearch, x)
        saved_search_dict['doc_type'] = 'savedsearch'
        l.append(saved_search_dict)

    u = User.objects.all()
    for x in u:
        l.append(object_to_dict(User, x))

    l = split_list(l, 1000)

    for location in solr_location.values():
        solr = pysolr.Solr(location)
        for x in l:
            x = filter(None, list(x))
            solr.add(x)


def parse_log(logs, solr_location):
    """
    Turns a list of boto keys into a list of dicts, with each dict representing
    a line from the keys

    Inputs:
    :logs: List of logs generated by boto that reference files on s3
        Lines in analytics logs are formatted as follows:
            %{%Y-%m-%d %H:%M:%S}t %a %m %U %q %H %s %{Referer}i %{aguid}C
                %{myguid}C %{user-agent}i
        Lines in redirect logs are formatted slightly differently:
            %{%Y-%m-%d %H:%M:%S}t %a %m %U %{X-REDIRECT}o %p %u %{X-Real-IP}i
                %H "%{User-agent}i" %{r.my.jobs}C %{Referer}i %V %>s %O %I %D

    :solr_location: Dict of separate cores to be updated (Optional);
        defaults to the default instance from settings
    """
    # Logs are potentially very large. If we are going to look up the company
    # associated with each hit, we should memoize the ids.
    log_memo = {}

    for log in logs:
        to_solr = []
        path = '/tmp/parse_log'
        # Ensure local temp storage for log files exists
        try:
            os.mkdir(path)
        except OSError:
            if not os.path.isdir(path):
                raise
        f = open('%s/%s' % (path, uuid.uuid4().hex), 'w+')
        try:
            log.get_contents_to_file(f)
            f.seek(0)

            for line in f:
                if line[0] == '#':
                    # Logs contain a header that LogParser uses to determine
                    # the log format; if we see this, ignore it
                    continue

                # line in f does not strip newlines if they exist
                line = line.rstrip('\n')
                line = line.split(' ')

                # reconstruct date and time
                line[0] = '%s %s' % (line[0], line[1])
                # turn date and time into a datetime object
                line[0] = datetime.strptime(line[0], '%Y-%m-%d %H:%M:%S')
                # remove the time portion, which is now merged with the date
                del line[1]

                # reconstruct user agent
                # and remove it from the line
                if 'redirect' in log.key:
                    ua = ' '.join(line[9:-7])
                    del line[9:-7]
                else:
                    ua = line[8]
                    del line[8]

                if not helpers.is_bot(ua):
                    # Only track hits that come from actual users
                    update_dict = {
                        'view_date': line[0],
                        'doc_type': 'analytics',
                    }

                    # Make sure the value for a given key is only a list if
                    # there are multiple elements
                    qs = dict((k, v if len(v) > 1 else v[0])
                              for k, v in urlparse.parse_qs(
                                  line[4]).iteritems())

                    if 'redirect' in log.key:
                        aguid = qs.get('jcnlx.aguid', '')
                        myguid = qs.get('jcnlx.myguid', '')
                        update_dict['view_source'] = qs.get('jcnlx.vsid', 0)
                        update_dict['job_view_buid'] = qs.get('jcnlx.buid', '0')

                        # GUID is the path portion of this line, which starts
                        # with a '/'; Remove it
                        update_dict['job_view_guid'] = line[3][1:]
                        update_dict['page_category'] = 'redirect'
                        domain = qs.get('jcnlx.ref', '')
                        domain = urlparse.urlparse(domain).netloc
                        update_dict['domain'] = domain
                    else:
                        aguid = qs.get('aguid', '')
                        myguid = qs.get('myguid', '')
                        update_dict['view_source'] = qs.get('jvs', 0)
                        update_dict['job_view_buid'] = qs.get('jvb', '0')
                        update_dict['job_view_guid'] = qs.get('jvg', '')
                        update_dict['page_category'] = qs.get('pc', '')

                        # These fields are only set in analytics logs
                        update_dict['domain'] = qs.get('d', '')
                        update_dict['facets'] = qs.get('f', '')
                        update_dict['job_view_title_exact'] = qs.get('jvt', '')
                        update_dict['job_view_company_exact'] = qs.get('jvc', '')
                        update_dict['job_view_location_exact'] = qs.get('jvl', '')
                        update_dict['job_view_canonical_domain'] = qs.get('jvcd', '')
                        update_dict['search_location'] = qs.get('sl', '')
                        update_dict['search_query'] = qs.get('sq', '')
                        update_dict['site_tag'] = qs.get('st', '')
                        update_dict['special_commitment'] = qs.get('sc', '')

                    # Handle logs containing the old aguid/myguid formats
                    aguid = aguid.replace('{', '').replace('}', '').replace('-', '')
                    update_dict['aguid'] = aguid

                    myguid = myguid.replace('-', '')

                    if myguid:
                        try:
                            user = User.objects.get(user_guid=myguid)
                        except User.DoesNotExist:
                            update_dict['User_user_guid'] = ''
                        else:
                            update_dict.update(object_to_dict(User, user))

                    buid = update_dict['job_view_buid']
                    domain = update_dict.get('domain', None)
                    if not (buid in log_memo or domain in log_memo):
                        # We haven't seen this buid or domain before
                        if buid == '0' and domain is not None:
                            # Retrieve company id via domain
                            try:
                                site = SeoSite.objects.get(domain=domain)
                                company_id = site.business_units.values_list(
                                    'company__pk', flat=True)[0]
                            except (SeoSite.DoesNotExist,
                                    IndexError):
                                # SeoSite.DoesNotExist: Site does not exist
                                #   with the given domain
                                # IndexError: SeoSite exists, but is not
                                #   associated with business units or companies
                                company_id = 999999
                            key = domain
                        else:
                            # Retrieve company id via buid
                            try:
                                # See if there is a company associated with it
                                company_id = Company.objects.filter(
                                    job_source_ids=buid)[0].pk
                            except IndexError:
                                # There is not; default to DirectEmployers
                                # Association
                                company_id = 999999
                            key = buid

                        # The defining feature of a given document will either
                        # be the domain or the buid.
                        # Our memoization dict will have the following structure
                        # {str(buid): int(company_id),
                        #  str(domain): int(company_id)}
                        log_memo[key] = company_id

                    # By this point, we are guaranteed that the correct key is
                    # in log_memo; pull the company id from the memo dict.
                    if domain is not None and domain in log_memo:
                        update_dict['company_id'] = log_memo[domain]
                    else:
                        update_dict['company_id'] = log_memo[buid]

                    update_dict['uid'] = 'analytics##%s#%s' % \
                        (update_dict['view_date'], aguid)
                    to_solr.append(update_dict)
        except Exception:
            # There may be more logs to process, don't propagate the exception
            pass
        finally:
            # remove the file from the filesystem to ensure we don't fill the
            # drive (again)
            f.close()
            os.remove(f.name)

        # Ensure all hits get recorded by breaking a potentially massive list
        # down into something that solr can manage
        subsets = split_list(to_solr, 500)
        for location in solr_location.values():
            solr = pysolr.Solr(location)
            for subset in subsets:
                subset = filter(None, subset)
                solr.add(subset)


@task(name="tasks.delete_old_analytics_docs")
def delete_old_analytics_docs():
    """
    Deletes all analytics docs from the "current" collection that are older
    than 30 days
    """
    if hasattr(mail, 'outbox'):
        solr_location = settings.TEST_SOLR_INSTANCE['current']
    else:
        solr_location = settings.SOLR['current']

    pysolr.Solr(solr_location).delete(
        q="doc_type:analytics AND view_date:[* TO NOW/DAY-30DAYS]")


@task(name="tasks.update_solr_from_log")
def read_new_logs(solr_location=None):
    """
    Reads new logs and stores their contents in solr

    Inputs:
    :solr_location: Dict of separate cores to be updated (Optional);
        defaults to the default instance from settings
    """
    # If running tests, use test instance of local solr
    if hasattr(mail, 'outbox'):
        solr_location = settings.TEST_SOLR_INSTANCE
    elif solr_location is None:
        solr_location = settings.SOLR

    conn = boto.connect_s3(aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                           aws_secret_access_key=settings.AWS_SECRET_KEY)
    # https://github.com/boto/boto/issues/2078
    # validate=True costs 13.5x validate=False; Skip validation if we are
    # reasonably certain that the bucket exists.
    log_bucket = conn.get_bucket('my-jobs-logs', validate=False)

    # Sort logs into groups based on server
    all_logs = log_bucket.list()
    logs_by_host = {}
    for log in all_logs:
        # Logs are being stored with a key of host/log_type/file.log
        key_parts = log.key.split('/')

        # Since we are also storing redirect error logs, we should ensure
        # we are only processing the logs we care about
        if key_parts[1] in ['analytics', 'redirect']:
            logs_by_host.setdefault(key_parts[0], []).append(log)

    logs_to_process = []
    for key in logs_by_host.keys():
        # Files are named by date and time; the last log for each host is the
        # last log uploaded by that host
        logs_to_process += logs_by_host[key][-1:]

    # Ensure we only process each['href'] file once
    processed = getattr(settings, 'PROCESSED_LOGS', set())
    unprocessed = [log for log in logs_to_process if log.key not in processed]

    parse_log(unprocessed, solr_location)

    settings.PROCESSED_LOGS = set([log.key for log in logs_to_process])

    delete_old_analytics_docs.delay()


@task(name='tasks.expire_jobs')
def expire_jobs():
    jobs = Job.objects.filter(date_expired=date.today(),
                              is_expired=False, autorenew=False)
    for job in jobs:
        # Setting is_expired to True will trigger job.remove_from_solr()
        job.is_expired = True
        job.save()

    jobs = Job.objects.filter(date_expired=date.today(),
                              is_expired=False, autorenew=True)
    for job in jobs:
        job.date_expired = date.today() + timedelta(days=30)
        # Saving will trigger job.add_to_solr().
        job.save()