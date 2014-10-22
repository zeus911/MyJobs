""" Functional Tests for mypartners (PRM). """
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

from myjobs.tests.factories import UserFactory
from functional_tests import SeleniumTestCase

class NewUserTests(SeleniumTestCase):

    """Tests Account creation"""

    def setUp(self):
        self.user = UserFactory(first_name="John", last_name="Doe")

    def test_home_page_works(self):
        """
        As John, navigating to https://secure.my.jobs should send me to a page
        titled "My.jobs".
        """
        self.browser.get(self.live_server_url)
        self.assertIn(self.browser.title, 'My.jobs')

    def test_cant_log_in_without_account(self):
        """
        As John, I shouldn't be able to log into My.jobs without registering
        first.
        """
        self.browser.get('/'.join([self.live_server_url, 'prm', 'view']))

        # attempt to log in
        username = self.find('id_username')
        username.send_keys(self.user.email)
        self.find('id_password').send_keys(self.user.password)
        self.find('login').click()

        self.assertEqual(username.get_attribute('placeholder'),
                         'Please enter a correct email.')

    def test_user_registration(self):
        """
        As John, I should be able to register on My.jobs and log in.
        """
        user = UserFactory.build(email='foobar1@baz.com')
        self.browser.get('/'.join([self.live_server_url, 'prm', 'view']))

        # register
        self.find('id_email').send_keys(user.email)
        self.find('id_password1').send_keys(user.password)
        self.find('id_password2').send_keys(user.password)
        self.find('register').click()

        self.assertEqual(self.find('profile').get_attribute(
            'innerHTML'),
            'Skip: Take me to my profile')

    def test_user_login(self):
        self.user.set_password("test")
        self.user.save()
        self.find('id_username').send_keys(self.user.email)
        self.find('id_password').send_keys("test")
        self.find('login').click()

class NormalUserTests(SeleniumTestCase):

    """Tests PRM navigation for existing Users"""
