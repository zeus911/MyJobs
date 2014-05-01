from django import template
from django.conf import settings
from django.utils.translation import ungettext

register = template.Library()

intword_converters = (
    (3, lambda number: (
        ungettext('%(value).1fk', '%(value).1fk', number),
        ungettext('%(value)sk', '%(value)sk', number),
    )),
    (6, lambda number: (
        ungettext('%(value).1fM', '%(value).1fM', number),
        ungettext('%(value)sM', '%(value)sM', number),
    )),
    (9, lambda number: (
        ungettext('%(value).1fB', '%(value).1fB', number),
        ungettext('%(value)sB', '%(value)sB', number),
    )),
    (12, lambda number: (
        ungettext('%(value).1fT', '%(value).1fT', number),
        ungettext('%(value)sT', '%(value)sT', number),
    )),
    (15, lambda number: (
        ungettext('%(value).1fQd', '%(value).1fQd', number),
        ungettext('%(value)sQd', '%(value)sQd', number),
    )),
    (18, lambda number: (
        ungettext('%(value).1fQt', '%(value).1fQt', number),
        ungettext('%(value)sQt', '%(value)sQt', number),
    )),
    (21, lambda number: (
        ungettext('%(value).1fSx', '%(value).1fSx', number),
        ungettext('%(value)sSx', '%(value)sSx', number),
    )),
    (24, lambda number: (
        ungettext('%(value).1fSp', '%(value).1fSp', number),
        ungettext('%(value)sSp', '%(value)sSp', number),
    )),
    (27, lambda number: (
        ungettext('%(value).1fO', '%(value).1fO', number),
        ungettext('%(value)sO', '%(value)sO', number),
    )),
    (30, lambda number: (
        ungettext('%(value).1fN', '%(value).1fN', number),
        ungettext('%(value)sN', '%(value)sN', number),
    )),
    (33, lambda number: (
        ungettext('%(value).1fD', '%(value).1fD', number),
        ungettext('%(value)sD', '%(value)sD', number),
    )),
    (100, lambda number: (
        ungettext('%(value).1fG', '%(value).1fG', number),
        ungettext('%(value)sG', '%(value)sG', number),
    )),
)


@register.filter(is_safe=True)
def intabbr(value):
    """
    Shortens large input values (>1k) to use their abbreviated SI prefixes
    (1,000,000 -> 1.0M, 9,500 -> 9.5k, etc)
    """
    try:
        value = int(value)
    except (TypeError, ValueError):
        return value

    if value < 1000:
        return value

    def _i18n(value, float_formatted, string_formatted):
        if settings.USE_L10N:
            value = int(value * 10) / 10.0
            value_template = string_formatted
        else:
            value_template = float_formatted
        return value_template % {'value': value}

    for exponent, converters in intword_converters:
        test_number = 10 ** exponent
        if value < test_number * 1000:
            new_value = value / float(test_number)
            return _i18n(new_value, *converters(new_value))
    return value
