from django.template import loader, Library

register = Library()

@register.filter(name='widget_template')
def widget_template(widget_name):
    """
    Checks to see if there is a widget template for the given name of
    widget_name. If there is return the template.

    Inputs:
    :widget_name:    String of widget's name.

    Outputs:
                Custom template location if exists otherwise returns None for
                boolean check reasons.
    """
    widget_name = widget_name.replace(" ", "")
    try:
        loaded = loader.get_template('mydashboard/widgets/%s.html' % widget_name)
        if loaded:
            return 'mydashboard/widgets/%s.html' % widget_name
    except loader.TemplateDoesNotExist:
        return None