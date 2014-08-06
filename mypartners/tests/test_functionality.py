from django.test import TestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class TestNewAccount(TestCase):

    def setUp(self):
        self.driver = webdriver.PhantomJS()
        self.email = 'foo@bar.com'
        self.password = 'password'

        self.driver.get('http://localhost:8000')

    def tearDown(self):
        self.driver.quit()

    def test_new_user(self):
        email = self.driver.find_element_by_name('email')
        password1 = self.driver.find_element_by_name('password1')
        password2 = self.driver.find_element_by_name('password2')
        register = self.driver.find_element_by_name('register')

        email.send_keys(self.email)
        password1.send_keys(self.password)
        password2.send_keys(self.password)
        register.click()
