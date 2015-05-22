from collections import OrderedDict
import re

from django.core.exceptions import ObjectDoesNotExist
from django.db import models, IntegrityError


ERROR = -1
NOT_STARTED = 0
SAVED = 1
COMPLETE = 2

SAVED_STATES = [SAVED, COMPLETE, ERROR]
COMPLETE_STATES = [COMPLETE, ERROR]


def add_to_queue(queue_object, queue):
    """
    Inserts an object and all important related information
    into the queue. Overwrites any existing information.

    :param queue_object: The object that needs inserted into the queue.
    :param queue: The queue the object is being inserted into.

    :return: The queue with the object inserted.
    """
    queue_key = object_to_key(queue_object)
    queue[queue_key] = {
        'error': None,
        'foreign_keys': get_foreign_key_objects(queue_object),
        'many_to_manys': get_many_to_many_objects(queue_object),
        'null_foreign_keys': get_foreign_key_objects(queue_object, null=True),
        'new_object': None,
        'object': queue_object,
        'status': NOT_STARTED
    }
    return queue


def build_object_kwargs(obj, queue, include_null=False):
    """
    Builds all the kwargs required to create a copy of an object.

    :param obj: The object the kwargs are being built for
    :param queue: The creation queue.
    :param include_null: True if non-required foreign keys and many-to-many
                         relationships should be included.

    :return: A dictionary of kwargs required to create a copy of obj.

    """
    kwargs = {}

    for field in obj._meta.local_fields:

        if hasattr(field, 'through'):
            # It's a many-to-many. Discard it, since this shouldn't
            # be handled until after the object is fully created.
            continue

        elif isinstance(field, models.ForeignKey):
            # If we're not including nullable foreign keys and we've
            # come to a nullable foreign key ignore the field.
            if not include_null and (field.null or field.blank):
                continue

            fk_object = get_foreign_key_object_for_field(obj, field)
            if fk_object:
                new_fk_object = get_new_object(fk_object, queue)
                if not new_fk_object:
                    # This point should never be reached. All associated
                    # foreign key objects should be made before
                    # we actually attempt to create the object
                    # itself.
                    raise ObjectDoesNotExist('The foreign key %s was not '
                                             'already created when attempting '
                                             'to create object %s.'
                                             % (fk_object, obj))
                kwargs[field.name] = new_fk_object
        else:
            kwargs[field.attname] = getattr(obj, field.attname)

    kwargs['pk'] = obj.pk

    return kwargs


def copy_following_relationships(queryset, copy_to='qc-redirect'):
    """
    Copies all of the objects and all objects related to those objects
    from the default database to the copy_to database.

    :param queryset: A queryset of objects to be copied.
    :param copy_to: The database the queryset is being copied to.

    :return: The ordered queue dictionary containing the existing objects,
             the newly created objects, and any errors that happened
             during the process.

    """
    return create_in_order(copy_to, populate_queue(queryset))


def create_in_order(copy_to, queue):
    """
    Creates all the objects based on the order of the queue.

    :param copy_to: The database the objects are being copied to.
    :param queue: An ordered dictionary of dictionaries, where the dictionries
                  are mapped to the object. The expected format of the
                  dictionary can be found in add_to_queue()

    :return: An updated queue with all the new objects created and/or
             relevant errors recorded.

    """
    index = len(queue.items()) - 1

    # Create all the objects with only the non-relationship fields and
    # required foreign keys.
    while [item for item in queue.items() if item[1]['status'] not in SAVED_STATES]:
        obj = queue.items()[index][1]['object']
        key = object_to_key(obj)

        can_save = True
        for fk in queue[key]['foreign_keys']:
            fk_key = object_to_key(fk)
            fk_dict = queue[fk_key]

            if fk_dict['status'] == ERROR:
                queue[fk_key]['error'] = ("Cannot save because of related "
                                          "error:", fk_dict['error'])
                queue[fk_key]['status'] = ERROR
            elif not fk_dict['new_object'] or fk_dict['status'] == NOT_STARTED:
                can_save = False

        if can_save:
            queue = save_object(copy_to, obj, queue)

        index -= 1
        if index < 0:
            index = len(queue.items()) - 1

    # Resave all objects with the extra "unnecessary" relationships
    # (i.e. nullable foreign keys and many-to-manys)
    for queue_entry in queue.values():
        obj = queue_entry['object']

        # At this point we've saved every object at least once,
        # so we don't have to check if we can save like we did last time.
        queue = full_save_object(copy_to, obj, queue)

    return queue


def create_new_object(copy_to, base_model, **kwargs):
    """
    Saves a new object to the specified database.

    :param copy_to: The database the object should be saved to.
    :param model: The model for the object.
    :param kwargs: The relevant kwargs for the object.

    :return: The new object

    """
    try:
        return base_model.objects.using(copy_to).create(**kwargs)
    except IntegrityError, e:
        duplicate = find_duplicate_object(copy_to, base_model, e, **kwargs)
        return update_existing_object(copy_to, duplicate, **kwargs)


def find_duplicate_object(database, base_model, integrity_error, **kwargs):
    """
    Given an integrity error, attempts to find the claimed duplicate.

    :param database: The database that has the duplicate.
    :param base_model: The model for the duplicate.
    :param integrity_error: The received IntegrityError.

    :return: The duplicate if found. Otherwise it raises another
             IntegrityError.

    """
    pattern = "Duplicate entry '(?P<value>.*)' for key '(?P<key>.*)'"
    pattern = re.compile(pattern)

    try:
        value, key = pattern.findall(integrity_error.args[1])[0]
        value = kwargs.get(key)
        obj = base_model.objects.using(database).get(**{key: value})
        return obj
    except IndexError, e:
        raise IntegrityError('A duplicate entry for an object of type %s '
                             ' was found. The copier was unable to '
                             'de-duplicate the object.' % base_model)


def get_foreign_keys(obj, null=False):
    """
    Gets a list of foreign key fields on an object.

    :param obj: The object you want foreign keys for.
    :param null: True if you want only foreign keys where null=True in the
                 model definition. False if you only want foreign keys
                 where null=False in the model definition.

    :return: A list of fields that are foreign keys on obj.

    """
    fields = obj._meta.local_fields

    return [field for field in fields
            if isinstance(field, models.ForeignKey) and (field.null == null or
                                                         field.blank == null)]


def get_foreign_key_objects(obj, null=False):
    """
    Gets a list of objects that a specified object has a foreign key to.

    :param obj: The object you want the foreign keys for.
    :param null: True if you want to consider only foreign keys where
                 null=True in the model definition. False if you only want
                 foreign keys where null=False in the model definition.

    :return: A list of fields objects that obj has a foreign key to.

    """
    objects = []

    for fk_field in get_foreign_keys(obj, null=null):
        objects.append(get_foreign_key_object_for_field(obj, fk_field))

    return [obj for obj in objects if obj]


def get_foreign_key_object_for_field(obj, field):
    """
    Gets the related object for a given foreign key field.

    :param obj: The object that you want the foreign key from.
    :param field: The field the objects are related on.

    :return: The related object.

    """
    return getattr(obj, field.name)


def get_many_to_many(obj):
    """
    Gets a list of all many-to-many fields.

    :param obj: The object you want all the many-to-many fields for.

    :return: A list of fields.

    """
    return obj._meta.local_many_to_many


def get_many_to_many_objects(obj):
    """
    Gets all of the objects that a specified object has a many-to-many
    relationship to.

    :param obj: The object you want all the related many-to-many objects for.

    :return: A list of objects that obj has a many-to-many relationship to.

    """
    objects = []
    for m2m_field in get_many_to_many(obj):
        m2m_field = getattr(obj, m2m_field.attname)
        if hasattr(m2m_field, 'add'):
            objects += list(m2m_field.all())
        else:
            # The field is related through an explicitly defined
            # through table, so we have to create the through
            # object in addition to the related object.
            query = {m2m_field.source_field_name: obj}
            objects += list(m2m_field.through.objects.filter(**query))
    return objects


def get_many_to_many_objects_for_field(obj, field):
    """
    Gets the related objects for a given many-to-many field.

    :param obj: The object that you want the related many-to-many objects
                from.
    :param field: The field the objects are related on.

    :return: All related objects for that fields.

    """
    field = getattr(obj, field.attname)
    if hasattr(field, 'add'):
        return field.all()
    else:
        # The field is related through an explicitly defined
        # through table, so we have to create the through
        # object in addition to the related object.
        query = {field.source_field_name: obj}
        return field.through.objects.filter(**query)


def get_new_object(obj, queue):
    """
    Gets the new/copied object from the queue for a given object.

    :param obj:  The object you want the copied object for.

    :return: The copied object.

    """
    key = object_to_key(obj)
    queue_entry = queue[key]
    return queue_entry['new_object']


def get_or_create_object(copy_to, obj, queue, include_null=False):
    """
    Adds or updates an object from the default database to a new database.

    :param copy_to: The location the object is being copied or added to
    :param obj: The object being added/updated.
    :param queue: The creation queue.
    :param include_null: True if you also want to copy objects in non-required
                         relationships and False otherwise. This should
                         never be set to True unless you know all
                         related objects have been created.

    :return: The newly created object.

    """

    kwargs = build_object_kwargs(obj, queue, include_null=include_null)
    model = obj.__class__
    try:
        new_obj = model.objects.using(copy_to).get(pk=obj.pk)
    except model.DoesNotExist:
        new_obj = None

    if new_obj:
        new_obj = update_existing_object(copy_to, new_obj, **kwargs)
    else:
        new_obj = create_new_object(copy_to, model, **kwargs)

    return new_obj


def full_save_object(copy_to, obj, queue):
    """
    Saves an object with all relationships included. This should never
    be run unless all releated objects have already been created.

    :param copy_to: The database you are copying the object too.
    :param obj: The object being copied.
    :param queue: The creation queue.

    :return: The creation queue updated with the new object
             and new status.

    """
    key = object_to_key(obj)
    try:
        queue[key]['new_object'] = get_or_create_object(copy_to, obj, queue,
                                                        include_null=True)
        new_obj = queue[key]['new_object']

        # Finally ensure that appropriate many-to-many relationships
        # exist now that we know the object is otherwise completely created.
        for field in get_many_to_many(obj):
            m2m_objects = get_many_to_many_objects_for_field(obj, field)
            if hasattr(getattr(obj, field.name), 'add'):
                for m2m_object in m2m_objects:
                    new_m2m_object = get_new_object(m2m_object, queue)
                    if new_m2m_object:
                        relation_manager = getattr(new_obj, field.name)
                        relation_manager.add(new_m2m_object)

        # Resave with the new m2m relationships intact.
        queue[key]['new_object'] = get_or_create_object(copy_to, obj, queue,
                                                        include_null=True)

        queue[key]['status'] = COMPLETE
    except Exception, e:
        queue[key]['status'] = ERROR
        queue[key]['error'] = e

    return queue


def object_to_key(obj):
    """
    Creates the queue key for an object.

    :param obj: A database model instance.
    :return: The key representing that object's entry in the queue dictionary.
    """

    module = "%s.%s" % (obj.__module__,
                        obj.__class__.__name__)
    return module, obj.pk


def populate_queue(queryset):
    """
    Adds everything in the queryset and all related objects to the queue
    in an attempted order.

    :param queryset: A queryset of objects that you're attempting to copy.

    :return: A creation queue with all the items added. The queue items
             follow the format defined in add_to_queue().
    """

    queue = OrderedDict({})
    for obj in queryset:
        queue = add_to_queue(obj, queue)

    index = 0
    while index < len(queue.items()):
        obj = queue.items()[index][1]['object']

        for fk_field in get_foreign_keys(obj):
            fk = get_foreign_key_object_for_field(obj, fk_field)
            if fk:
                queue = add_to_queue(fk, queue)

        for fk_field in get_foreign_keys(obj, null=True):
            fk = get_foreign_key_object_for_field(obj, fk_field)
            if fk:
                queue = add_to_queue(fk, queue)

        m2m_objects = get_many_to_many_objects(obj)

        for m2m in m2m_objects:
            queue = add_to_queue(m2m, queue)

        index += 1

    return queue


def save_object(copy_to, obj, queue):
    """
    Saves an object only necessary foreign key relationships included.
    This should never be run unless all required foreign key objects have
    already been created.

    :param copy_to: The database you are copying the object too.
    :param obj: The object being copied.
    :param queue: The creation queue.

    :return: The creation queue updated with the new object
             and new status.

    """
    key = object_to_key(obj)

    try:
        queue[key]['new_object'] = get_or_create_object(copy_to, obj, queue)
        queue[key]['status'] = SAVED
    except Exception, e:
        queue[key]['status'] = ERROR
        queue[key]['error'] = e
        return queue

    # If there aren't additional foreign keys or many-to-manys that need
    # added we can mark the object as completed now.
    if not queue[key]['null_foreign_keys'] and not queue[key]['many_to_manys']:
        queue[key]['status'] = COMPLETE

    return queue


def update_existing_object(copy_to, obj, **kwargs):
    """
    Overwrites an existing object on a specified database with data.
    Doesn't use update to ensure any related signals are triggered.

    :param copy_to: The database the object should be saved to.
    :param obj: The existing object from the copy_to database.
    :param kwargs: The relevant kwargs for the object.

    :return: The new object

    """
    for key, value in kwargs.items():
        setattr(obj, key, value)

    try:
        obj.save(using=copy_to)
    except IntegrityError, e:
        duplicate = find_duplicate_object(copy_to, obj.__class__, e, **kwargs)
        kwargs['pk'] = duplicate.pk
        kwargs['id'] = duplicate.id
        return update_existing_object(copy_to, duplicate, **kwargs)

    return obj