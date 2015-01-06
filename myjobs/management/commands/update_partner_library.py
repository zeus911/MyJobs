# TODO:
#   * proper logging
#   * check for succesful record insertion without hitting the database
#   * command line options
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from tasks import update_partner_library


class Command(BaseCommand):
    help = "Update PartnerLibrary model."

    def handle(self, *args, **options):
        update_partner_library()
