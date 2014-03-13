from django.template import Library

from mypartners.helpers import contact_record_val_to_str


register = Library()

@register.simple_tag
def get_human_readable_field_name(field):
    return field.replace("_", " ").title()

@register.assignment_tag
def get_attr(record, field):
    return contact_record_val_to_str(getattr(record, field, ''))