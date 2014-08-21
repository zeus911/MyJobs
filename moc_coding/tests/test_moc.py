import os

from seo.models import User
from seo.tests.setup import DirectSEOBase

from moc_coding.tests.factories import (CustomCareerFactory, MocFactory,
                                        MocDetailFactory, OnetFactory)
from xmlparse import DEv2JobFeed


class MocTestCase(DirectSEOBase):
    def setUp(self):
        super(MocTestCase, self).setUp()
        self.onet = OnetFactory()
        self.moc = MocFactory()
        self.mapping = CustomCareerFactory()
        self.superuser = User.objects.create_superuser(
            password='iam',
            email='sam@sales.com')
        self.staff_user, created = User.objects.create_user(
            password='123',
            email='joe@test.com',
            )
        self.staff_user.is_staff = True
        self.staff_user.save()

    def test_mapped_mocs(self):
        file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                 'dseo_feed_1.xml')
        feed = DEv2JobFeed(file_path, jsid=self.mapping.object_id)
        job = {'onet_code': [self.onet.code]}
        mocs = feed.job_mocs(job)
        mapped_mocs = feed.mapped_mocs(mocs, job)
        self.assertEqual(len(mocs), 0)
        self.assertEqual(len(mapped_mocs.codes), 1)

    def test_mocs(self):
        new_onet = OnetFactory(code="22222222")
        new_custom_mapping = CustomCareerFactory(onet_id="22222222")
        new_moc_detail = MocDetailFactory(id=2)
        new_moc = MocFactory(id=2, code="2", moc_detail_id=2)
        new_moc.onets = [new_onet]
        new_moc.save()

        new_onet = OnetFactory(code="33333333")
        new_custom_mapping = CustomCareerFactory(onet_id="33333333")
        new_moc_detail = MocDetailFactory(id=3)
        new_moc = MocFactory(id=3, code="3", moc_detail_id=3)
        new_moc.onets = [new_onet]
        new_moc.save()

        file_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                 'dseo_feed_2.xml')
        feed = DEv2JobFeed(file_path, jsid=self.mapping.object_id)
        solr_dict = feed.solr_jobs()
        self.assertEqual(solr_dict[0]['moc'], ['2', '3'])

        job = {'onet_code': ['99999999', '22222222', '33333333']}
        mocs = feed.job_mocs(job)
        mapped_mocs = feed.mapped_mocs(mocs, job)

        self.assertEqual(len(mocs), 2)

    def test_authentication(self):
        #If user isn't logged in, redirect to login view
        resp = self.client.get('/mocmaps/newmap/?onet=99999999')
        self.assertEqual(resp.status_code, 302)

        #superusers should get a JSON 'success' response
        login = self.client.login(email=self.superuser.email,
                                  password='iam')
        resp =self.client.get(
            '/mocmaps/newmap/?onet=99999999&'
            'moc=01&branch=coast-guard&oid=1&ct=21',
            )
        self.assertEqual(resp.status_code, 200)
        self.assertIn('success', resp.content)

        #Staff should get a JSON error message
        login = self.client.login(email=self.staff_user.email,
                                  password='123')
        resp =self.client.get(
            '/mocmaps/newmap/?onet=99999999&'
            'moc=01&branch=coast-guard&oid=1&ct=21',
            )
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn('success', resp.content)
