from django.db import models

from myjobs.models import User


class Contact(models.Model):
    """

    """
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=255, verbose_name='Full Name',
                            blank=True)
    email = models.EmailField(max_length=255, verbose_name='Email', blank=True)
    phone = models.CharField(max_length=30, verbose_name='Phone', blank=True)
    label = models.CharField(max_length=60, verbose_name='Address Label',
                             blank=True)
    address_line_one = models.CharField(max_length=255,
                                        verbose_name='Address Line One',
                                        blank=True)
    address_line_two = models.CharField(max_length=255,
                                        verbose_name='Address Line Two',
                                        blank=True)
    city = models.CharField(max_length=255, verbose_name='City', blank=True)
    state = models.CharField(max_length=5, verbose_name='State/Region',
                             blank=True)
    country_code = models.CharField(max_length=3, verbose_name='Country',
                                    blank=True)
    postal_code = models.CharField(max_length=12, verbose_name='Postal Code',
                                   blank=True)
    notes = models.TextField(max_length=1000, verbose_name='Notes', blank=True)


class Partner(models.Model):
    """

    """
    name = models.CharField(max_length=255,
                            verbose_name='Partner Organization')
    uri = models.URLField(verbose_name='Partner URL')
    partner_of = models.ForeignKey(User)
    contacts = models.ManyToManyField(Contact, related_name="contacts")
    primary_contact = models.ForeignKey(Contact, null=True,
                                        on_delete=models.SET_NULL)
