from django.core.management.base import BaseCommand, CommandError

from mypartners.models import OFCCPContact
from mypartners import ofccp

class Command(BaseCommand):
    help = "Update OFCCP Contacts"

    def handle(self, *args, **kwargs):
        contacts = ofccp.get_contacts()

        for contact in contacts:
            if not OFCCPContact.objects.filter(email=contact.email_id,
                                               st=contact.st,
                                               city=contact.city):
                OFCCPContact(
                    organization=contact.organization_name,
                    website=contact.website,
                    region=contact.region,
                    state=contact.state,
                    area=contact.area,
                    title=contact.title,
                    first_name=contact.first_name,
                    middle_name=contact.middle_name,
                    last_name=contact.last_name,
                    phone=contact.phone,
                    phone_ext=contact.phone_ext,
                    alt_phone=contact.alt_phone,
                    fax=contact.fax,
                    email=contact.email_id,
                    street1=contact.street1,
                    street2=contact.street2,
                    city=contact.city,
                    st=contact.st,
                    zip_code=contact.zip_code,
                    is_minority=contact.minority,
                    is_female=contact.female,
                    is_disabled=contact.disabled,
                    is_veteran=contact.veteran,
                    is_exec_om=contact.exec_om,
                    is_first_om=contact.first_om,
                    is_professional=contact.professional,
                    is_technician=contact.technician,
                    is_sales=contact.sales,
                    is_admin_support=contact.admin_support,
                    is_craft=contact.craft,
                    is_operative=contact.operative,
                    is_labor=contact.labor,
                    is_service=contact.service).save()
