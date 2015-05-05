from collections import OrderedDict

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
        'foreign_keys': [],
        'many_to_manys': [],
        'new_object': None,
        'object': queue_object,
        'status': NOT_STARTED
    }
    return queue


def copy_following_relationships(queryset, copy_to='qc-redirect'):
    queue = populate_queue(queryset)
    queue = create_in_order(queue)


def get_foreign_keys(obj):
    fields = obj._meta.local_fields

    return [field for field in fields if isinstance(field, models.ForeignKey)]


def get_foreign_key_object_for_field(obj, field):
    return getattr(obj, field.name)


def get_many_to_many(obj):
    return obj._meta.local_many_to_many


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


def full_save_object(obj, queue):
    key = object_to_key(obj)

    queue[key]['new_object'] = obj
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

        for m2m_field in get_many_to_many(obj):
            m2m_field = getattr(obj, m2m_field.attname)
            if hasattr(m2m_field, 'through'):
                # The field is related through an explicitly defined
                # through table, so we have to create the through
                # object in addition to the related object.
                query = {m2m_field.source_field_name: obj}
                m2m_objects = m2m_field.through.objects.filter(**query)

            else:
                m2m_objects = m2m_field.all()

            for m2m in m2m_objects:
                queue = add_to_queue(m2m, queue)

        iterator += 1

    return queue


def create_in_order(queue):
    iterator = len(queue.items()) - 1
    done_states = [COMPLETE, ERROR]
    while [item for item in queue.items() if item[1]['status'] not in done_states]:
        obj = queue.items()[iterator][1]['object']
        key = object_to_key(obj)

        can_save = True
        for fk in queue[key]['foreign_keys']:
            key = object_to_key(fk)
            fk_dict = queue[key]
            if fk_dict['status'] == ERROR:
                queue[key]['error'] = ("Cannot save because of related "
                                       "error:", fk_dict['error'])
                queue[key]['status'] = ERROR
            elif not fk_dict['new_object'] or fk_dict['status'] == NOT_STARTED:
                can_save = False

        if can_save:
            queue = save_object(obj, queue)
            queue = full_save_object(obj, queue)

        iterator -= 1
        if iterator < 0:
            iterator = len(queue.items()) - 1

    return queue


def save_object(obj, queue):
    key = object_to_key(obj)

    queue[key]['new_object'] = obj
    queue[key]['status'] = SAVED

    return queue