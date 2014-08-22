from seo.cache import get_site_config


def site_config_context(request):
    return {'site_config': get_site_config(request)}
