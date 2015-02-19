from BeautifulSoup import BeautifulSoup
from django.core.management.base import NoArgsCommand
import re
from seo.models import Company
import urllib

class Command(NoArgsCommand):
    args = 'None'
    help = 'Checks for the existence of member logos on the content server'

    def handle_noargs(self, **options):
        # Create a list of logo file names from the Company.logo_url attribute
        # e.g. '//d2e48ltfsb5exy.cloudfront.net/100x50/seo/foo.gif' --> 'foo.gif'
        in_db = [co.logo_url.split("/")[-1] for co 
                 in Company.objects.filter(member=True)]

        # Instead of checking each logo individually, find the difference
        # between the two sets.
        server = urllib.urlopen('//d2e48ltfsb5exy.cloudfront.net/100x50/seo/')
        soup = BeautifulSoup(server.read())

        on_server = [x['href'] for x in soup.findAll(href=re.compile('.*\.gif'))]

        missing_logos = list(set(in_db) - set(on_server))
        missing_logos.sort()

        print "{0} member logo urls in the database".format(len(in_db))
        print "Missing {0} logos".format(len(missing_logos))

        # print 25 logo filenames
        for logo in missing_logos[:25]:
            print logo
