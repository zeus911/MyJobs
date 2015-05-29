from django.contrib import admin

from django_extensions.admin import ForeignKeyAutocompleteAdmin

from seo.models import CompanyUser


def get_companyuser_pk(companyuser):
    """
    Trivial functionality used to change column names

    Inputs:
    :companyuser: CompanyUser instance whose PK is to be retrieved

    Outputs:
    :pk: PK of input object
    """
    return companyuser.pk
get_companyuser_pk.short_description = 'ID'


def get_company_cell(companyuser):
    """
    Inputs:
    :companyuser: CompanyUser instance from which company name will be
        retrieved

    Outputs:
    :name: Name of company
    """
    return companyuser.company.name
get_company_cell.short_description = 'company'


def get_user_cell(companyuser):
    """
    Inputs:
    :companyuser: CompanyUser instance from which user information will
        be retrieved

    Outputs:
    :tag: Anchor tag that opens user edit link in a new tab
    """
    user = companyuser.user
    tag = '<a href="/admin/myjobs/user/%s/" target="_blank">%s</a>' % \
          (user.pk, user.get_full_name(user.email))
    return tag
get_user_cell.short_description = 'user'
get_user_cell.allow_tags = True


def company_user_name(company):
    if company.company_user_count == 0:
        return "%s (%s users) **Might be a duplicate**" % (
            company.name, company.company_user_count)
    else:
        return "%s (%s users)" % (company.name, company.company_user_count)


class CompanyUserAdmin(ForeignKeyAutocompleteAdmin):
    related_search_fields = {
        'user': ('email', ),
        'company': ('name', ),
    }
    related_string_functions = {
        'company': company_user_name,
    }

    search_fields = ['company__name', 'user__email']

    list_display = [get_companyuser_pk, get_user_cell, get_company_cell]

    class Meta:
        model = CompanyUser

    class Media:
        js = ('django_extensions/js/jquery-1.7.2.min.js', )

    def save_model(self, request, obj, form, change):
        # request isn't really accessible from forms; pass inviting user to
        # CompanyUser.save() so that it can be added to an Invitation if one
        # is generated
        obj.save(inviting_user=request.user)


admin.site.register(CompanyUser, CompanyUserAdmin)
