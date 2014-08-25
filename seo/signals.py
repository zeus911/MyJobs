import Queue

from django.contrib import messages
from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import Signal, receiver

from seo.models import Configuration, SeoSite, Company


# We're a using queue to store messages until they can be read by their handler
# In admin, we check this queue so that warning messages can be sent to the user
# using django.contrib.messages and the request object
# We may be able to implement this behavior in a custom logger
class MessageQueue():
    """
    A queue for storing messages until they can be handled
    Methods should be accessed through the class itself, not instances
    MessageQueue.put(message)
    MessageQueue.send_messages(request)
    """
    message_queue = Queue.Queue()
    
    @classmethod
    def send_messages(self, request):
        """
        Sends all messages in queue to current user based on input request object
        This currently sends a flash message using django.contrib.messages

        """
        while not self.message_queue.empty():
            messages.warning(request, self.message_queue.get())

    @classmethod
    def put(self, message):
        """Store the input message string in queue to be sent later """
        self.message_queue.put(message)


moc_toggled_on = Signal()
moc_toggled_off = Signal()

# Microsite signals should take Site instances for the sender argument
microsite_disabled = Signal()
microsite_moved = Signal(['old_domain'])


def check_message_queue(f):
    """
    A decorator that will send messages from the signal MessageQueue in
    functions with a request object

    We currently use this in the admin and assume that the 2nd argument on the
    decorated function is a request object. If there is no request object,
    messages are not sent.

    """
    def send_message(self, request=None, *args, **kwargs):
        retval = f(self, request, *args, **kwargs)
        if request is not None:
            MessageQueue.send_messages(request)
        return retval
    return send_message

@receiver(microsite_moved)
def update_canonical_microsites(sender, old_domain, **kwargs):
    """
    Updates company's canonical microsite when an seosite domain is
    changed
    
    """
    companies = Company.objects.filter(
            canonical_microsite='http://%s' % old_domain)
    #Log messages now because the queryset becomes empty after the update
    for company in companies:
        MessageQueue.put(
          'Canonical microsite for {0} changed from {1} to {2}'.format(
             company.name, old_domain, sender.domain))
    companies.update(canonical_microsite='http://%s' % sender.domain)

@receiver(microsite_disabled)
def remove_canonical_microsite(sender, **kwargs):
    """
    Removes a company's canonical microsite when a SeoSite is disabled
    
    """
    companies = Company.objects.filter(
            canonical_microsite='http://%s' % sender.domain)
    for company in companies:
        MessageQueue.put(
          'Canonical microsite for {0} removed, default is www.my.jobs'.format(
             company.name, sender.domain))
    companies.update(canonical_microsite=None)


@receiver(post_save, sender=Configuration, dispatch_uid='seo.config_change_monitor')
def config_change_monitor(sender, instance, **kwargs):
    """
    Checks if a configuration change results in a disabled microsite

    """
    for site in instance.seosite_set.all():
        production_configs =  site.configurations.filter(status=2)
        if not production_configs.exists():
            microsite_disabled.send(sender=site)

@receiver(pre_delete, sender=Configuration, dispatch_uid='seo.config_delete_monitor')
def config_delete_monitor(sender, instance, **kwargs):
    """
    Checks if a configuration deletion results in a disabled microsite

    """

    for site in instance.seosite_set.all():
        production_configs =  site.configurations.filter(
                status=2).exclude(id=instance.id)
        if not production_configs.exists():
            microsite_disabled.send(sender=site)

@receiver(pre_delete, sender=SeoSite, dispatch_uid='seo.seosite_delete_monitor')
def seosite_delete_monitor(sender, instance, **kwargs):
    microsite_disabled.send(sender=instance)

@receiver(pre_save, sender=SeoSite, dispatch_uid='seo.seosite_change_monitor')
def seosite_change_monitor(sender, instance, **kwargs):
    """
    Checks for changes to an SeoSite domain and sends the appropriate signal

    """
    pk = instance.pk
    try:
        old_instance = SeoSite.objects.get(id=pk)
    except sender.DoesNotExist:
        return None
    if old_instance.domain != instance.domain:
        microsite_moved.send(sender=instance, old_domain=old_instance.domain) 
