""" Functional Test for MyPartners using Selenium """

from django_liveserver.textcases import LiveServerTextCase
from selenium import webdriver

class SeleniumTestCase(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        cls.driver = driver.PhantomJS()
        super(SeleniumTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
