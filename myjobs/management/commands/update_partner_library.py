# TODO: 
#   * proper logging
#   * check for succesful record insertion without hitting the database
#   * command line options
from django.core.management.base import BaseCommand, CommandError

from mypartners.models import PartnerLibrary
from mypartners.helpers import get_library_partners

class Command(BaseCommand):
    help = "Update PartnerLibrary Model"

    def handle(self, *args, **kwargs):
        contacts = get_library_partners(from_html=True)

        for contact in contacts:
            if not PartnerLibrary.objects.filter(email=contact.email_id,
                                                 st=contact.st,
                                                 city=contact.city):
                PartnerLibrary(
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
                    is_veteran=contact.veteran).save()

                #TODO: see if there is a way to do this without querying the
                #      database
                if PartnerLibrary.objects.filter(email=contact.email_id):
                    print "Successfully added %s %s (%s) from %s, %s." % (
                        contact.first_name, contact.last_name,
                        contact.email_id, contact.city, contact.st)
            else:
                print  "%s %s (%s) from %s, %s already exists, skipping.." % (
                    contact.first_name, contact.last_name, contact.email_id,
                    contact.city, contact.st)
