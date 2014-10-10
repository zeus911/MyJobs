import pytz

from django.template import Library
from django.utils.timezone import get_current_timezone_name, now

from mypartners.widgets import SplitDateDropDownWidget

register = Library()

@register.filter(name='get_admins')
def get_admins(company):
    company_admins = company.admins.all()
    admins = []
    for admin in company_admins:
        info = {}
        name = admin.get_full_name()
        if name:
            info['name'] = name
        else:
            info['name'] = admin.email
        info['id'] = admin.id
        admins.append(info)
    return admins


@register.simple_tag
def render_datepicker(name='datechooser', date=None):
    date = date or now()
    user_tz = pytz.timezone(get_current_timezone_name())
    date = date.astimezone(user_tz)
    return SplitDateDropDownWidget().render(name, date)
