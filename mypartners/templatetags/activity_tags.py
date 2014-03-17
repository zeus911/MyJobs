import bleach

from django.template import Library
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe

from mypartners.helpers import get_attachment_link
from mypartners.models import CONTACT_TYPE_CHOICES, ACTIVITY_TYPES

register = Library()


@register.inclusion_tag('mypartners/activity.html')
def get_activity_block(activity):
    if activity.user:
        user_name = activity.user.get_full_name()
    else:
        user_name = ''
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


@register.filter
def bleach_clean(string):
    """
    Cleans a string of all html tags, attributes, and sytles except those
    specified and marks it safe to display as html.

    """
    tags = ['br', 'a']
    attrs = {
        'a': ['href'],
    }
    style = []

    # strip = True means the tags are stripped from the result
    # rather than being included as escaped characters.
    return mark_safe(bleach.clean(string, tags, attrs, style, strip=True))


@register.filter
def strip_tags(string):
    return mark_safe(bleach.clean(string, strip=True))