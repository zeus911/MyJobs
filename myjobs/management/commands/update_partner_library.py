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
        print "Connecting to OFCCP directory..."
        for partner in get_library_partners():
            if not PartnerLibrary.objects.filter(email=partner.email_id,
                                                 st=partner.st,
                                                 city=partner.city):

                contact_name = " ".join(" ".join([partner.first_name,
                                                 partner.middle_name,
                                                 partner.last_name]).split())
                PartnerLibrary(
                    name=partner.organization_name,
                    uri=partner.website,
                    region=partner.region,
                    state=partner.state,
                    area=partner.area,
                    contact_name=contact_name,
                    phone=partner.phone,
                    phone_ext=partner.phone_ext,
                    alt_phone=partner.alt_phone,
                    fax=partner.fax,
                    email=partner.email_id,
                    street1=partner.street1,
                    street2=partner.street2,
                    city=partner.city,
                    st=partner.st,
                    zip_code=partner.zip_code,
                    is_minority=partner.minority,
                    is_female=partner.female,
                    is_disabled=partner.disabled,
                    is_disabled_veteran=partner.disabled_veteran,
                    is_veteran=partner.veteran).save()

                #TODO: see if there is a way to do this without querying the
                #      database
                if PartnerLibrary.objects.filter(email=partner.email_id):
                    print "Successfully added %s %s (%s) from %s, %s." % (
                        partner.first_name, partner.last_name,
                        partner.email_id, partner.city, partner.st)
            else:
                print  "%s %s (%s) from %s, %s already exists, skipping.." % (
                    partner.first_name, partner.last_name, partner.email_id,
                    partner.city, partner.st)
