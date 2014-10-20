from myjobs.forms import ChangePasswordForm
from myjobs.tests.factories import UserFactory
from myjobs.tests.test_views import TestClient
from myprofile.tests.factories import PrimaryNameFactory
from setup import MyJobsBase


class AccountFormTests(MyJobsBase):
    def setUp(self):
        super(AccountFormTests, self).setUp()
        self.user = UserFactory()
        self.name = PrimaryNameFactory(user=self.user)
        self.client = TestClient()
        
    def test_password_form(self):
        invalid_data = [
            { 'data': {'password': 'cats',
                       'new_password1': 'newpassword',
                       'new_password2': 'newpassword'},
              u'errors': [['password', [u"Wrong password."]]]},
            { 'data': {'password': 'secret',
                       'new_password1': 'newpassword',
                       'new_password2': 'notnewpassword'},
                u'errors':
                    [[u'new_password2', [u'The new password fields did not match.']],
                    [u'new_password1', [u'The new password fields did not match.']]],
            
            },
        ]

        for item in invalid_data:
            form = ChangePasswordForm(user=self.user, data=item['data'])
            self.failIf(form.is_valid())
            self.assertEqual(form.errors[item[u'errors'][0][0]],
                             item[u'errors'][0][1])

        form = ChangePasswordForm(user=self.user,data={'password': 'secret',
                                                       'new_password1': 'anothersecret',
                                                       'new_password2': 'anothersecret'})
        
        self.failUnless(form.is_valid())
        form.save()
        self.failUnless(self.user.check_password('anothersecret'))
