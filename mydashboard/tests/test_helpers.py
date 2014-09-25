from django.contrib.auth.models import Group

from myjobs.tests.setup import MyJobsBase
from myjobs.tests.factories import UserFactory

from mydashboard.helpers import saved_searches
from seo.models import CompanyUser
from mydashboard.tests.factories import (BusinessUnitFactory,
                                         CompanyUserFactory, CompanyFactory,
                                         SeoSiteFactory)
from mysearches.tests.factories import SavedSearchFactory


class HelpersTests(MyJobsBase):
    def setUp(self):
        self.staff_user = UserFactory()
        group, _ = Group.objects.get_or_create(name=CompanyUser.GROUP_NAME)
        self.staff_user.groups.add(group)

        self.business_unit = BusinessUnitFactory()

        self.company = CompanyFactory()
        self.company.job_source_ids.add(self.business_unit)
        self.admin = CompanyUserFactory(user=self.staff_user,
                                        company=self.company)
        self.microsite = SeoSiteFactory()
        self.microsite.business_units.add(self.business_unit)
        second_microsite = SeoSiteFactory(id=30, domain='test2.jobs')
        second_microsite.business_units.add(self.business_unit)

        self.candidate = UserFactory(email='candidate@my.jobs')

    def test_saved_searches(self):
        # User has no searches at all
        searches = saved_searches(self.staff_user, self.company, self.candidate)
        self.assertFalse(searches)

        # User has searches but none of them belong to the company
        SavedSearchFactory(user=self.candidate,
                           url='http://not-test.jobs/search?q=django',
                           feed='http://not-test.jobs/jobs/feed/rss?',
                           label='test Jobs')
        searches = saved_searches(self.staff_user, self.company, self.candidate)
        self.assertFalse(searches)

        # User has searches that belong to the company
        search1 = 'http://test.jobs/search?q=django'
        search2 = 'http://something.test2.jobs/search?q=python'
        SavedSearchFactory(user=self.candidate,
                           url=search1,
                           feed=search1,
                           label='test Jobs')
        searches = saved_searches(self.staff_user, self.company, self.candidate)
        self.assertEqual(len(searches), 1)
        SavedSearchFactory(user=self.candidate,
                           url=search2,
                           feed=search2,
                           label='test Jobs')
        searches = saved_searches(self.staff_user, self.company, self.candidate)
        self.assertEqual(len(searches), 2)

