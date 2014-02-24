from django.template import Library
from django.utils.encoding import force_text

from mypartners.helpers import get_attachment_link

register = Library()


@register.inclusion_tag('mypartners/activity.html')
def get_activity_block(activity):
    activity_types = {
        1: 'added',
        2: 'updated',
        3: 'deleted',
    }

    user_name = activity.user.get_full_name()
    return {
        'activity': activity,
        'action_type': activity_types[activity.action_flag],
        'content_type': force_text(activity.content_type),
        'activity_object': activity.get_edited_object(),
        'user_name': user_name,
    }

@register.inclusion_tag('mypartners/records.html')
def get_record_block(records, company, partner):
    return {
        'records': records,
        'company': company,
        'partner': partner,
    }

@register.simple_tag
def attachment_link(attachment, partner, company):
    name = attachment.attachment.name.split("/")[-1]
    return get_attachment_link(company.id, partner.id, attachment.id, name)
