from django.conf import settings
from django.contrib.admin import AdminSite
from django.db import connection
from django.test import RequestFactory

from myemails.admin import ValueEventAdmin, CronEventAdmin
from myemails.models import ValueEvent, CronEvent
from myjobs.tests.factories import UserFactory
from myjobs.tests.setup import MyJobsBase
from seo.models import SeoSite
from seo.tests.factories import CompanyUserFactory


class AdminTests(MyJobsBase):
    def setUp(self):
        super(AdminTests, self).setUp()
        self.site = AdminSite()
        settings.SITE = SeoSite.objects.first()
        self.request = RequestFactory().get('/')
        self.user = UserFactory(is_superuser=True)
        self.request.user = self.user

    def test_admin_request_form(self):
        """
        The forms used by ValueEventAdmin and CronEventAdmin should have the
        current request as attributes.
        """
        for Admin, Model in [(ValueEventAdmin, ValueEvent),
                             (CronEventAdmin, CronEvent)]:
            admin = Admin(Model, self.site)
            form = admin.get_form(self.request)()
            self.assertEqual(form.request, self.request)

    def test_non_superuser_form(self):
        """
        The email_template queryset should have an appropriate WHERE clause
        if the current user is not a company user.
        """
        company = CompanyUserFactory(user=self.user).company
        admin = ValueEventAdmin(ValueEvent, self.site)

        for superuser in [True, False]:
            self.user.is_superuser = superuser
            self.user.save()
            form = admin.get_form(self.request)()
            email_template = form.fields['email_template']
            query = str(email_template.queryset.query)
            if superuser:
                self.assertFalse('WHERE' in query)
            else:
                if connection.vendor == 'sqlite':
                    test = 'WHERE ("myemails_emailtemplate"."owner_id" = %s'
                else:
                    test = 'WHERE (`myemails_emailtemplate`.`owner_id` = %s'
                self.assertTrue(test % company.pk in query)
