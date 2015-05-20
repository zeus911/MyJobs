from collections import OrderedDict

from django.core.exceptions import ObjectDoesNotExist
from django.db import models

ERROR = -1
NOT_STARTED = 0
SAVED = 1
COMPLETE = 2


def add_to_queue(queue_object, queue):
    """
    Inserts an object and all important related information
    into the queue. Overwrites any existing information.

    :param queue_object: The object that needs inserted into the queue.
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
    kwargs = {}

    for field in obj._meta.local_fields:
        if isinstance(field, models.ForeignKey) and field.null == include_null:
            fk_object = get_foreign_key_object_for_field(obj, field)
            if fk_object:
                fk_queue_key = object_to_key(fk_object)
                fk_queue_entry = queue[fk_queue_key]
                new_fk_object = fk_queue_entry['new_object']
                if not new_fk_object:
                    # This point should never be reached. All associated
                    # foreign key objects should be made before
                    # we actually attempt to create the object
                    # itself.
                    raise ObjectDoesNotExist('The foreign key %s was not '
                                             'already created when attempting '
                                             'to create object %s.'
                                             % fk_object, obj)

        elif not isinstance(field, models.ForeignKey):
            kwargs[field.attname] = getattr(obj, field.attname)

    kwargs['pk'] = obj.pk

    return kwargs


def copy_following_relationships(queryset, copy_to='qc-redirect'):
    queue = populate_queue(queryset)
    queue = create_in_order(copy_to, queue)
    return queue


def create_in_order(copy_to, queue):
    iterator = len(queue.items()) - 1
    done_states = [COMPLETE, ERROR]

    while [item for item in queue.items() if item[1]['status'] not in done_states]:
        obj = queue.items()[iterator][1]['object']
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
            queue = full_save_object(copy_to, obj, queue)

        iterator -= 1
        if iterator < 0:
            iterator = len(queue.items()) - 1

    return queue


def create_new_object(copy_to, model, **kwargs):
    new_obj = model(**kwargs)
    new_obj.save(using=copy_to)
    print new_obj.pk, model
    return new_obj


def get_foreign_keys(obj, null=False):
    fields = obj._meta.local_fields

    return [field for field in fields
            if isinstance(field, models.ForeignKey) and field.null == null]


def get_foreign_key_objects(obj, null=False):
    objects = []

    for fk_field in get_foreign_keys(obj, null=null):
        objects.append(get_foreign_key_object_for_field(obj, fk_field))

    return objects


def get_foreign_key_object_for_field(obj, field):
    return getattr(obj, field.name)


def get_many_to_many(obj):
    return obj._meta.local_many_to_many


def get_many_to_many_objects(obj):
    objects = []
    for m2m_field in get_many_to_many(obj):
        m2m_field = getattr(obj, m2m_field.attname)
        if hasattr(m2m_field, 'through'):
            # The field is related through an explicitly defined
            # through table, so we have to create the through
            # object in addition to the related object.
            query = {m2m_field.source_field_name: obj}
            objects += list(m2m_field.through.objects.filter(**query))

        else:
            objects += list(m2m_field.all())
    return objects


def get_many_to_many_objects_for_field(obj, field):
    field = getattr(obj, field.attname)
    if hasattr(field, 'through'):
        # The field is related through an explicitly defined
        # through table, so we have to create the through
        # object in addition to the related object.
        query = {field.source_field_name: obj}
        return field.through.objects.filter(**query)

    else:
        return field.all()


def get_or_create_object(copy_to, obj, queue, include_null=False):
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
    key = object_to_key(obj)

    queue[key]['new_object'] = get_or_create_object(copy_to, obj, queue,
                                                    include_null=False)
    queue[key]['status'] = COMPLETE

    return queue


def object_to_key(obj):
    """
    Creates the queue key for an object.

    :param obj: A database model instance.
    :return: The key representing that object for the dictionary queue.
    """

    module = "%s.%s" % (obj.__module__,
                        obj.__class__.__name__)
    return module, obj.pk


def populate_queue(queryset):
    queue = OrderedDict({})
    for obj in queryset:
        queue = add_to_queue(obj, queue)

    iterator = 0
    while iterator < len(queue.items()):
        obj = queue.items()[iterator][1]['object']

        for fk_field in get_foreign_keys(obj):
            fk = get_foreign_key_object_for_field(obj, fk_field)
            if fk:
                queue = add_to_queue(fk, queue)

            m2m_objects = get_many_to_many_objects(obj)

            for m2m in m2m_objects:
                queue = add_to_queue(m2m, queue)

        iterator += 1

    return queue


def save_object(copy_to, obj, queue):
    key = object_to_key(obj)

    queue[key]['new_object'] = get_or_create_object(copy_to, obj, queue)
    queue[key]['status'] = SAVED

    return queue


def update_existing_object(copy_to, obj, **kwargs):
    for key, value in kwargs.items():
        setattr(obj, key, value)

    obj.save(using=copy_to)

    return obj