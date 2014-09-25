import itertools

from django.core.cache import cache
from django.conf import settings
from django.db.models import Q
from social_links.models import SocialLink
from social_links.helpers import (get_microsite_carousel,
                                  create_carousel_cycle_string)

def social_links_context(request):
    cache_key = '%s:social_links' % request.get_host()
    timeout = 60 * settings.MINUTES_TO_CACHE
    social_links_cache = cache.get(cache_key)
    
    if not social_links_cache:
        social_links = {'company':[], 'social':[], 'directemployers':[]}
        slinks = SocialLink.objects.filter(sites=settings.SITE_ID)
        default = SocialLink.objects.filter(group__name='SEO Test Group')
        slinks = itertools.chain(slinks, default)
        for slink in sorted(slinks, 
                            key=lambda x:getattr(x, 'link_title')):
            social_links[slink.link_type].append(slink)
        carousel = get_microsite_carousel(settings.SITE_ID)
        
        if carousel:
            cyclestr = create_carousel_cycle_string(carousel)
        else:
            cyclestr = None

        social_links_cache = {
            'social_links': social_links,
            'carousel': carousel,
            'carousel_cycle_string': cyclestr
        }
                  
        cache.set(cache_key, social_links_cache, timeout)

    return social_links_cache

