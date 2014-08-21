from django.contrib.auth.models import AnonymousUser

from myjobs.tests.setup import MyJobsBase
from myprofile.forms import InitialNameForm
from myjobs.models import User


class FormTests(MyJobsBase):
    def test_anon_user(self):
        """
        Test confirms that forms using BaseModelForm save without errors or
        creating a user when the user is anonymous.

        """
        anon_user = AnonymousUser()
        data = {"given_name": "Anon", "family_name": "User",
                "user": anon_user}
        form = InitialNameForm(data, **{"user": anon_user})
        self.assertTrue(form.is_valid())
        form.save()
        self.assertFalse(User.objects.all().exists())
