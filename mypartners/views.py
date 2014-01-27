import json

from django.contrib.auth.decorators import user_passes_test
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

from myjobs.models import User
from mydashboard.models import Company
from mypartners.forms import (PartnerForm, ContactForm, PartnerInitialForm,
                              NewPartnerForm)
from mypartners.models import Partner, Contact
from mypartners.helpers import get_partner


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
        try:
            company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            raise Http404

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

    partner_ct_id = ContentType.objects.get(name="partner").id

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
    company_id = request.REQUEST.get('company')
    try:
        company = Company.objects.filter(id=company_id)\
            .select_related('partner_set')[0]
    except Company.DoesNotExist:
        raise Http404

    user = request.user
    if not user in company.admins.all():
        raise Http404

    partner_id = int(request.REQUEST.get('partner'))
    partner = get_partner(company, partner_id)

    form = PartnerForm(instance=partner, auto_id=False)

    contacts = partner.contacts.all()
    contact_ct_id = ContentType.objects.get(name="contact").id
    partner_ct_id = ContentType.objects.get(name="partner").id

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

    try:
        company = Company.objects.filter(id=company_id)\
            .select_related('partner_set')[0]
    except Company.DoesNotExist:
        raise Http404

    user = request.user
    if not user in company.admins.all():
        raise Http404

    if request.path != "/prm/view/edit":
        try:
            partner_id = int(request.REQUEST.get('partner'))
        except TypeError:
            raise Http404
        partner = get_partner(company, partner_id)
    else:
        partner = None

    try:
        content_id = int(request.REQUEST.get('ct'))
    except TypeError:
        raise Http404
    item_id = request.REQUEST.get('id') or None

    if content_id == ContentType.objects.get(name='partner').id:
        if not item_id:
            form = NewPartnerForm()
    elif content_id == ContentType.objects.get(name='contact').id:
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
    company_id = request.REQUEST.get('company')
    try:
        company = Company.objects.filter(id=company_id)\
            .select_related('partner_set')[0]
    except Company.DoesNotExist:
        raise Http404

    content_id = int(request.REQUEST.get('ct'))

    if content_id == ContentType.objects.get(name='contact').id:
        item_id = request.REQUEST.get('id') or None
        if item_id:
            try:
                partner_id = int(request.REQUEST.get('partner'))
            except TypeError:
                raise Http404

            partner = get_partner(company, partner_id)

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

    if content_id == ContentType.objects.get(name='partner').id:
        try:
            partner_id = int(request.REQUEST.get('partner'))
        except TypeError:
            raise Http404

        partner = get_partner(company, partner_id)
        form = PartnerForm(instance=partner, auto_id=False, data=request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse(status=200)
        else:
            return HttpResponse(json.dumps(form.errors))


@user_passes_test(lambda u: User.objects.is_group_member(u, 'Employer'))
def delete_prm_item(request):
    company_id = request.REQUEST.get('company')
    try:
        company = Company.objects.filter(id=company_id)\
            .select_related('partner_set')[0]
    except Company.DoesNotExist:
        raise Http404

    partner_id = request.REQUEST.get('partner')
    if partner_id:
        partner_id = int(partner_id)
    contact_id = request.REQUEST.get('id')
    if contact_id:
        contact_id = int(contact_id)
    content_id = request.REQUEST.get('ct')
    if content_id:
        content_id = int(content_id)

    if content_id == ContentType.objects.get(name='contact').id:
        contact = get_object_or_404(Contact, id=contact_id)
        contact.delete()
        return HttpResponseRedirect(reverse('partner_details')+'?company=' +
                                    str(company_id)+'&partner=' +
                                    str(partner_id))
    if content_id == ContentType.objects.get(name='partner').id:
        partner = get_object_or_404(Partner, id=partner_id, owner=company)
        partner.contacts.all().delete()
        partner.delete()
        return HttpResponseRedirect(reverse('prm')+'?company='+str(company_id))

