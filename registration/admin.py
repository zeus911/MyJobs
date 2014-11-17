from django.contrib import admin
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from registration.forms import InvitationForm
from registration.models import ActivationProfile, Invitation


class InvitationAdmin(admin.ModelAdmin):
    form = InvitationForm
    list_display = ['invitee_email', 'inviting_user', 'inviting_company',
                    'invited', 'added_permission', 'added_saved_search',
                    'accepted']

    def __init__(self, *args, **kwargs):
        super(InvitationAdmin, self).__init__(*args, **kwargs)
        # Render the model instances on the Invitation admin non-clickable.
        self.list_display_links = (None, )

    def change_view(self, *args, **kwargs):
        # Redirect the user to the main Invitation admin if they correctly
        # guess the url to edit an invitation.
        return HttpResponseRedirect(
            reverse('admin:registration_invitation_changelist'))

    def get_actions(self, request):
        actions = super(InvitationAdmin, self).get_actions(request)
        # Remove the edit button from the Invitation list.
        actions.pop('edit_selected', None)
        return actions

    def get_form(self, request, obj=None, **kwargs):
        # Add the current administrative user to the invitation form so that
        # the inviting user can be tracked.
        form = super(InvitationAdmin, self).get_form(request, obj, **kwargs)
        form.admin_user = request.user
        return form


admin.site.register(ActivationProfile)
admin.site.register(Invitation, InvitationAdmin)
