from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.utils.text import get_text_list, force_unicode, force_text
from django.utils.translation import ugettext

from datetime import datetime, time, timedelta
import re
from urlparse import urlparse, parse_qsl, urlunparse
from urllib import urlencode

from mydashboard.models import Company
from mypartners.models import (ContactLogEntry, CONTACT_TYPE_CHOICES, CHANGE)


def prm_worthy(request):
    """
    Makes sure the User is worthy enough to use PRM.

    """
    company_id = request.REQUEST.get('company')
    company = get_object_or_404(Company, id=company_id)

    user = request.user
    if not user in company.admins.all():
        raise Http404

    partner_id = int(request.REQUEST.get('partner'))
    partner = get_object_or_404(company.partner_set, id=partner_id)

    return company, partner, user


def add_extra_params(url, extra_urls):
    """
    Adds extra parameters to a url

    Inputs:
    :url: Url that parameters will be added to
    :extra_urls: Extra parameters to be added

    Outputs:
    :url: Input url with parameters added
    """
    extra_urls = extra_urls.lstrip('?&')
    new_queries = dict(parse_qsl(extra_urls, keep_blank_values=True))

    # By default, extra parameters besides vs are discarded by the redirect
    # server. We can get around this by adding &z=1 to the url, which enables
    # custom query parameter overrides.
    new_queries['z'] = '1'

    parts = list(urlparse(url))
    query = dict(parse_qsl(parts[4], keep_blank_values=True))
    query.update(new_queries)
    parts[4] = urlencode(query)
    return urlunparse(parts)


def add_extra_params_to_jobs(items, extra_urls):
    """
    Adds extra parameters to all jobs in a list

    Inputs:
    :items: List of jobs to which extra parameters should be added
    :extra_urls: Extra parameters to be added

    Modifies:
    :items: List is mutable and is modified in-place
    """
    for item in items:
        item['link'] = add_extra_params(item['link'], extra_urls)


def log_change(obj, form, user, partner, contact_identifier,
               action_type=CHANGE, change_msg=None):
    """
    Creates a ContactLogEntry for obj.

    inputs:
    :obj: The object a log entry is being created for
    :form: The form the log entry is being created from. This is optional,
        but without it a valuable change message can't be created, so either
        one will need to be passed to the function or there won't be a change
        message for this log entry.
    :user: The user who caused the change. Can be null, but shouldn't be unless
        in most cases.
    :partner: The partner this object applies to. Should never be null.
    :contact_identifier: Some meaningful piece of information (e.g. name,
        email, phone number) that identifies the person being contacted.
    :action_type: The action being taken. Available types are in
        mypartners.models.
    :change_msg: A short description of the changes made. If one isn't provided,
        the change_msg will attempt to be created from the form.

    """
    if not change_msg:
        change_msg = get_change_message(form) if action_type == CHANGE else ''

    ContactLogEntry.objects.create(
        action_flag=action_type,
        change_message=change_msg,
        contact_identifier=contact_identifier,
        content_type=ContentType.objects.get_for_model(obj),
        object_id=obj.pk,
        object_repr=force_text(obj)[:200],
        partner=partner,
        user=user,
    )


def get_change_message(form):
    """
    Creates a list of changes made from a form.

    """
    change_message = []
    if not form:
        return ''
    if form.changed_data:
        change_message = (ugettext('Changed %s.') %
                          get_text_list(form.changed_data, ugettext('and')))
    return change_message or ugettext('No fields changed.')


def get_attachment_link(company_id, partner_id, attachment_id, attachment_name):
    """
    Creates a link (html included) to a PRMAttachment.

    """
    url = '/prm/download?company=%s&partner=%s&id=%s' % (company_id,
                                                         partner_id,
                                                         attachment_id)

    html = "<a href='{url}' target='_blank'>{attachment_name}</a>"
    return mark_safe(html.format(url=url, attachment_name=attachment_name))


def retrieve_fields(model):
    fields = [field for field in model._meta.get_all_field_names()
              if unicode(field) not in [u'id', u'prmattachment']]
    return fields


def contact_record_val_to_str(value):
    """
    Translates a field value from a contact record into a human-readable string.
    Dates are formatted "ShortMonth Day, Year Hour:Minute AMorPM"
    Times are formatted "XX Hours XX Minutes"
    If the value matches a contact type choice it's translated to the
    verbose form.
    """

    value = (value.strftime('%b %d, %Y %I:%M %p') if type(value)
             is datetime else value.strftime('%H hours %M minutes')
             if type(value) is time else force_unicode(value))

    contact_types = dict(CONTACT_TYPE_CHOICES)
    if value in contact_types:
        value = contact_types[value]

    return value


def get_records_from_request(request):
    """
    Filters a list of records on partner, date_time, contact_name, and
    contact_type based on the request

    outputs:
    The date range filtered on, A string "X Day(s)" representing the
    date filtered on, and the filtered records.


    """
    company, partner, user = prm_worthy(request)

    contact = request.REQUEST.get('contact')
    contact_type = request.REQUEST.get('record_type')
    contact = None if contact == 'all' else contact
    contact_type = None if contact_type == 'all' else contact_type
    records = partner.get_contact_records(contact_name=contact,
                                          record_type=contact_type)

    date_range = request.REQUEST.get('date')
    if date_range:
        try:
            date_range = int(date_range)
        except (TypeError, ValueError):
            date_range = 30
        range_end = datetime.now()
        range_start = datetime.now() - timedelta(date_range)
    else:
        range_start = request.REQUEST.get('date_start')
        range_end = request.REQUEST.get('date_end')
        try:
            range_start = datetime.strptime(range_start, "%m/%d/%Y")
            range_end = datetime.strptime(range_end, "%m/%d/%Y")
        except (AttributeError, TypeError, ValueError):
            range_start = None
            range_end = None
    date_str = 'Filter by time range'
    if range_start and range_end:
        try:
            date_str = (range_end - range_start).days + 1
            date_str = (("%s Days" % date_str) if date_str != 1
                        else ("%s Day" % date_str))
            records = records.filter(date_time__range=[range_start, range_end])
        except (ValidationError, TypeError):
            pass

    range_start = (datetime.now() + timedelta(-30) if not range_start else
                   range_start)
    range_end = datetime.now() if not range_end else range_end

    return (range_start, range_end), date_str, records


def send_contact_record_email_response(created_records, created_contacts,
                                       unmatched_contacts, error, to_email):
    ctx = {
        'created_records': created_records,
        'created_contacts': created_contacts,
        'error': error,
        'unmatched_contacts': unmatched_contacts,
    }

    subject = 'Partner Relationship Manager Contact Records'
    message = render_to_string('mypartners/email/email_response.html',
                               ctx)

    msg = EmailMessage(subject, message, settings.PRM_EMAIL, [to_email])
    msg.content_subtype = 'html'
    msg.send()


def find_partner_from_email(partner_list, email):
    """
    Finds a possible partner based on the email domain.

    inputs:
    :partner_list: The partner list to compare the email against.
    :email: The email address the domain is needed for.

    outputs:
    A matching partner if there is one, otherwise None.

    """
    if '@' not in email or not partner_list:
        return None
    email_domain = email.split('@')[-1]

    pattern = re.compile('(http://|https://)?(www)?\.?(?P<url>.*)')
    for partner in partner_list:
        try:
            url = pattern.search(partner.uri).groupdict()['url'].split("/")[0]
        except (AttributeError, KeyError):
            pass
        if email_domain.lower() == url.lower():
            return partner

    return None