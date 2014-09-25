from django import template
from django.contrib.admin import site
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse, NoReverseMatch

from seo.models import Company, GoogleAnalytics, SeoSite, Configuration, \
    BusinessUnit
from social_links.models import SocialLink

register = template.Library()


@register.filter
def get_common_tasks(apps, request):
    """
    Groups common admin tasks into their own grouping on the admin index

    Inputs:
    :apps: List of apps to be displayed on the admin

    Outputs:
    :common_group: List of commonly-used apps

    Modified:
    :apps: Input :apps: with :common_group: and empty sections removed
        (e.g. Groups will not be in this list. Since Groups is the only
        displayed app in the Auth section, Auth will also not be displayed)
    """
    # This is the order that models will appear in the custom group
    common_task_models = [Group, SeoSite, Configuration, BusinessUnit,
                          SocialLink, GoogleAnalytics, Company]
    # model._meta.verbose_name_plural will be a unicode string (if we have set
    # the name) or a <django.utils.functional._proxy__ object ...>; calling a
    # string method on it gives us the actual name of the model
    common_tasks = [model._meta.verbose_name_plural.title()
                    for model in common_task_models]
    common_group = [None] * len(common_tasks)
    # apps is a list of dictionaries, one entry per app (Auth, Seo, Moc_Coding)
    for app in apps[::]:
        # This (and the inner for) mutate the original lists; iterate on copies

        # The model key of an app dictionary is another list of dictionaries,
        # one per model in the app (Seo app contains Companies, Seo Sites, etc)
        for model in app['models'][::]:
            # As with model._meta.verbose_name_plural earlier, this can be
            # unicode or a _proxy__ object.
            model['name'] = model['name'].title()
            if model['name'] in common_tasks:
                # This is a commonly-used model. Add it to the common group
                # and then remove it from the app it was originally in
                common_group[common_tasks.index(
                    model['name'])] = model
                app['models'].remove(model)
        if len(app['models']) == 0:
            # Remove empty apps from the original app list
            apps.remove(app)

    user = request.user
    while None in common_group:
        # We're on a specific app's admin page that does not contain some of
        # our common task models. We must add them manually.
        index = common_group.index(None)
        model = common_task_models[index]
        common_group[index] = {'name': common_tasks[index]}
        if user.has_module_perms(model._meta.app_label):
            # The current user does have permissions for this model
            common_group[index] = {'name': common_tasks[index]}
            model_content_type = ContentType.objects.get_for_model(model)
            url_info = (model_content_type.app_label,
                        model_content_type.model)
            _, admin = [(admin_model, admin)
                        for admin_model, admin in site._registry.items()
                        if admin_model == model][0]
            perms = admin.get_model_perms(request)
            # Only add change/add url if the current user has permission to
            # do those actions
            if perms.get('change', False):
                try:
                    common_group[index]['admin_url'] = \
                        reverse('admin:%s_%s_changelist' % url_info)
                except NoReverseMatch:
                    pass
            if perms.get('add', False):
                try:
                    common_group[index]['add_url'] = reverse('admin:%s_%s_add' %
                                                             url_info)
                except NoReverseMatch:
                    pass
        else:
            common_group[index] = False
    common_group = [item for item in common_group if item]

    return common_group
