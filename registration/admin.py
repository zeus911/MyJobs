from django.contrib import admin

from registration.forms import InvitationForm
from registration.models import ActivationProfile, Invitation


class InvitationAdmin(admin.ModelAdmin):
    form = InvitationForm
    list_display = ['invitee_email', 'inviting_user', 'inviting_company',
                    'invited', 'added_permission', 'added_saved_search',
                    'accepted']

    def __init__(self, *args, **kwargs):
        super(InvitationAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None, )

    def get_actions(self, request):
        actions = super(InvitationAdmin, self).get_actions(request)
        actions.pop('edit_selected', None)
        return actions

    def get_form(self, request, obj=None, **kwargs):
        form = super(InvitationAdmin, self).get_form(request, obj, **kwargs)
        form.admin_user = request.user
        return form


admin.site.register(ActivationProfile)
admin.site.register(Invitation, InvitationAdmin)