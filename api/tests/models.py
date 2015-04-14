from django.test import TestCase
from api.models import APIUser
from api.tests.factories import APIUserFactory


class Models(TestCase):
    def setUp(self):
        self.client.follow = True

    def test_user_creation(self):
        APIUserFactory()
        self.assertEqual(APIUser.objects.count(), 1)

    def test_user_api_key(self):
        user = APIUserFactory()
        path = '/?key=%s&kw=*' % user.key
        response = self.client.get(path)
        self.assertIn(response.status_code, [302, 200])

        path = '/?key=bad'
        response = self.client.get(path)
        self.assertEqual(response.status_code, 403)
