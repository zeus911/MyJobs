import json

from django.contrib.auth.decorators import user_passes_test
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

from myjobs.models import User
from mydashboard.models import Company
from mysearches.models import PartnerSavedSearch
from mysearches.forms import PartnerSavedSearchForm
from mypartners.forms import (PartnerForm, ContactForm, PartnerInitialForm,
                              NewPartnerForm)
from mypartners.models import Partner, Contact
from mypartners.helpers import prm_worthy


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
    cred = prm_worthy(request)

    form = PartnerForm(instance=cred['partner'], auto_id=False)

    contacts = cred['partner'].contacts.all()
    contact_ct_id = ContentType.objects.get_for_model(Contact).id
    partner_ct_id = ContentType.objects.get_for_model(Partner).id

    ctx = {'company': cred['company'],
           'form': form,
           'contacts': contacts,
           'partner': cred['partner'],
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
        form.save()
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
                    form.save()
                    return HttpResponse(status=200)
                else:
                    return HttpResponse(json.dumps(form.errors))
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
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
            form.save()
            return HttpResponse(status=200)
        else:
            return HttpResponse(json.dumps(form.errors))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def delete_prm_item(request):
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
        contact = get_object_or_404(Contact, id=contact_id)
        contact.delete()
        return HttpResponseRedirect(reverse('partner_details')+'?company=' +
                                    str(company_id)+'&partner=' +
                                    str(partner_id))
    if content_id == ContentType.objects.get_for_model(Partner).id:
        partner = get_object_or_404(Partner, id=partner_id, owner=company)
        partner.contacts.all().delete()
        partner.delete()
        return HttpResponseRedirect(reverse('prm')+'?company='+str(company_id))
    
    
@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def prm_overview(request):
    cred = prm_worthy(request)

    most_recent_activity = []
    most_recent_communication = []
    most_recent_saved_searches = []

    ctx = {'partner': cred['partner'],
           'company': cred['company'],
           'recent_activity': most_recent_activity,
           'recent_communication': most_recent_communication,
           'recent_ss': most_recent_saved_searches}

    return render_to_response('mypartners/overview.html', ctx,
                              RequestContext(request))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def prm_saved_searches(request):
    cred = prm_worthy(request)
    saved_searches = PartnerSavedSearch.objects.filter(provider=
                                                       cred['company'].id)
    ctx = {'searches': saved_searches,
           'company': cred['company'],
           'partner': cred['partner']}
    return render_to_response('mypartners/partner_searches.html', ctx,
                              RequestContext(request))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def prm_new_saved_search(request):
    cred = prm_worthy(request)
    form = PartnerSavedSearchForm(partner=cred['partner'])
    ctx = {'company': cred['company'],
           'partner': cred['partner'],
           'form': form}
    return render_to_response('mypartners/partner_new_search.html', ctx,
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
    cred = prm_worthy(request)
    item_id = request.REQUEST.get('id')

    if item_id:
        item = get_object_or_404(PartnerSavedSearch, id=item_id,
                                 provider=cred['company'].id)
        form = PartnerSavedSearchForm(instance=item, auto_id=False,
                                      data=request.POST,
                                      partner=cred['partner'])
        if form.is_valid():
            form.save()
            return HttpResponse(status=200)
        else:
            return HttpResponse(json.dumps(form.errors))
    form = PartnerSavedSearchForm(request.POST, partner=cred['partner'])
    if form.is_valid():
        form.save()
        return HttpResponse(status=200)
    else:
        return HttpResponse(json.dumps(form.errors))
