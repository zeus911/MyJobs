from django.http import Http404


def get_partner(company, partner_id):
    company_partners = company.partner_set.all()
    try:
        partner = [partner for partner in company_partners
                   if partner.id == partner_id][0]
    except:
        raise Http404
    return partner
