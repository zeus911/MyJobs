def message_lists(request):
    """
    Ensures lists of messages, if any, are always in template contexts.
    """
    if request.user.is_anonymous() or not request.user.pk:
        # User is anonymous or has been deleted; We shouldn't try
        # retrieving messages.
        return {}

    user = request.user
    user.claim_messages()

    all_messages = user.messageinfo_set.filter(
        deleted_on__isnull=True).order_by('-id')
    new_messages = all_messages.filter(read=False, expired=False)
    system_messages = new_messages.filter(message__system=True)

    return {
        'all_messages': all_messages,
        'new_messages': new_messages,
        'system_messages': system_messages
    }