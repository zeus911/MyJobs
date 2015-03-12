from django import forms

from myblocks import models


class BlockForm(forms.ModelForm):
    class Meta:
        model = models.Block

    def __init__(self, *args, **kwargs):
        super(BlockForm, self).__init__(*args, **kwargs)
        self.fields['template'].initial = models.raw_base_template(self.Meta.model)


class ApplyLinkBlockForm(BlockForm):
    class Meta:
        model = models.ApplyLinkBlock


class BreadboxBlockForm(BlockForm):
    class Meta:
        model = models.BreadboxBlock


class ColumnBlockForm(forms.ModelForm):
    class Meta:
        exclude = ('template', )
        model = models.ColumnBlock


class ContentBlockForm(BlockForm):
    class Meta:
        model = models.ContentBlock


class JobDetailBlockForm(BlockForm):
    class Meta:
        model = models.JobDetailBlock


class JobDetailBreadboxBlockForm(BlockForm):
    class Meta:
        model = models.JobDetailBreadboxBlock


class LoginBlockForm(BlockForm):
    class Meta:
        model = models.LoginBlock


class MoreButtonBlockForm(BlockForm):
    class Meta:
        model = models.MoreButtonBlock


class RegistrationBlockForm(BlockForm):
    class Meta:
        model = models.RegistrationBlock


class SavedSearchWidgetBlockForm(BlockForm):
    class Meta:
        model = models.SavedSearchWidgetBlock


class SearchBoxBlockForm(BlockForm):
    class Meta:
        model = models.SearchBoxBlock


class SearchFilterBlockForm(BlockForm):
    class Meta:
        model = models.SearchFilterBlock


class SearchResultBlockForm(BlockForm):
    class Meta:
        model = models.SearchResultBlock


class ShareBlockForm(BlockForm):
    class Meta:
        model = models.ShareBlock


class VeteranSearchBoxForm(BlockForm):
    class Meta:
        model = models.VeteranSearchBox


class RowForm(forms.ModelForm):
    class Meta:
        model = models.Row