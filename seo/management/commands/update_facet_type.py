from django.core.management.base import BaseCommand 
from seo.models import SeoSiteFacet

class Command(BaseCommand):
    help = "Sets facet type based on is_default field."

    def handle(self, *args, **options):
        for facet in SeoSiteFacet.objects.all():
            if facet.is_default:
                facet.facet_type = SeoSiteFacet.DEFAULT
            else:
                facet.facet_type = SeoSiteFacet.STANDARD
            facet.save()
