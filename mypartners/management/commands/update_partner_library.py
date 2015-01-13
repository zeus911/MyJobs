from django.core.management.base import BaseCommand
from tasks import update_partner_library


class Command(BaseCommand):
    help = "Update PartnerLibrary model."

    def handle(self, *args, **options):
        update_partner_library()
