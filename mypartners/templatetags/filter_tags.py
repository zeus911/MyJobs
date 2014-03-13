import datetime

from django.template import Library

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


@register.filter(name='render_datepicker')
def render_datepicker(thing):
    render = SplitDateDropDownWidget().render('datechooser',
                                              datetime.datetime.now())
    return render
