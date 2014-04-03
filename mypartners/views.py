from collections import OrderedDict
import unicodecsv
from datetime import date, datetime, timedelta
from email.parser import HeaderParser
from email.utils import getaddresses, mktime_tz, parsedate_tz
from itertools import chain
import json
from lxml import etree

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.contrib.contenttypes.models import ContentType
from django.core.files.storage import default_storage
from django.db.models import Count
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.text import force_text
from django.utils.timezone import utc
from django.views.decorators.csrf import csrf_exempt

from email_parser import build_email_dicts, get_datetime_from_str
from myjobs.models import User
from mydashboard.models import Company
from mysearches.models import PartnerSavedSearch
from mysearches.helpers import (url_sort_options, parse_feed,
                                get_interval_from_frequency)
from mysearches.forms import PartnerSavedSearchForm
from mypartners.forms import (PartnerForm, ContactForm, PartnerInitialForm,
                              NewPartnerForm, ContactRecordForm)
from mypartners.models import (Partner, Contact, ContactRecord, PRMAttachment,
                               ContactLogEntry, CONTACT_TYPE_CHOICES,
                               ADDITION, DELETION)
from mypartners.helpers import (prm_worthy, add_extra_params,
                                add_extra_params_to_jobs, log_change,
                                contact_record_val_to_str, retrieve_fields,
                                get_records_from_request,
                                send_contact_record_email_response,
                                find_partner_from_email, get_int_or_none)


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def prm(request):
    """
    Partner Relationship Manager

    """
    company_id = request.REQUEST.get('company')

    if company_id is None:
        try:
            company = Company.objects.filter(admins=request.user)[0]
        except Company.DoesNotExist:
            raise Http404
    else:
        company = get_object_or_404(Company, id=company_id)

    user = request.user
    if not user in company.admins.all():
        raise Http404

    form = request.REQUEST.get('form')
    if not company.partner_set.all():
        if not form:
            partner_form = PartnerInitialForm()
        partners = []
    else:
        try:
            partners = Partner.objects.filter(owner=company.id)
        except Partner.DoesNotExist:
            raise Http404
        partner_form = None

    ctx = {'has_partners': True if partners else False,
           'partners': partners,
           'form': partner_form or form,
           'company': company,
           'user': user,
           'partner_ct': ContentType.objects.get_for_model(Partner).id,
           'view_name': 'PRM'}

    return render_to_response('mypartners/prm.html', ctx,
                              RequestContext(request))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def partner_details(request):
    company, partner, user = prm_worthy(request)

    form = PartnerForm(instance=partner, auto_id=False)

    contacts = Contact.objects.filter(partner=partner)
    contact_ct_id = ContentType.objects.get_for_model(Contact).id
    partner_ct_id = ContentType.objects.get_for_model(Partner).id

    ctx = {'company': company,
           'form': form,
           'contacts': contacts,
           'partner': partner,
           'contact_ct': contact_ct_id,
           'partner_ct': partner_ct_id,
           'view_name': 'PRM'}
    return render_to_response('mypartners/partner_details.html', ctx,
                              RequestContext(request))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def edit_item(request):
    """
    Form page that is what makes new and edits partners/contacts.

    """
    company_id = request.REQUEST.get('company')

    company = get_object_or_404(Company, id=company_id)

    user = request.user
    if not user in company.admins.all():
        raise Http404

    # If the user is trying to create a new Partner they won't have a
    # partner_id. A Contact however does, it also comes from a different URL.
    if request.path != reverse('create_partner'):
        try:
            partner_id = int(request.REQUEST.get('partner'))
        except TypeError:
            raise Http404
        partner = get_object_or_404(company.partner_set.all(), id=partner_id)
    else:
        partner = None

    try:
        content_id = int(request.REQUEST.get('ct'))
    except TypeError:
        raise Http404
    item_id = request.REQUEST.get('id') or None

    if content_id == ContentType.objects.get_for_model(Partner).id:
        if not item_id:
            form = NewPartnerForm()
        else:
            item = get_object_or_404(Partner, pk=item_id)
            form = PartnerForm(instance=item)
    elif content_id == ContentType.objects.get_for_model(Contact).id:
        if not item_id:
            form = ContactForm()
        else:
            try:
                item = Contact.objects.get(partner=partner, pk=item_id)
            except:
                raise Http404
            form = ContactForm(instance=item, auto_id=False)
    else:
        raise Http404

    ctx = {'form': form,
           'partner': partner,
           'company': company,
           'contact': item_id,
           'content_id': content_id,
           'view_name': 'PRM'}

    return render_to_response('mypartners/edit_item.html', ctx,
                              RequestContext(request))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def save_init_partner_form(request):
    if 'partnername' in request.POST:
        form = NewPartnerForm(user=request.user, data=request.POST)
    else:
        form = PartnerInitialForm(user=request.user, data=request.POST)
    if form.is_valid():
        form.save(request.user)
        return HttpResponse(status=200)
    else:
        return HttpResponse(json.dumps(form.errors))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def save_item(request):
    """
    Generic save for Partner and Contact Forms.

    """
    company_id = request.REQUEST.get('company')

    company = get_object_or_404(Company, id=company_id)

    content_id = int(request.REQUEST.get('ct'))

    if content_id == ContentType.objects.get_for_model(Contact).id:
        item_id = request.REQUEST.get('id') or None
        try:
            partner_id = int(request.REQUEST.get('partner'))
        except TypeError:
            raise Http404

        partner = get_object_or_404(company.partner_set.all(), id=partner_id)

        if item_id:
            try:
                item = Contact.objects.get(partner=partner, pk=item_id)
            except Contact.DoesNotExist:
                raise Http404
            else:
                form = ContactForm(instance=item, auto_id=False,
                                   data=request.POST)
                if form.is_valid():
                    form.save(request.user, partner)
                    return HttpResponse(status=200)
                else:
                    return HttpResponse(json.dumps(form.errors))
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save(request.user, partner)
            return HttpResponse(status=200)
        else:
            return HttpResponse(json.dumps(form.errors))

    if content_id == ContentType.objects.get_for_model(Partner).id:
        try:
            partner_id = int(request.REQUEST.get('partner'))
        except TypeError:
            raise Http404

        partner = get_object_or_404(company.partner_set.all(), id=partner_id)
        form = PartnerForm(instance=partner, auto_id=False, data=request.POST)
        if form.is_valid():
            form.save(request.user)
            return HttpResponse(status=200)
        else:
            return HttpResponse(json.dumps(form.errors))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def delete_prm_item(request):
    """
    Deletes Partners and Contacts

    """
    company_id = request.REQUEST.get('company')
    company = get_object_or_404(Company, id=company_id)

    partner_id = request.REQUEST.get('partner')
    partner_id = get_int_or_none(partner_id)
    item_id = request.REQUEST.get('id')
    contact_id = get_int_or_none(item_id)
    content_id = request.REQUEST.get('ct')
    content_id = get_int_or_none(content_id)

    if content_id == ContentType.objects.get_for_model(Contact).id:
        partner = get_object_or_404(Partner, id=partner_id, owner=company)
        contact = get_object_or_404(Contact, id=contact_id)
        log_change(contact, None, request.user, partner, contact.name,
                   action_type=DELETION)
        contact.delete()
        return HttpResponseRedirect(reverse('partner_details')+'?company=' +
                                    str(company_id)+'&partner=' +
                                    str(partner_id))
    elif content_id == ContentType.objects.get_for_model(Partner).id:
        partner = get_object_or_404(Partner, id=partner_id, owner=company)
        Contact.objects.filter(partner=partner).delete()
        log_change(partner, None, request.user, partner, partner.name,
                   action_type=DELETION)
        partner.delete()
        return HttpResponseRedirect(reverse('prm') + '?company=' +
                                    str(company_id))
    elif content_id == ContentType.objects.get_for_model(ContactRecord).id:
        contact_record = get_object_or_404(ContactRecord, partner=partner_id,
                                           id=item_id)
        partner = get_object_or_404(Partner, id=partner_id, owner=company)
        log_change(contact_record, None, request.user, partner,
                   contact_record.contact_name, action_type=DELETION)
        contact_record.delete()
        return HttpResponseRedirect(reverse('partner_records')+'?company=' +
                                    str(company_id)+'&partner=' +
                                    str(partner_id))
    elif content_id == ContentType.objects.get_for_model(PartnerSavedSearch).id:
        saved_search = get_object_or_404(PartnerSavedSearch, id=item_id)
        partner = get_object_or_404(Partner, id=partner_id, owner=company)
        log_change(saved_search, None, request.user, partner,
                   saved_search.email, action_type=DELETION)
        saved_search.delete()
        return HttpResponseRedirect(reverse('partner_searches')+'?company=' +
                                    str(company_id)+'&partner=' +
                                    str(partner_id))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def prm_overview(request):
    """
    View that is the "Overview" of one's Partner Activity.

    """
    company, partner, user = prm_worthy(request)

    most_recent_activity = partner.get_logs()
    dt_range = [datetime.now() + timedelta(-30), datetime.now()]
    records = partner.get_contact_records(date_time_range=dt_range)
    communication = records.order_by('-date_time')
    referrals = records.filter(contact_type='job').count()
    records = records.exclude(contact_type='job').count()
    most_recent_communication = communication[:3]
    saved_searches = partner.get_searches()
    most_recent_saved_searches = saved_searches[:3]

    older_records = partner.get_contact_records()
    older_records = older_records.exclude(date_time__gte=datetime.now() +
                                                         timedelta(-30))

    ctx = {'partner': partner,
           'company': company,
           'recent_activity': most_recent_activity,
           'recent_communication': most_recent_communication,
           'recent_ss': most_recent_saved_searches,
           'count': records,
           'referrals': referrals,
           'view_name': 'PRM',
           'num_older_records': older_records.count(),
           'num_other_records': saved_searches.count() - 3, }

    return render_to_response('mypartners/overview.html', ctx,
                              RequestContext(request))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def prm_saved_searches(request):
    """
    View that lists the Partner's Saved Searches

    """
    company, partner, user = prm_worthy(request)
    saved_searches = partner.get_searches()
    ctx = {'searches': saved_searches,
           'company': company,
           'partner': partner}
    return render_to_response('mypartners/partner_searches.html', ctx,
                              RequestContext(request))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def prm_edit_saved_search(request):
    company, partner, user = prm_worthy(request)
    item_id = request.REQUEST.get('id')
    if item_id:
        instance = get_object_or_404(PartnerSavedSearch, id=item_id)
        form = PartnerSavedSearchForm(partner=partner, instance=instance)
    else:
        form = PartnerSavedSearchForm(partner=partner)
    microsites = []
    for microsite in company.microsite_set.all():
        ms = {'url': microsite.url}
        readable_url = microsite.url.split('//')[1]
        readable_url = readable_url.rstrip('/')
        ms['name'] = readable_url
        microsites.append(ms)

    ctx = {
        'company': company,
        'partner': partner,
        'item_id': item_id,
        'form': form,
        'microsites': microsites,
        'content_type': ContentType.objects.get_for_model(PartnerSavedSearch).id,
        'view_name': 'PRM'
    }
    return render_to_response('mypartners/partner_edit_search.html', ctx,
                              RequestContext(request))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def verify_contact(request):
    """
    Checks to see if a contact has a My.jobs account. Checks to see if they are
    active as well.

    """
    if request.REQUEST.get('action') != 'validate':
        raise Http404
    email = request.REQUEST.get('email')
    if email == 'None':
        return HttpResponse(json.dumps(
            {'status': 'None',
             'message': 'If a contact does not have an email they will not '
                        'show up on this list.'}))
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return HttpResponse(json.dumps(
            {'status': 'unverified',
             'message': 'A My.jobs account will be created for this contact, '
                        'which will include a personal greeting.'}))
    else:
        # Check to see if user is active
        if user.is_active:
            return HttpResponse(json.dumps(
                {'status': 'verified',
                 'message': ''}))
        else:
            return HttpResponse(json.dumps(
                {'status': 'unverified',
                 'message': 'This contact has an account on My.jobs already '
                            'but has yet to activate their account.'}))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def partner_savedsearch_save(request):
    """
    Handles saving the PartnerSavedSearchForm and creating the inactive user
    if it is needed.

    """
    company, partner, user = prm_worthy(request)
    item_id = request.REQUEST.get('id', None)

    if item_id:
        item = get_object_or_404(PartnerSavedSearch, id=item_id,
                                 provider=company.id)
        form = PartnerSavedSearchForm(instance=item, auto_id=False,
                                      data=request.POST,
                                      partner=partner)
        if form.is_valid():
            form.save()
            return HttpResponse(status=200)
        else:
            return HttpResponse(json.dumps(form.errors))
    form = PartnerSavedSearchForm(request.POST, partner=partner)

    # Since the feed is created below, this will always be invalid.
    if 'feed' in form.errors:
        del form.errors['feed']

    if form.is_valid():
        instance = form.instance
        instance.feed = form.data['feed']
        instance.provider = company
        instance.partner = partner
        instance.created_by = request.user
        instance.custom_message = instance.partner_message
        form.save()
        return HttpResponse(status=200)
    else:
        return HttpResponse(json.dumps(form.errors))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def partner_view_full_feed(request):
    """
    PartnerSavedSearch feed.

    """
    company, partner, user = prm_worthy(request)
    search_id = request.REQUEST.get('id')
    saved_search = get_object_or_404(PartnerSavedSearch, id=search_id)

    if company == saved_search.partnersavedsearch.provider:
        url_of_feed = url_sort_options(saved_search.feed,
                                       saved_search.sort_by,
                                       saved_search.frequency)
        items, count = parse_feed(url_of_feed, saved_search.frequency)
        start_date = date.today() + timedelta(get_interval_from_frequency(
            saved_search.frequency))
        extras = saved_search.partnersavedsearch.url_extras
        if extras:
            add_extra_params_to_jobs(items, extras)
            saved_search.url = add_extra_params(saved_search.url, extras)
    else:
        return HttpResponseRedirect(reverse('prm_saved_searches'))

    ctx = {
        'search': saved_search,
        'items': items,
        'view_name': 'Saved Searches',
        'is_pss': True,
        'partner': partner.id,
        'company': company.id,
        'start_date': start_date,
        'count': count
    }

    return render_to_response('mysearches/view_full_feed.html', ctx,
                              RequestContext(request))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def prm_records(request):
    """
    ContactRecord overview and ContactRecord overview from PRM reports.

    """
    company, partner, user = prm_worthy(request)
    contact_type = request.REQUEST.get('record_type')
    contact = request.REQUEST.get('contact')

    dt_range, date_str, contact_records = get_records_from_request(request)
    most_recent_activity = partner.get_logs()

    contact_type_choices = list(CONTACT_TYPE_CHOICES)
    try:
        index = [x[0] for x in contact_type_choices].index(contact_type)
        contact_type_choices.insert(0, contact_type_choices.pop(index))
        contact_type_choices.append(('all', 'All'))
    except ValueError:
        contact_type_choices.insert(0, ('all', 'All'))
    try:
        index = [x[0] for x in contact_type_choices].index('pssemail')
        contact_type_choices.pop(index)
    except ValueError:
        pass

    contacts = ContactRecord.objects.filter(partner=partner)
    contacts = contacts.values('contact_name').distinct()
    contact_choices = [(c['contact_name'], c['contact_name']) for c in contacts]
    try:
        index = [x[0] for x in contact_choices].index(contact)
        contact_choices.insert(0, contact_choices.pop(index))
        contact_choices.append(('all', 'All'))
    except ValueError:
        contact_choices.insert(0, ('all', 'All'))

    ctx = {
        'admin_id': request.REQUEST.get('admin'),
        'company': company,
        'contact': contact,
        'contact_choices': contact_choices,
        'contact_type': contact_type,
        'contact_type_choices': contact_type_choices,
        'date_display': date_str,
        'date_start': dt_range[0],
        'date_end': dt_range[1],
        'most_recent_activity': most_recent_activity,
        'partner': partner,
        'records': contact_records.order_by('-date_time'),
        'view_name': 'PRM'
    }

    if request.path == reverse('prm_report_records'):
        return render_to_response('mypartners/report_record_view.html', ctx,
                                  RequestContext(request))
    else:
        return render_to_response('mypartners/main_records.html', ctx,
                                  RequestContext(request))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def prm_edit_records(request):
    company, partner, user = prm_worthy(request)
    record_id = request.GET.get('id', None)

    try:
        instance = ContactRecord.objects.get(pk=record_id)
    except ContactRecord.DoesNotExist:
        instance = None

    if request.method == 'POST':
        instance = None
        if record_id:
            try:
                instance = ContactRecord.objects.get(pk=record_id)
            except ContactRecord.DoesNotExist:
                instance = None
        form = ContactRecordForm(request.POST, request.FILES,
                                 partner=partner, instance=instance)
        if form.is_valid():
            form.save(user, partner)
            return HttpResponseRedirect(reverse('partner_records') +
                                        '?company=%d&partner=%d' %
                                        (company.id, partner.id))
    else:
        form = ContactRecordForm(partner=partner, instance=instance)

    ctx = {
        'company': company,
        'partner': partner,
        'content_type': ContentType.objects.get_for_model(ContactRecord).id,
        'object_id': record_id,
        'form': form,
    }
    return render_to_response('mypartners/edit_record.html', ctx,
                              RequestContext(request))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def prm_view_records(request):
    """
    View an individual ContactRecord.

    """
    company, partner, user = prm_worthy(request)
    record_id = request.GET.get('id')
    offset = request.GET.get('offset', 0)
    record_type = request.GET.get('type')
    name = request.GET.get('name')
    range_start = request.REQUEST.get('date_start')
    range_end = request.REQUEST.get('date_end')
    try:
        range_start = datetime.strptime(range_start, "%m/%d/%Y")
        range_end = datetime.strptime(range_end, "%m/%d/%Y")
    except (AttributeError, TypeError):
        range_start = None
        range_end = None

    try:
        record_id = int(record_id)
        offset = int(offset)
    except (TypeError, ValueError):
        return HttpResponseRedirect(reverse('partner_records') +
                                    '?company=%d&partner=%d' %
                                    (company.id, partner.id))

    prev_offset = (offset - 1) if offset > 1 else 0
    records = partner.get_contact_records(record_type=record_type,
                                          contact_name=name,
                                          date_time_range=[range_start,
                                                           range_end],
                                          offset=prev_offset,
                                          limit=prev_offset + 3)

    # Since we always retrieve 3, if the record is at the beginning of the
    # list we might have 3 results but no previous.
    if len(records) == 3 and records[0].pk == record_id:
        prev_id = None
        record = records[0]
        next_id = records[1].pk
    elif len(records) == 3:
        prev_id = records[0].pk
        record = records[1]
        next_id = records[2].pk
    # If there are only 2 results, it means there is either no next or
    # no previous, so we need to compare record ids to figure out which
    # is which.
    elif len(records) == 2 and records[0].pk == record_id:
        prev_id = None
        record = records[0]
        next_id = records[1].pk
    elif len(records) == 2:
        prev_id = records[0].pk
        record = records[1]
        next_id = None
    elif len(records) == 1:
        prev_id = None
        record = records[0]
        next_id = None
    else:
        prev_id = None
        record = get_object_or_404(ContactRecord, pk=record_id)
        next_id = None

    # Double check our results and drop the next and previous options if
    # the results were wrong
    if record_id != record.pk:
        prev_id = None
        record = get_object_or_404(ContactRecord, pk=record_id)
        next_id = None

    attachments = PRMAttachment.objects.filter(contact_record=record)
    logs = ContactLogEntry.objects.filter(object_id=record_id)
    record_history = ContactLogEntry.objects.filter(object_id=record_id)
    ctx = {
        'date_start': range_start,
        'date_end': range_end,
        'record': record,
        'partner': partner,
        'company': company,
        'activity': logs,
        'attachments': attachments,
        'record_history': record_history,
        'next_id': next_id,
        'next_offset': offset + 1,
        'prev_id': prev_id,
        'prev_offset': prev_offset,
        'contact_type': record_type,
        'contact_name': name,
        'view_name': 'PRM'

    }

    return render_to_response('mypartners/view_record.html', ctx,
                              RequestContext(request))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def get_contact_information(request):
    """
    Returns a json object containing a contact's email address and
    phone number if they have one.

    """
    company, partner, user = prm_worthy(request)
    contact_id = request.REQUEST.get('contact_name')
    try:
        contact = Contact.objects.get(pk=contact_id)
    except Contact.DoesNotExist:
        data = {'error': 'Contact does not exist'}
        return HttpResponse(json.dumps(data))

    if partner != contact.partner:
        data = {'error': 'Permission denied'}
        return HttpResponse(json.dumps(data))

    if hasattr(contact, 'email'):
        if hasattr(contact, 'phone'):
            data = {'email': contact.email,
                    'phone': contact.phone}
        else:
            data = {'email': contact.email}
    else:
        if hasattr(contact, 'phone'):
            data = {'phone': contact.phone}
        else:
            data = {}

    return HttpResponse(json.dumps(data))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def get_records(request):
    """
    Returns a json object containing the records matching the search
    criteria (contact, contact_type, and date_time range) rendered using
    records.html and the date range and date string required to update
    the time_filter.html template to match the search.

    """
    company, partner, user = prm_worthy(request)

    contact = request.REQUEST.get('contact')
    contact_type = request.REQUEST.get('record_type')
    contact = None if contact == 'all' else contact
    contact_type = None if contact_type == 'all' else contact_type
    dt_range, date_str, records = get_records_from_request(request)

    ctx = {
        'records': records.order_by('-date_time'),
        'company': company,
        'partner': partner,
        'contact_type': None if contact_type == 'all' else contact_type,
        'contact_name': None if contact == 'all' else contact,
        'view_name': 'PRM'
    }

    data = {
        'month_end': dt_range[1].strftime('%m'),
        'day_end': dt_range[1].strftime('%d'),
        'year_end': dt_range[1].strftime('%Y'),
        'month_start': dt_range[0].strftime('%m'),
        'day_start': dt_range[0].strftime('%d'),
        'year_start': dt_range[0].strftime('%Y'),
        'date_str': date_str,
        'html': render_to_response('mypartners/records.html', ctx,
                                   RequestContext(request)).content,
    }
    return HttpResponse(json.dumps(data))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def get_uploaded_file(request):
    """
    Determines the location of a PRMAttachment (either in S3 or in local
    storage) and redirects to it.

    PRMAttachments stored in S3 require a generated key and have a 10 minute
    access window.

    """
    company, partner, user = prm_worthy(request)
    file_id = request.GET.get('id', None)
    attachment = get_object_or_404(PRMAttachment, pk=file_id,
                                   contact_record__partner=partner)
    try:
        if repr(default_storage.connection) == 'S3Connection:s3.amazonaws.com':
            from boto.s3.connection import S3Connection

            s3 = S3Connection(settings.AWS_ACCESS_KEY_ID,
                              settings.AWS_SECRET_KEY, is_secure=True)
            path = s3.generate_url(600, 'GET',
                                   bucket=settings.AWS_STORAGE_BUCKET_NAME,
                                   key=attachment.attachment.name,
                                   force_http=True)
        else:
            path = "%s%s" % (settings.MEDIA_URL, attachment.attachment.name)
    except AttributeError:
        path = "%s%s" % (settings.MEDIA_URL, attachment.attachment.name)

    return HttpResponseRedirect(path)


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def partner_main_reports(request):
    company, partner, user = prm_worthy(request)
    dt_range, date_str, records = get_records_from_request(request)
    total_records_wo_followup = records.exclude(contact_type='job').count()
    referral = records.filter(contact_type='job').count()

    # need to order_by -count to keep the "All Contacts" list in proper order
    all_contacts = records.exclude(contact_type='pssemail')\
        .values('contact_name', 'contact_email')\
        .annotate(count=Count('contact_name')).order_by('-count')

    # Used for Top Contacts
    contact_records = records\
        .exclude(contact_type='job')\
        .exclude(contact_type='pssemail')\
        .values('contact_name', 'contact_email')\
        .annotate(count=Count('contact_name')).order_by('-count')

    # Individual Referral Records count
    referral_list = records.filter(contact_type='job')\
        .values('contact_name', 'contact_email')\
        .annotate(count=Count('contact_name'))

    # Merge contact_records with referral_list and have all contacts
    # A contact can have 0 contact records and 1 referral record and still show
    # up vice versa with 1 contact record and 0 referrals
    contacts = []
    for contact_obj in all_contacts:
        contact = {}
        name = contact_obj['contact_name']
        email = contact_obj['contact_email']
        contact['name'] = name
        contact['email'] = email
        for cr in contact_records:
            if cr['contact_name'] == name and cr['contact_email'] == email:
                contact['cr_count'] = cr['count']
        if not 'cr_count' in contact:
            contact['cr_count'] = 0
        for ref in referral_list:
            if ref['contact_name'] == name and ref['contact_email'] == email:
                contact['ref_count'] = ref['count']
        if not 'ref_count' in contact:
            contact['ref_count'] = 0
        contacts.append(contact)

    # calculate 'All Others' in Top Contacts (when more than 3)
    total_others = 0
    if contact_records.count() > 3:
        others = contact_records[3:]
        contact_records = contact_records[:3]
        for contact in others:
            total_others += contact['count']
    ctx = {
        'admin_id': request.REQUEST.get('admin'),
        'partner': partner,
        'company': company,
        'contacts': contacts,
        'total_records': total_records_wo_followup,
        'referral': referral,
        'top_contacts': contact_records,
        'others': total_others,
        'view_name': 'PRM',
        'date_start': dt_range[0],
        'date_end': dt_range[1],
        'date_display': date_str,
    }
    return render_to_response('mypartners/partner_reports.html', ctx,
                              RequestContext(request))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def partner_get_records(request):
    if request.method == 'GET':
        prm_worthy(request)

        dt_range, date_str, records = get_records_from_request(request)
        records = records.exclude(contact_type='job')
        email = records.filter(contact_type='email').count()
        email += records.filter(contact_type='pssemail').count()
        phone = records.filter(contact_type='phone').count()
        meetingorevent = records.filter(contact_type='meetingorevent').count()

        # figure names
        if email != 1:
            email_name = 'Emails'
        else:
            email_name = 'Email'
        if phone != 1:
            phone_name = 'Phone Calls'
        else:
            phone_name = 'Phone Call'
        if meetingorevent != 1:
            meetingorevent_name = 'Meeting or Event'
        else:
            meetingorevent_name = 'Meetings & Events'

        data = {
            'email': {"count": email, "name": email_name, 'typename': 'email'},
            'phone': {"count": phone, "name": phone_name, 'typename': 'phone'},
            'meetingorevent': {"count": meetingorevent,
                               "name": meetingorevent_name,
                               "typename": "meetingorevent"},
        }
        data = OrderedDict(sorted(data.items(), key=lambda t: t[1]['count']))
        data_items = data.items()
        data_items.reverse()
        data = OrderedDict(data_items)
        return HttpResponse(json.dumps(data))
    else:
        raise Http404


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def partner_get_referrals(request):
    if request.method == 'GET':
        prm_worthy(request)
        dt_range, date_str, records = get_records_from_request(request)
        referrals = records.filter(contact_type='job')

        # (job application, job interviews, job hires)
        nums = referrals.values_list('job_applications', 'job_interviews',
                                     'job_hires')

        applications, interviews, hires = 0, 0, 0
        # add numbers together
        for num_set in nums:
            try:
                applications += int(num_set[0])
            except (ValueError, KeyError):
                pass
            try:
                interviews += int(num_set[1])
            except (ValueError, KeyError):
                pass
            try:
                hires += int(num_set[2])
            except (ValueError, KeyError):
                pass

        # figure names
        if applications != 1:
            app_name = 'Applications'
        else:
            app_name = 'Application'
        if interviews != 1:
            interview_name = 'Interviews'
        else:
            interview_name = 'Interview'
        if hires != 1:
            hire_name = 'Hires'
        else:
            hire_name = 'Hire'

        data = {
            'applications': {'count': applications, 'name': app_name,
                             'typename': 'job'},
            'interviews': {'count': interviews, 'name': interview_name,
                           'typename': 'job'},
            'hires': {'count': hires, 'name': hire_name,
                      'typename': 'job'},
        }

        return HttpResponse(json.dumps(data))
    else:
        raise Http404


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def prm_export(request):
    company, partner, user = prm_worthy(request)
    file_format = request.REQUEST.get('file_format', 'csv')
    fields = retrieve_fields(ContactRecord)
    _, _, records = get_records_from_request(request)

    if file_format == 'xml':
        root = etree.Element("contact_records")
        for record in records:
            xml_record = etree.SubElement(root, "record")
            for field in fields:
                xml = etree.SubElement(xml_record, field)
                xml.text = contact_record_val_to_str(getattr(record, field, ""))
        response = HttpResponse(etree.tostring(root, pretty_print=True),
                                mimetype='application/force-download')
    elif file_format == 'printer_friendly':
        ctx = {
            'company': company,
            'fields': fields,
            'partner': partner,
            'records': records,
        }
        return render_to_response('mypartners/printer_friendly.html', ctx,
                                  RequestContext(request))
    # CSV/XLS
    else:
        response = HttpResponse(content_type='text/csv')
        writer = unicodecsv.writer(response, encoding='utf-8')
        writer.writerow(fields)
        for record in records:
            values = [getattr(record, field, '') for field in fields]
            values = [contact_record_val_to_str(v) for v in values]
            writer.writerow(values)

    response['Content-Disposition'] = 'attachment; ' \
                                      'filename="company_record_report".%s' \
                                      % file_format

    return response


@csrf_exempt
def process_email(request):
    """
    Creates a contact record from an email received via POST.

    """
    if request.method != 'POST':
        return HttpResponse(status=200)

    admin_email = request.REQUEST.get('from')
    headers = request.REQUEST.get('headers')
    key = request.REQUEST.get('key')
    subject = request.REQUEST.get('subject')
    email_text = request.REQUEST.get('text')
    if key != settings.EMAIL_KEY:
        return HttpResponse(status=200)
    if headers:
        parser = HeaderParser()
        headers = parser.parsestr(headers)

    if headers and 'Date' in headers:
        try:
            date_time = get_datetime_from_str(headers.get('Date'))
        except Exception:
            date_time = datetime.now()
    else:
        date_time = datetime.now()

    to = request.REQUEST.get('to', '')
    cc = request.REQUEST.get('cc', '')
    recipient_emails_and_names = getaddresses(["%s, %s" % (to, cc)])
    admin_email = getaddresses([admin_email])[0][1]
    contact_emails = filter(None,
                            [email[1] for email in recipient_emails_and_names])

    if contact_emails == [] or (len(contact_emails) == 1 and
                                contact_emails[0].lower() == 'prm@my.jobs'):
        # If prm@my.jobs is the only contact, assume it's a forward.
        fwd_headers = build_email_dicts(email_text)
        try:
            recipient_emails_and_names = fwd_headers[0]['recipients']
            contact_emails = [recipient[1] for recipient
                              in recipient_emails_and_names]
            date_time = fwd_headers[0]['date']
        except IndexError:
            contact_emails = []

    for element in contact_emails:
        if element.lower() == 'prm@my.jobs':
            contact_emails.remove(element)
            break

    try:
        contact_emails.remove(admin_email)
    except ValueError:
        pass

    admin_user = User.objects.get_email_owner(admin_email)
    if admin_user is None:
        return HttpResponse(status=200)

    partners = list(chain(*[company.partner_set.all()
                            for company in admin_user.company_set.all()]))

    possible_contacts, created_contacts, unmatched_contacts = [], [], []
    for contact in contact_emails:
        try:
            matching_contacts = Contact.objects.filter(email=contact,
                                                       partner__in=partners)
            [possible_contacts.append(x) for x in matching_contacts]
            if not matching_contacts:
                poss_partner = find_partner_from_email(partners, contact)
                if poss_partner:
                    new_contact = Contact.objects.create(name=contact,
                                                         email=contact,
                                                         partner=poss_partner)
                    change_msg = "Contact was created from email."
                    log_change(new_contact, None, admin_user,
                               new_contact.partner,   new_contact.name,
                               action_type=ADDITION, change_msg=change_msg)
                    created_contacts.append(new_contact)
                else:
                    unmatched_contacts.append(contact)
        except ValueError:
            unmatched_contacts.append(contact)

    num_attachments = int(request.POST.get('attachments', 0))
    attachments = []
    for file_number in range(1, num_attachments+1):
        try:
            attachment = request.FILES['attachment%s' % file_number]
        except KeyError:
            error = "There was an issue with the email attachments. The " \
                    "contact records for the email will need to be created " \
                    "manually."
            send_contact_record_email_response([], [], contact_emails, error,
                                               admin_email)
            return HttpResponse(status=200)
        attachments.append(attachment)

    created_records = []
    date_time = datetime.now() if not date_time else date_time
    for contact in possible_contacts + created_contacts:
        change_msg = "Email was sent by %s to %s" % \
                     (admin_user.get_full_name(), contact.name)
        record = ContactRecord.objects.create(partner=contact.partner,
                                              contact_type='email',
                                              contact_name=contact.name,
                                              contact_email=contact.email,
                                              contact_phone=contact.phone,
                                              date_time=date_time,
                                              subject=subject,
                                              notes=force_text(email_text))
        for attachment in attachments:
            prm_attachment = PRMAttachment()
            prm_attachment.attachment = attachment
            prm_attachment.contact_record = record
            setattr(prm_attachment, 'partner', contact.partner)
            prm_attachment.save()
        log_change(record, None, admin_user, contact.partner,  contact.name,
                   action_type=ADDITION, change_msg=change_msg)

        created_records.append(record)

    send_contact_record_email_response(created_records, created_contacts,
                                       unmatched_contacts, None, admin_email)
    return HttpResponse(status=200)
