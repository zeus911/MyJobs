from myjobs.tests.setup import MyJobsBase
from mydashboard.tests.factories import CompanyFactory

from myjobs.tests.factories import UserFactory
from registration.models import Invitation
from seo.models import CompanyUser, Group


class CompanyUserTests(MyJobsBase):
    def setUp(self):
        super(CompanyUserTests, self).setUp()
        self.user = UserFactory()
        self.company = CompanyFactory()
        self.data = {'user': self.user,
                     'company': self.company}

    def test_add_company_user(self):
        """
        Adding one user as a company user also creates an invitation
        """
        company2 = CompanyFactory(id=12345, name='New Company')
        company_user = CompanyUser(**self.data)
        company_user.save(inviting_user=self.user)
        self.assertEqual(self.company.admins.count(), 1)
        self.assertEqual(Invitation.objects.count(), 1)

        self.data['company'] = company2
        # Save with no iniviting_user. No invitation should be created.
        company_user = CompanyUser(**self.data)
        company_user.save()
        self.assertEqual(company2.admins.count(), 1)
        self.assertEqual(Invitation.objects.count(), 1)

    def test_user_without_company_removed_from_employers_group(self):
        """
        When deleting a company user, if a user still belongs to another
        company, they should still be a part of the "Employer" group. However,
        if they are no longer associated with *any* companies, they should be
        removed from the "Empployer" group.
        """
        company = CompanyFactory(id=2, name="Foo")
        CompanyUser(id=1, user=self.user, company=self.company).save()
        CompanyUser(id=2, user=self.user, company=company).save()
        # ensure that user properly added to Employer group
        self.assertIn(
            Group.objects.get(name="Employer"), self.user.groups.all())
        # ensure that user still belongs to the Employer group
        CompanyUser.objects.first().delete()
        self.assertIn(
            Group.objects.get(name="Employer"), self.user.groups.all())
        # ensure that user doesn't belong to Employer group anymore
        CompanyUser.objects.first().delete()
        self.assertFalse(
            Group.objects.get(name="Employer") in self.user.groups.all())
