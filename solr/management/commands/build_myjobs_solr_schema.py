from optparse import make_option

from django.core.management.base import BaseCommand
from django.template import loader, Context

from myprofile.models import ProfileUnits
from myjobs.models import User
from mysearches.models import SavedSearch

DEFAULT_FIELD_NAME = 'text'
UNIQUE_FIELD_NAME = 'uid'
DEFAULT_OPERATOR = 'AND'

# Django model field types that map to non-text_en fields
type_mapping = {
    'AutoField': 'long',
    'BooleanField': 'boolean',
    'DateField': 'date',
    'DateTimeField': 'date',
    'ForeignKey': 'long',
    'IntegerField': 'long',
    'ManyToMany': 'long',
}

# Field name endings for dynamic fields
dynamic_type_mapping = {
    'boolean': '_b',
    'date': '_dt',
    'double': '_d',
    'float': '_f',
    'int': '_i',
    'location': '_p',
    'long': '_l',
    'string': '_s',
    'tdouble': '_coordinate',
    'text_en': '_t',
}


class Command(BaseCommand):
    help = 'Builds solr schema from models'

    options = (
        # Default option. Builds schema using static field names.
        make_option("-s", "--static",
                    action='store_true', default=True, dest='static',
                    help='create schema using static fields (default)'),
        # Builds schema using only dynamic field types.
        make_option("-d", "--dynamic",
                    action='store_false', dest='static',
                    help='create schema using dynamic fields'),
    )
    option_list = BaseCommand.option_list + options

    def handle(self, *args, **options):
        models = ProfileUnits.__subclasses__()
        models.append(User)
        models.append(SavedSearch)
        schema_fields = []
        copy_fields = []

        if options['static']:
            # One-off fields
            schema_fields.append({
                'field_name': 'ProfileUnits_user_id',
                'type': 'long',
                'indexed': 'true',
                'stored': 'true',
                'multiValued': 'false',
            })
            schema_fields.append({
                'field_name': 'Address_full_location',
                'type': 'string',
                'indexed': 'true',
                'stored': 'true',
                'multiValued': 'true',
            })
            schema_fields.append({
                'field_name': 'Address_region',
                'type': 'string',
                'indexed': 'true',
                'stored': 'true',
                'multiValued': 'true',
            })
            schema_fields.append({
                'field_name': 'text',
                'type': 'text_en',
                'indexed': 'true',
                'stored': 'false',
                'multiValued': 'true',
            })
            schema_fields.append({
                'field_name': 'SavedSearch_company_id',
                'type': 'long',
                'indexed': 'true',
                'stored': 'true',
                'multiValued': 'false',
            })
            # Analytics
            for field in ['job_view_title', 'job_view_company',
                          'job_view_location']:
                exact_field = field + '_exact'
                field_data = {
                    'field_name': field,
                    'type': 'text_en',
                    'indexed': 'true',
                    'stored': 'true',
                    'multiValued': 'false',
                }
                schema_fields.append(field_data.copy())
                field_data['field_name'] = exact_field
                field_data['type'] = 'string'
                schema_fields.append(field_data)
                copy_fields.append({'source': exact_field, 'dest': field})
            for field in ['aguid', 'domain', 'job_view_canonical_domain',
                          'job_view_guid', 'search_location', 'search_query',
                          'page_category', 'doc_type']:
                # myguid is the same as User_user_guid and will be kept there
                schema_fields.append({
                    'field_name': field,
                    'type': 'string',
                    'indexed': 'true',
                    'stored': 'true',
                    'multiValued': 'false',
                })
            for field in ['view_source', 'job_view_buid', 'company_id']:
                schema_fields.append({
                    'field_name': field,
                    'type': 'long',
                    'indexed': 'true',
                    'stored': 'true',
                    'multiValued': 'false',
                })
            for field in ['search_keywords', 'facets', 'site_tag',
                          'special_commitment']:
                schema_fields.append({
                    'field_name': field,
                    'type': 'string',
                    'indexed': 'true',
                    'stored': 'true',
                    'multiValued': 'true',
                })
            schema_fields.append({
                'field_name': 'view_date',
                'type': 'date',
                'indexed': 'true',
                'stored': 'true',
                'multiValued': 'false',
            })
            for model in models:
                for field in model._meta.fields:
                    field_type = field.get_internal_type()

                    # The OneToOneField fields is useless in every single case
                    # so far.
                    if field_type == 'OneToOneField' or \
                            any(s in field.attname
                                for s in ['password', 'deactivate_type']):
                        continue

                    field_data = {
                        'field_name': "%s_%s" % (model.__name__, field.attname),
                        'type': 'string',
                        'indexed': 'true',
                        'stored': 'true',
                        'multiValued': 'false',
                    }

                    try:
                        field_data['type'] = type_mapping[field_type]
                    except KeyError:
                        # If there's no field in the type_mapping then the
                        # default text_en should work.
                        pass

                    if model in ProfileUnits.__subclasses__():
                        field_data['multiValued'] = 'true'

                    schema_fields.append(field_data)

        context = Context({
            'default_field_name': DEFAULT_FIELD_NAME,
            'unique_field_name': UNIQUE_FIELD_NAME,
            'default_operator': DEFAULT_OPERATOR,
            'fields': schema_fields,
            'copy_fields': copy_fields
        })

        print loader.get_template('solr_schema_base.xml').render(context)




