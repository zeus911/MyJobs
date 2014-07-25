from django.core.management.base import BaseCommand, CommandError

from mypartners import models
from mypartners import ofccp

def booleanize(value):
    if value.lower() == 'y':
        return True
    elif value.lower() == 'n':
        return False
    else:
        return value

class Command(BaseCommand):
    help = "Update OFCCP Contacts"

    def handle(self, *args, **kwargs):
        for contact in ofccp.get_contacts():
            contact = dict((key, booleanize(value)) 
                           for key, value in contact._asdict().iteritems())
            record = models.OFCCPContact(*contact)
            record.save()

        print len(list(models.OFCCPContact.objects.all()))
                
