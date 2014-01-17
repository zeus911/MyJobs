from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, post_delete

from MyJobs.myjobs.models import User
from MyJobs.solr.management.commands.build_solr_schema import (type_mapping,
                                                               dynamic_type_mapping)
from MyJobs.myprofile.models import ProfileUnits
from MyJobs.mysearches.models import SavedSearch
from MyJobs.solr.models import Update


def prepare_add_to_solr(sender, instance, **kwargs):
    """
    Converts an object instance into a dictionary and adds it to solr.

    inputs:
    :sender: the model of the object being added to solr
    :instance: the object being added to solr

    """
    solr_dict = object_to_dict(sender, instance)

    obj, _ = Update.objects.get_or_create(uid=solr_dict['uid'])
    obj.solr_dict = solr_dict
    obj.delete = False
    obj.save()


def prepare_delete_from_solr(sender, instance, **kwargs):
    """
    Removes and object instance from solr.

    inputs:
    :sender: the model of the object being removed from solr
    :instance: the object being removed from solr

    """
    content_type_id = ContentType.objects.get_for_model(sender).pk
    object_id = instance.pk
    solr_dict = {'uid': "%s#%s" % (content_type_id, object_id)}

    obj, _ = Update.get_or_create(uid=solr_dict['uid'])
    obj.solr_dict = solr_dict
    obj.delete = True
    obj.save()


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
        field_type = field.get_internal_type()
        if field_type != 'OneToOneField' and 'password' not in field.attname:
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
        if field_type != 'OneToOneField' and 'password' not in field.attname:
            try:
                mapped_field = dynamic_type_mapping[type_mapping[field_type]]
            except KeyError:
                mapped_field = '_t'

            field_name = "%s_%s%s" % (model.__name__, field.attname,
                                      mapped_field)
            solr_dict[field_name] = getattr(obj, field.attname)
    return solr_dict


post_save.connect(prepare_add_to_solr, sender=User,
                  dispatch_uid="user")
post_delete.connect(prepare_delete_from_solr, sender=User,
                    dispatch_uid='user')

post_save.connect(prepare_add_to_solr, sender=ProfileUnits,
                  dispatch_uid="profileunits")
post_delete.connect(prepare_delete_from_solr, sender=ProfileUnits,
                    dispatch_uid='profileunits')

post_save.connect(prepare_add_to_solr, sender=SavedSearch,
                  dispatch_uid='savedsearch')
post_delete.connect(prepare_delete_from_solr, sender=SavedSearch,
                    dispatch_uid='savedsearch')
