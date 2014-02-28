import json

from django.conf import settings
from django.contrib.admin.models import DELETION
from django.contrib.auth.decorators import user_passes_test
from django.contrib.contenttypes.models import ContentType
from django.core.files.storage import default_storage
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

from myjobs.models import User
from mydashboard.models import Company
from mysearches.models import SavedSearch, PartnerSavedSearch
from mysearches.helpers import url_sort_options, parse_rss
from mysearches.forms import PartnerSavedSearchForm
from mypartners.forms import (PartnerForm, ContactForm, PartnerInitialForm,
                              NewPartnerForm, ContactRecordForm)
from mypartners.models import (Partner, Contact, ContactRecord, PRMAttachment,
                               ContactLogEntry, CONTACT_TYPE_CHOICES)
from mypartners.helpers import (prm_worthy, add_extra_params,
                                add_extra_params_to_jobs, log_change,
                                get_searches_for_partner, get_logs_for_partner,
                                get_contact_records_for_partner)

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
        has_partners = False
        if not form:
            partner_form = PartnerInitialForm()
        partners = []
    else:
        try:
            partners = Partner.objects.filter(owner=company.id)
        except Partner.DoesNotExist:
            raise Http404
        has_partners = True
        partner_form = None

    partner_ct_id = ContentType.objects.get_for_model(Partner).id

    ctx = {'has_partners': has_partners,
           'partners': partners,
           'form': partner_form or form,
           'company': company,
           'user': user,
           'partner_ct': partner_ct_id}

    return render_to_response('mypartners/prm.html', ctx,
                              RequestContext(request))

@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def partner_details(request):
    company, partner, user = prm_worthy(request)

    form = PartnerForm(instance=partner, auto_id=False)

    contacts = partner.contacts.all()
    contact_ct_id = ContentType.objects.get_for_model(Contact).id
    partner_ct_id = ContentType.objects.get_for_model(Partner).id

    ctx = {'company': company,
           'form': form,
           'contacts': contacts,
           'partner': partner,
           'contact_ct': contact_ct_id,
           'partner_ct': partner_ct_id}
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
    elif content_id == ContentType.objects.get_for_model(Contact).id:
        if not item_id:
            form = ContactForm()
        else:
            try:
                item = partner.contacts.get(pk=item_id)
            except:
                raise Http404
            form = ContactForm(instance=item, auto_id=False)
    else:
        raise Http404

    ctx = {'form': form,
           'partner': partner,
           'company': company,
           'contact': item_id,
           'content_id': content_id}

    return render_to_response('mypartners/edit_item.html', ctx,
                              RequestContext(request))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def save_init_partner_form(request):
    company_id = request.REQUEST.get('company_id')
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
        if item_id:
            try:
                partner_id = int(request.REQUEST.get('partner'))
            except TypeError:
                raise Http404

            partner = get_object_or_404(company.partner_set.all(),
                                        id=partner_id)

            try:
                item = partner.contacts.get(pk=item_id)
            except:
                raise Http404
            else:
                form = ContactForm(instance=item, auto_id=False,
                                   data=request.POST)
                if form.is_valid():
                    form.save(request.user)
                    return HttpResponse(status=200)
                else:
                    return HttpResponse(json.dumps(form.errors))
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save(request.user)
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
    if partner_id:
        partner_id = int(partner_id)
    contact_id = request.REQUEST.get('id')
    if contact_id:
        contact_id = int(contact_id)
    content_id = request.REQUEST.get('ct')
    if content_id:
        content_id = int(content_id)

    if content_id == ContentType.objects.get_for_model(Contact).id:
        partner = get_object_or_404(Partner, id=partner_id, owner=company)
        contact = get_object_or_404(Contact, id=contact_id)
        log_change(contact, None, request.user, partner, contact.name,
                   action_type=DELETION)
        contact.delete()
        return HttpResponseRedirect(reverse('partner_details')+'?company=' +
                                    str(company_id)+'&partner=' +
                                    str(partner_id))
    if content_id == ContentType.objects.get_for_model(Partner).id:
        partner = get_object_or_404(Partner, id=partner_id, owner=company)
        partner.contacts.all().delete()
        log_change(partner, None, request.user, partner, partner.name,
                   action_type=DELETION)
        partner.delete()
        return HttpResponseRedirect(reverse('prm')+'?company='+str(company_id))
    
    
@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def prm_overview(request):
    """
    View that is the "Overview" of one's Partner Activity.

    """
    company, partner, user = prm_worthy(request)

    most_recent_activity = get_logs_for_partner(partner)
    communication = get_contact_records_for_partner(partner)
    most_recent_communication = communication[:3]
    saved_searches = get_searches_for_partner(partner)
    most_recent_saved_searches = saved_searches[:3]


    ctx = {'partner': partner,
           'company': company,
           'recent_activity': most_recent_activity,
           'recent_communication': most_recent_communication,
           'recent_ss': most_recent_saved_searches}

    return render_to_response('mypartners/overview.html', ctx,
                              RequestContext(request))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def prm_saved_searches(request):
    """
    View that lists the Partner's Saved Searches

    """
    company, partner, user = prm_worthy(request)
    saved_searches = get_searches_for_partner(partner)
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
    ctx = {'company': company,
           'partner': partner,
           'item_id': item_id,
           'form': form}
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
        try:
            instance.user = User.objects.get(email=instance.email)
        except User.DoesNotExist:
            user = User.objects.create_inactive_user(
                email=instance.email,
                custom_msg=instance.account_activation_message)
            instance.user = user[0]
            Contact.objects.filter(email=instance.email).update(user=instance.user)
        instance.feed = form.data['feed']
        instance.provider = company
        instance.created_by = request.user
        instance.custom_message = instance.partner_message
        form.save()
        return HttpResponse(status=200)
    else:
        return HttpResponse(json.dumps(form.errors))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def partner_view_full_feed(request):
    """
    PSSs' feed

    """
    company, partner, user = prm_worthy(request)
    search_id = request.REQUEST.get('id')
    saved_search = SavedSearch.objects.get(id=search_id)

    if hasattr(saved_search, 'partnersavedsearch'):
        is_pss = True
        if company == saved_search.partnersavedsearch.provider:
            url_of_feed = url_sort_options(saved_search.feed,
                                           saved_search.sort_by,
                                           saved_search.frequency)
            items = parse_rss(url_of_feed, saved_search.frequency)
            extras = saved_search.partnersavedsearch.url_extras
            if extras:
                add_extra_params_to_jobs(items, extras)
                saved_search.url = add_extra_params(saved_search.url, extras)
        else:
            return HttpResponseRedirect(reverse('prm_saved_searches'))
    else:
        return HttpResponseRedirect(reverse('prm_saved_searches'))
    return render_to_response('mysearches/view_full_feed.html',
                              {'search': saved_search,
                               'items': items,
                               'view_name': 'Saved Searches',
                               'is_pss': is_pss,
                               'partner': partner.id,
                               'company': company.id},
                              RequestContext(request))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def prm_records(request):
    company, partner, user = prm_worthy(request)
    contact_records = get_contact_records_for_partner(partner)
    most_recent_activity = get_logs_for_partner(partner)

    contact_type_choices = [('all', 'All')] + list(CONTACT_TYPE_CHOICES)
    contacts = ContactRecord.objects.values('contact_name').distinct()
    contact_choices = [('all', 'All')]
    [contact_choices.append((c['contact_name'], c['contact_name']))
     for c in contacts]

    ctx = {
        'company': company,
        'partner': partner,
        'records': contact_records,
        'most_recent_activity': most_recent_activity,
        'contact_choices': contact_choices,
        'contact_type_choices': contact_type_choices,
    }
    return render_to_response('mypartners/main_records.html', ctx,
                              RequestContext(request))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def prm_edit_records(request):
    company, partner, user = prm_worthy(request)
    record_id = request.GET.get('id', None)
    ctx = {
        'company': company,
        'partner': partner,
    }

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
                '?company=%d&partner=%d' % (company.id, partner.id))
        else:
            ctx['form'] = form
    else:
        if record_id:
            try:
                instance = ContactRecord.objects.get(pk=record_id)
            except ContactRecord.DoesNotExist:
                instance = None
            form = ContactRecordForm(partner=partner, instance=instance)
        else:
            form = ContactRecordForm(partner=partner)
        ctx['form'] = form

    return render_to_response('mypartners/edit_record.html', ctx,
                              RequestContext(request))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def prm_view_records(request):
    company, partner, user = prm_worthy(request)
    record_id = request.GET.get('id', None)
    offset = request.GET.get('offset', 0)
    record_type = request.GET.get('type', None)
    name = request.GET.get('name', None)

    try:
        record_id = int(record_id)
        offset = int(offset)
    except (TypeError, ValueError):
        return HttpResponseRedirect(reverse('partner_records') +
                '?company=%d&partner=%d' % (company.id, partner.id))

    prev_offset = (offset - 1) if offset > 1 else 0
    records = get_contact_records_for_partner(partner, record_type=record_type,
                                              contact_name=name,
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
    else:
        prev_id = None
        record = records[0]
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

    }

    return render_to_response('mypartners/view_record.html', ctx,
                              RequestContext(request))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def get_contact_information(request):
    company, partner, user = prm_worthy(request)
    contact_id = request.REQUEST.get('contact_name')
    try:
        contact = Contact.objects.get(pk=contact_id)
    except Contact.DoesNotExist:
        data = {'error': 'Contact does not exist'}
        return HttpResponse(json.dumps(data))

    if partner not in contact.partners_set.all():
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
    company, partner, user = prm_worthy(request)
    contact = request.REQUEST.get('contact')
    contact_type = request.REQUEST.get('contact_type')

    contact = None if contact == 'all' else contact
    contact_type = None if contact_type == 'all' else contact_type

    ctx = {
        'records': get_contact_records_for_partner(partner,
                                                   contact_name=contact,
                                                   record_type=contact_type),
        'company': company,
        'partner': partner,
        'contact_type': contact_type,
        'contact_name': contact,
    }
    return render_to_response('mypartners/records.html', ctx,
                              RequestContext(request))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def get_uploaded_file(request):
    company, partner, user = prm_worthy(request)
    file_id = request.GET.get('id', None)
    attachment = get_object_or_404(PRMAttachment, pk=file_id,
                                   contact_record__partner=partner)
    try:
        if default_storage.connection.__repr__() == 'S3Connection:s3.amazonaws.com':
            from boto.s3.connection import S3Connection

            s3 = S3Connection(settings.AWS_ACCESS_KEY_ID,
                              settings.AWS_SECRET_KEY, is_secure=True)
            path = s3.generate_url(600, 'GET', bucket=settings.AWS_STORAGE_BUCKET_NAME,
                                   key=attachment.attachment.name,
                                   force_http=True)
        else:
            path = "%s%s" % (settings.MEDIA_URL, attachment.attachment.name)
    except AttributeError:
        path = "%s%s" % (settings.MEDIA_URL, attachment.attachment.name)

    return HttpResponseRedirect(path)


def partner_get_records(request):
    company, partner, user = prm_worthy(request)
    retrieve_type = request.GET.get('type')
    if retrieve_type == 'sample':
        records = get_contact_records_for_partner(partner, filter_day=30)\
            .exclude(contact_type='job')
        email = records.filter(contact_type='email').count()
        phone = records.filter(contact_type='phone').count()
        facetoface = records.filter(contact_type='facetoface').count()
        data = {'totalrecs': records.count(),
                'email': email,
                'phone': phone,
                'facetoface': facetoface}
        return HttpResponse(json.dumps(data))
