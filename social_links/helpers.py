from django.conf import settings


def get_microsite_carousel(site_id):
    mc = settings.SITE.microsite_carousel
    if mc is None or not mc.is_active:
        mc = None
    return mc

def create_carousel_cycle_string(mc):
    num_rows = mc.display_rows
    empty_string = []
    for number in range(num_rows-1):
        empty_string.append('')
    cycle_string = (empty_string + ['</ul><ul>'] + empty_string + ['</ul><ul>']
                    + empty_string + ['</ul></div><div><ul>'])
    return cycle_string
