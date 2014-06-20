from django.core.urlresolvers import reverse
from django.test import TestCase

from myjobs.tests.factories import UserFactory
from mysearches.templatetags.email_tags import get_created_url
from mysearches.tests import SavedSearchFactory
from registration.models import ActivationProfile


class SavedSearchTemplateTagTests(TestCase):
    def setUp(self):
        self.user = UserFactory(is_active=True)
        self.search = SavedSearchFactory(user=self.user)

    def test_confirm_creation_active_user(self):
        expected = reverse('view_full_feed') + '?id={id}&verify={guid}'.format(
            id=self.search.pk, guid=self.user.user_guid)
        actual = get_created_url(self.search)

        self.assertEqual(actual, expected)

    def test_confirm_creation_inactive_user(self):
        self.user.is_active = False
        self.user.save()

        user_with_profile = UserFactory(email='example@example.com',
                                        is_active=False)
        profile_search = SavedSearchFactory(user=user_with_profile)
        ActivationProfile.objects.create(user=user_with_profile,
                                         email=user_with_profile.email)

        for saved_search in [self.search, profile_search]:
            actual = get_created_url(saved_search)

            profile = ActivationProfile.objects.get(user=saved_search.user)
            expected = reverse('registration_activate',
                               args=[profile.activation_key]) + \
                '?verify={guid}'.format(guid=saved_search.user.user_guid)
            self.assertEqual(actual, expected)
