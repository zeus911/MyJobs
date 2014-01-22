from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save, post_delete

from MyJobs.myjobs.models import User
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
    if sender in ProfileUnits.__subclasses__():
        content_type_id = ContentType.objects.get_for_model(ProfileUnits).pk
        object_id = instance.user_id
    else:
        content_type_id = ContentType.objects.get_for_model(sender).pk
        object_id = instance.pk
    uid = "%s#%s" % (content_type_id, object_id)

    obj, _ = Update.objects.get_or_create(uid=uid)
    obj.delete = False
    obj.save()


def prepare_delete_from_solr(sender, instance, **kwargs):
    """
    Removes and object instance from solr.

    inputs:
    :sender: the model of the object being removed from solr
    :instance: the object being removed from solr

    """
    if sender in ProfileUnits.__subclasses__():
        content_type_id = ContentType.objects.get_for_model(ProfileUnits).pk
        object_id = instance.user_id
    else:
        content_type_id = ContentType.objects.get_for_model(sender).pk
        object_id = instance.pk
    uid = "%s#%s" % (content_type_id, object_id)

    obj, _ = Update.objects.get_or_create(uid=uid)
    obj.delete = True
    obj.save()


def profileunits_to_dict(user_id):
    """
    Creates a dictionary of profile units for a user.

    inputs:
    :user_id: the id of the user the dictionary is being created for

    """
    content_type_id = ContentType.objects.get_for_model(ProfileUnits).pk
    solr_dict = {
        'uid': "%s#%s" % (content_type_id, user_id),
        'ProfileUnits_user_id': user_id,
    }
    models = {}

    units = ProfileUnits.objects.filter(user_id=user_id).select_related('name',
                                                                        'education',
                                                                        'website',
                                                                        'telephone',
                                                                        'address',
                                                                        'secondaryemail',
                                                                        'militaryservice',
                                                                        'license',
                                                                        'summary',
                                                                        'employmenthistory',
                                                                        'volunteerhistory',
                                                                        'content_type')
    try:
        for unit in units:
            unit = getattr(unit, unit.get_model_name())
            models.setdefault(unit.__class__.__name__, []).append(unit)

        for model_name, objs in models.items():
            if not objs:
                continue

            for field in objs[0]._meta._fields():
                obj_list = [getattr(obj, field.attname) for obj in objs]
                field_type = field.get_internal_type()
                if field_type != 'OneToOneField' and 'password' not in field.attname:
                    field_name = "%s_%s" % (model_name, field.attname)
                    solr_dict[field_name] = filter(None, list(obj_list))
    except Exception:
        pass

    return solr_dict


def object_to_dict(model, obj):
    """
    Turns an object into a solr compatible dictionary.

    inputs:
    :model: the model for the object
    :object: object being converted into a solr dictionary

    """
    content_type_id = ContentType.objects.get_for_model(model).pk
    object_id = obj.pk
    solr_dict = {
        'uid': "%s#%s" % (content_type_id, object_id),
    }

    if model == SavedSearch:
        for field in User._meta._fields():
            field_type = field.get_internal_type()
            if field_type != 'OneToOneField' and 'password' not in field.attname:
                field_name = "User_%s" % field.attname
                solr_dict[field_name] = getattr(obj.user, field.attname)

    for field in model._meta._fields():
        field_type = field.get_internal_type()
        if field_type != 'OneToOneField' and 'password' not in field.attname:
            field_name = "%s_%s" % (model.__name__, field.attname)
            solr_dict[field_name] = getattr(obj, field.attname)
    return solr_dict


post_save.connect(prepare_add_to_solr, sender=User,
                  dispatch_uid="user")
post_delete.connect(prepare_delete_from_solr, sender=User,
                    dispatch_uid='user')

post_save.connect(prepare_add_to_solr, sender=SavedSearch,
                  dispatch_uid='savedsearch')
post_delete.connect(prepare_delete_from_solr, sender=SavedSearch,
                    dispatch_uid='savedsearch')

for model_class in ProfileUnits.__subclasses__():
    post_save.connect(prepare_add_to_solr,
                      sender=model_class,
                      dispatch_uid="att_post_save_"+model_class.__name__)
    post_delete.connect(prepare_delete_from_solr,
                      sender=model_class,
                      dispatch_uid="att_post_save_"+model_class.__name__)