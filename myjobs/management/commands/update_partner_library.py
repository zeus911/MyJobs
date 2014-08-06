# TODO:
#   * proper logging
#   * check for succesful record insertion without hitting the database
#   * command line options
from django.core.management.base import BaseCommand, CommandError
from tasks import update_partner_library


class Command(BaseCommand):
    help = "Update PartnerLibrary Model"

    def handle(self, *args, **kwargs):
        update_partner_library()
