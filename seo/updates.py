import logging

from json import dumps

from django.http import HttpResponse
from django.conf import settings

from seo.models import BusinessUnit, SeoSite, CustomFacet, Company


log = logging.getLogger('views')


def update_businessunit(request):
    """
    Copies an old business unit to a new business unit.

    """
    key = request.GET.get('key', None)

    if settings.BUID_API_KEY != key:
        data = {
            'error': 'Unauthorized',
        }
        data = dumps(data)
        return HttpResponse(data, content_type='application/json', status=401)

    try:
        old_buid = int(request.GET.get('old_buid', None))
    except (ValueError, TypeError):
        data = {
            'error': 'Invalid format for old business unit.',
        }
        data = dumps(data)
        return HttpResponse(data, content_type='application/json', status=400)
    try:
        new_buid = int(request.GET.get('new_buid', None))
    except (ValueError, TypeError):
        data = {
            'error': 'Invalid format for new business unit.',
        }
        data = dumps(data)
        return HttpResponse(data, content_type='application/json', status=400)

    if BusinessUnit.objects.filter(id=new_buid):
        data = {
            'error': 'New business unit already exists.'
        }
        data = dumps(data)
        return HttpResponse(data, content_type='application/json', status=400)

    try:
        old_bu = BusinessUnit.objects.get(id=old_buid)
    except BusinessUnit.DoesNotExist:
        data = {
            'error': 'Old business unit does not exist.'
        }
        data = dumps(data)
        return HttpResponse(data, content_type='application/json', status=400)

    custom_careers = old_bu.customcareers.all()

    new_bu = old_bu
    new_bu.pk = new_buid
    new_bu.save()

    new_bu.customcareers = custom_careers
    new_bu.company_set = Company.objects.filter(job_source_ids=old_buid)
    new_bu.seosite_set = SeoSite.objects.filter(business_units=old_buid)
    new_bu.customfacet_set = CustomFacet.objects.filter(business_units=old_buid)

    new_bu.enable_markdown = True

    new_bu.save()
    data = {
        'new_bu': str(new_bu.id),
        'sites': ", ".join(new_bu.seosite_set.all().values_list('domain',
                                                                flat=True)),
    }
    data = dumps(data)

    log.info("BUID %s updated to %s" % (old_buid, new_buid))

    return HttpResponse(data, content_type='application/json')