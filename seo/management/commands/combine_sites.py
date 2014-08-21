from django.core.management.base import BaseCommand

from seo.models import SeoSite, SeoSiteFacet, SeoSiteRedirect

location_group_ids = [511, 491]

occupation_group_ids = [553]

configuration_ids = [3281]#Combo Domain Default

group_id = 621 

base_site_id = 2972

view_source_id = 88

excluded_site_ids = ["1409",
                     "1420",
                     "1421",
                     "1516",
                     "1513",
                     "1514",
                     "1517",
                     "1518",
                     "1519",
                     "1512",
                     "1520",
                     "1521",
                     "1510",
                     "1341",
                     "1511",
                     "1515",
                     "2820"]

def get_site_info(site):
    info['name'] = site_a.domain.rstrip('.jobs')

def create_site_facet(site_facet, site):
    """
    Creates a copy of site_facet with boolean_operation switched to 'and', and
    seosite switched to site. Saves the modified facet
    
    """
    new_site_facet = SeoSiteFacet(seosite=site, customfacet =
            site_facet.customfacet, facet_type = 'DFT', boolean_operation =
            'and')
    new_site_facet.save()

class Command(BaseCommand):
    """
    Creates new domains that are a combination of two different groups and a
    base site configuration, currently location groups, occupation groups, and
    a base site indianahotel.jobs. For instance, akron.jobs and management.jobs 
    would be combine to make akronmanagement.jobs.  This can be refactored to
    be a more general script if we decide to continue building these combo domains.

    """
    def handle(self, *args, **options):
        location_sites = SeoSite.objects.filter(group__id__in =
                location_group_ids).exclude(id__in=excluded_site_ids)
        occupation_sites = SeoSite.objects.filter(group__id__in =
               occupation_group_ids).exclude(id__in=excluded_site_ids)
        combo_site = SeoSite.objects.get(id = base_site_id)
        configurations = combo_site.configurations.all()
        group = combo_site.group
        view_sources = combo_site.view_sources
        site_file = open('created_combo_sites.txt', 'w+')
        for site_a in location_sites:
            domain_a = site_a.domain.rstrip('.jobs')
            name_a = site_a.name.rstrip(' Jobs')
            #Don't check a location combo if there are no redirects starting with that location
            if not SeoSiteRedirect.objects.filter(
                    redirect_url__startswith=domain_a).exists():
                continue
            for site_b in occupation_sites:
                combo_site.pk = None
                combo_site.id = None
                domain_b = site_b.domain.rstrip('.jobs')
                combo_site.domain = domain_a + domain_b + '.jobs'
                print "Checking " + combo_site.domain
                if SeoSite.objects.filter(domain=combo_site.domain).exists() or not\
                    SeoSiteRedirect.objects.filter(redirect_url=combo_site.domain).exists():
                        continue 
                name_b = site_b.name.rstrip(' Jobs')
                combo_site.name = name_a + ' ' + name_b + ' Jobs' 
                combo_site.site_title = combo_site.name
                combo_site.site_heading = name_a + name_b + ' Jobs' 
                combo_site.save()
                combo_site.business_units =\
                    site_a.business_units.all() | site_b.business_units.all()
                for facet in site_a.seositefacet_set.filter(facet_type = 'DFT'):
                   create_site_facet(facet, combo_site)
                for facet in site_b.seositefacet_set.filter(facet_type = 'DFT'):
                   create_site_facet(facet, combo_site)
                combo_site.configurations = configurations 
                combo_site.group = group
                combo_site.view_sources = view_sources
                site_file.write(combo_site.domain + '\n')
        site_file.close()
