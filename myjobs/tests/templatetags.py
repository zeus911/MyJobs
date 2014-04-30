from bs4 import BeautifulSoup

from django.template import Template, Context
from django.test import TestCase

from myjobs.forms import EditAccountForm
from myjobs.tests.factories import UserFactory
from myjobs.templatetags.common_tags import gz
from myprofile.tests.factories import PrimaryNameFactory


class CommonTagsTests(TestCase):
    def setUp(self):
        super(CommonTagsTests, self).setUp()
        self.user = UserFactory()
        self.context = Context({'user': self.user})

    def test_get_name_obj_no_name(self):
        template = Template(
            '{{ user.get_full_name }}'
        )
        out = template.render(self.context)
        self.assertEqual(out, '')

    def test_get_name_obj_with_name(self):
        template = Template(
            '{{ user.get_full_name }}'
        )
        name = PrimaryNameFactory(user=self.user)
        out = template.render(self.context)
        self.assertEqual(out, name.get_full_name())

    def test_get_name_obj_with_default(self):
        template = Template(
            '{% if not user.get_full_name %}'
            'Default value'
            '{% else %}'
            '{{ user.get_full_name }}'
            '{% endif %}'
        )
        out = template.render(self.context)
        self.assertEqual(out, 'Default value')


class FormTagsTests(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.form = EditAccountForm(user=self.user, data={})
        self.context = Context({'form': self.form})
        self.template = Template(
                         '{% load form_tags %}'
                         '{% add_required_label form.visible_fields.2 %}'
                      )

    def test_add_required_label(self):
        self.form.data['gravatar'] = self.user.email
        out = self.template.render(self.context)
        soup = BeautifulSoup(out)
        self.assertEqual(soup.label['class'], [u''])

    def test_add_required_label_bad_form(self):
        out = self.template.render(self.context)
        soup = BeautifulSoup(out)
        self.assertEqual(soup.label['class'], [u'label-required'])

    def test_add_required_label_extra_classes(self):
        self.template = Template(
                 '{% load form_tags %}'
                 '{% add_required_label form.visible_fields.2 "extra-class" %}'
                      )
        out = self.template.render(self.context)
        soup = BeautifulSoup(out)
        self.assertItemsEqual(soup.label['class'], [u'extra-class',
                                                    u'label-required'])


class GZipTagTestCase(TestCase):
    """Validate that the gzip tag works correctly."""

    def test_gz_without_request(self):
        """
        Validate that when the request is not passed to the tag, we default to
        no gzip compression.
        """
        context = {}
        self.assertEqual(gz(context), '')

    def test_gz_without_gzip_encoding_accepted(self):
        """
        Validate that when the request does not specify gzip is accepted, we
        do not append .gz to links.
        """
        # Mock the context object, which should include a request.
        request = lambda: None
        request.META = {'HTTP_ACCEPT_ENCODING': ''}
        context = {'request': request}
        self.assertEqual(gz(context), '')

    def test_gz_with_gzip_encoding_accepted(self):
        """
        Validate that when the request does not specify gzip is accepted, we
        do not append .gz to links.
        """
        # Mock the context object, which should include a request.
        request = lambda: None
        request.META = {'HTTP_ACCEPT_ENCODING': 'gzip'}
        context = {'request': request}
        self.assertEqual(gz(context), '.gz')
