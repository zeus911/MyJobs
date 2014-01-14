import pysolr

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, post_delete

from myjobs.models import User
from myjobs.management.commands.build_solr_schema import (type_mapping,
                                                          dynamic_type_mapping)
from MyJobs.tasks import add_to_solr_task, delete_from_solr_task
from myprofile.models import (Name, Education, Address, Telephone,
                              EmploymentHistory, MilitaryService, Website,
                              License, Summary, VolunteerHistory)
from mysearches.models import SavedSearch


def add_to_solr(sender, instance):
    """
    Converts an object instance into a dictionary and adds it to solr.

    inputs:
    :sender: the model of the object being added to solr
    :instance: the object being added to solr

    """
    solr_dict = object_to_dict(sender, instance)

    solr = pysolr.Solr(settings.SOLR_LOCATION)
    solr.add([solr_dict])


def delete_from_solr(sender, instance):
    """
    Removes and object instance from solr.

    inputs:
    :sender: the model of the object being removed from solr
    :instance: the object being removed from solr

    """
    content_type_id = ContentType.objects.get_for_model(sender).pk
    object_id = instance.pk
    uid = "%s#%s" % (content_type_id, object_id)

    solr = pysolr.Solr(settings.SOLR_LOCATION)
    solr.delete(q='uid:%s' % uid)


def object_to_dict(model, obj):
    """
    Turns an object into a solr compatible dictionary.

    inputs:
    :model: the model for the object
    :object: object being converted into a solr dictionary

    """
    content_type_id = ContentType.objects.get_for_model(model).pk
    object_id = obj.pk
    solr_dict = {'uid': "%s#%s" % (content_type_id, object_id)}

    for field in model._meta._fields():
        if field.get_internal_type() != 'OneToOneField':
            field_name = "%s_%s" % (model.__name__, field.attname)
            solr_dict[field_name] = getattr(obj, field.attname)
    return solr_dict


def object_to_dict_with_dynamic_fields(model, obj):
    """
    Turns an object into a solr compatible dictionary, taking advantage of
    dynamicFields.

    inputs:
    :model: the model for the object
    :object: object being converted into a solr dictionary

    """
    content_type_id = ContentType.objects.get_for_model(model).pk
    object_id = obj.pk
    solr_dict = {'uid': "%s#%s" % (content_type_id, object_id)}

    for field in model._meta._fields():
        field_type = field.get_internal_type()
        if field_type != 'OneToOneField':
            try:
                mapped_field = dynamic_type_mapping[type_mapping[field_type]]
            except KeyError:
                mapped_field = '_t'

            field_name = "%s_%s%s" % (model.__name__, field.attname,
                                      mapped_field)
            solr_dict[field_name] = getattr(obj, field.attname)
    return solr_dict


# These two functions filter out unneccessary information before calling the
# celery task. Skipping this step will cause the task to fail because the
# signals contain a lock that can't be pickled by celery.
def trigger_add(sender, instance, **kwargs):
    add_to_solr_task.delay(sender, instance)


def trigger_delete(sender, instance, **kwargs):
    delete_from_solr_task.delay(sender, instance)


post_save.connect(trigger_add, sender=User,
                  dispatch_uid="user")
post_delete.connect(trigger_delete, sender=User,
                    dispatch_uid='user')

post_save.connect(trigger_add, sender=Name,
                  dispatch_uid='name')
post_delete.connect(trigger_delete, sender=Name,
                    dispatch_uid='name')

post_save.connect(trigger_add, sender=Education,
                  dispatch_uid='education')
post_delete.connect(trigger_delete, sender=Education,
                    dispatch_uid='education')

post_save.connect(trigger_add, sender=Address,
                  dispatch_uid='address')
post_delete.connect(trigger_delete, sender=Address,
                    dispatch_uid='address')

post_save.connect(trigger_add, sender=Telephone,
                  dispatch_uid='telephone')
post_delete.connect(trigger_delete, sender=Telephone,
                    dispatch_uid='telephone')

post_save.connect(trigger_add, sender=EmploymentHistory,
                  dispatch_uid='employmenthistory')
post_delete.connect(trigger_delete, sender=EmploymentHistory,
                    dispatch_uid='employmenthistory')

post_save.connect(trigger_add, sender=MilitaryService,
                  dispatch_uid='militaryservice')
post_delete.connect(trigger_delete, sender=MilitaryService,
                    dispatch_uid='militaryservice')

post_save.connect(trigger_add, sender=Website,
                  dispatch_uid='website')
post_delete.connect(trigger_delete, sender=Website,
                    dispatch_uid='website')

post_save.connect(trigger_add, sender=License,
                  dispatch_uid='license')
post_delete.connect(trigger_delete, sender=License,
                    dispatch_uid='license')

post_save.connect(trigger_add, sender=Summary,
                  dispatch_uid='summary')
post_delete.connect(trigger_delete, sender=Summary,
                    dispatch_uid='summary')

post_save.connect(trigger_add, sender=VolunteerHistory,
                  dispatch_uid='volunteerhistory')
post_delete.connect(trigger_delete, sender=VolunteerHistory,
                    dispatch_uid='volunteerhistory')

post_save.connect(trigger_add, sender=SavedSearch,
                  dispatch_uid='savedsearch')
post_delete.connect(trigger_delete, sender=SavedSearch,
                    dispatch_uid='savedsearch')