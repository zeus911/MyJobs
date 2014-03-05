from django.template import Library
from django.utils.encoding import force_text

from mypartners.helpers import get_attachment_link
from mypartners.models import CONTACT_TYPE_CHOICES

register = Library()


ACTIVITY_TYPES = {
    1: 'added',
    2: 'updated',
    3: 'deleted',
}

@register.inclusion_tag('mypartners/activity.html')
def get_activity_block(activity):
    user_name = activity.user.get_full_name()
    return {
        'activity': activity,
        'action_type': ACTIVITY_TYPES[activity.action_flag],
        'content_type': force_text(activity.content_type),
        'activity_object': activity.get_edited_object(),
        'user_name': user_name,
    }

@register.inclusion_tag('mypartners/records.html', takes_context=True)
def get_record_block(context, records, company, partner):
    date_start = context.get('date_start')
    date_end = context.get('date_end')

    if date_start:
        pass
    if date_end:
        pass

    return {
        'date_start': date_start,
        'date_end': date_end,
        'records': records,
        'company': company,
        'partner': partner,
    }

@register.simple_tag
def attachment_link(attachment, partner, company):
    name = attachment.attachment.name.split("/")[-1]
    return get_attachment_link(company.id, partner.id, attachment.id, name)


@register.simple_tag
def get_action_type(activity):
    action_type = ACTIVITY_TYPES[activity.action_flag]
    return action_type.title()

@register.simple_tag
def get_contact_type(record):
    contact_type_choices = dict(CONTACT_TYPE_CHOICES)
    return contact_type_choices[record.contact_type]