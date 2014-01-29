from django.shortcuts import get_object_or_404
from django.http import Http404

from mydashboard.models import Company


def prm_worthy(request):
    """
    Makes sure the User is worthy enough to use PRM.

    Do you have enough cred?
    """
    company_id = request.REQUEST.get('company')
    company = get_object_or_404(Company, id=company_id)

    user = request.user
    if not user in company.admins.all():
        raise Http404

    partner_id = int(request.REQUEST.get('partner'))
    partner = get_object_or_404(company.partner_set.all(), id=partner_id)

    cred = {'comany_id': company_id,
            'company': company,
            'user': user,
            'partner_id': partner_id,
            'partner': partner}

    return cred
