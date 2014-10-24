""" Functional Tests for My.jobs
    These tests are meant to test My.jobs functionality at a high-level. As
    such, they are written such that they test user expectations, rather than
    specific functionality.
"""
from django.test import LiveServerTestCase
from django.test.utils import override_settings
from pyvirtualdisplay import Display
from selenium import webdriver

@override_settings(DEBUG=True)
class SeleniumTestCase(LiveServerTestCase):

    """ Adds Selenium to LiveServerTestCase. """

    @classmethod
    def setUpClass(cls):
        cls.display = Display(visible=0, size=(1024, 768))
        cls.display.start()
        cls.browser = webdriver.Firefox()
        super(SeleniumTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        cls.display.stop()
        super(SeleniumTestCase, cls).tearDownClass()

    def find(self, id_=None, **kwargs):
        """
        Conveninece method which dispatches to selenium's find_element_by_*
        methods. Since searching by ID is the common case, it is the sole
        positional argument. Searching by name or xpath can be done by passing
        their respective keyword arguments.
        """
        name = kwargs.pop('name', None)
        xpath = kwargs.pop('xpath', None)

        if id_:
            return self.browser.find_element_by_id(id_)
        elif name:
            return self.browser.find_element_by_name(name)
        elif xpath:
            return self.browser.find_element_by_xpath(xpath)
