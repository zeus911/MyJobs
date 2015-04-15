from api.models import APIUser
from api.tests.setup import APIBaseTestCase
from api.tests.factories import APIUserFactory


class Models(APIBaseTestCase):
    def setUp(self):
        super(Models, self).setUp()
        self.client.follow = True

    def test_user_creation(self):
        APIUserFactory()
        # One user was already created during test setup.
        self.assertEqual(APIUser.objects.count(), 2)

    def test_user_api_key(self):
        user = APIUserFactory()
        path = '/?key=%s&kw=*' % user.key
        response = self.client.get(path)
        self.assertIn(response.status_code, [302, 200])

        path = '/?key=bad'
        response = self.client.get(path)
        self.assertEqual(response.status_code, 403)
