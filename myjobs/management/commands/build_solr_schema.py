from django.core.management.base import BaseCommand
from django.template import loader, Context

from MyJobs.myprofile.models import ProfileUnits
from MyJobs.myjobs.models import User
from MyJobs.mysearches.models import SavedSearch

DEFAULT_FIELD_NAME = 'uid'
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

class Command(BaseCommand):
    help = 'Builds solr schema from models'

    def handle(self, *args, **options):
        models = ProfileUnits.__subclasses__()
        models.append(User)
        models.append(SavedSearch)
        schema_fields = []

        for model in models:
            for field in model._meta.fields:
                field_type = field.get_internal_type()

                # The OneToOneField fields is useless in every single case
                # so far.
                if type == 'OneToOneField':
                    continue

                field_data = {
                    'field_name': "%s_%s" % (model.__name__, field.attname),
                    'type': 'text_en',
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

                if field_type == "ManyToMany":
                    field_data['multiValued'] = 'true'

                schema_fields.append(field_data)

        context = Context({
            'default_field_name': DEFAULT_FIELD_NAME,
            'unique_field_name': DEFAULT_FIELD_NAME,
            'default_operator': DEFAULT_OPERATOR,
            'fields': schema_fields,
        })

        print loader.get_template('solr_schema_base.xml').render(context)




