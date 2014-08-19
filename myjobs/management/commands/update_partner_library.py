# TODO:
#   * proper logging
#   * check for succesful record insertion without hitting the database
#   * command line options
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from tasks import update_partner_library


class Command(BaseCommand):
    help = "Update PartnerLibrary Model"
    option_list = BaseCommand.option_list + (
        make_option(
            '--quiet' ,'-q', action='store_true',
            dest='quiet',
            help='Supress output'),
        )

    def add_arguments(self, parser):
        parser.add_argument(
            'path', type=str, default=None,
             help='Location of an HTML file to parse for OFCCP data')

    def handle(self, *args, **options):
        quiet = options.pop('quiet', False)
        path = None
        if args:
            path = args[0]

        update_partner_library(path, quiet=quiet)
