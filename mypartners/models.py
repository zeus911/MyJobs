from django.db import models

from myjobs.models import User


class Partner(models.Model):
    """

    """
    name = models.CharField(max_length=255,
                            verbose_name='Partner Organization')
    uri = models.URLField(verbose_name='Partner URL')
    partner_of = models.ForeignKey(User)
    contacts = models.ManyToManyField(PartnerContact)


class PartnerContact(models.Model):
    """

    """
    partner = models.ForeignKey(Partner)
    given_name = models.CharField(max_length=255)
    family_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, verbose_name='Email')
    phone = models.CharField(max_length=30, verbose_name='Phone',
                             blank=True)
    address = models.CharField(max_length=255, verbose_name='Address',
                               blank=True)
    city = models.CharField(max_length=255, verbose_name='City',
                            blank=True)
    state = models.CharField(max_length=5, verbose_name='State/Region',
                             blank=True)
    postal_code = models.CharField(max_length=12, verbose_name='Postal Code',
                                   blank=True)
    notes = models.TextField(max_length=1000, verbose_name='Notes', blank=True)
