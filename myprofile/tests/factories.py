import factory
import datetime
from myjobs.tests.factories import UserFactory


class SecondaryEmailFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'myprofile.SecondaryEmail'

    user = factory.SubFactory(UserFactory)
    email = "alicia.smith@foo.com"
    label = "Personal"


class NewNameFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'myprofile.Name'

    given_name = "Alice"
    family_name = "Smith"
    primary = False
    user = factory.SubFactory(UserFactory)
    

class PrimaryNameFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'myprofile.Name'

    given_name = "Alice"
    family_name = "Smith"
    primary = True
    user = factory.SubFactory(UserFactory)


class NewPrimaryNameFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'myprofile.Name'

    given_name = "Alicia"
    family_name = "Smith"
    primary = True
    user = factory.SubFactory(UserFactory)


class EducationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'myprofile.Education'

    organization_name = "College"
    degree_date = datetime.date(2005, 1, 2)
    city_name = "Indianapolis"
    country_code = "IN"
    education_level_code = 6
    education_score = "4.0"
    degree_name = "Art"
    degree_major = "Worksmanship"
    degree_minor = "English"
    user = factory.SubFactory(UserFactory)


class AddressFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'myprofile.Address'

    label = "Home"
    address_line_one = "1234 Thing Road"
    address_line_two = "Apt. 8"
    city_name = "Indianapolis"
    country_code = "USA"
    country_sub_division_code = "IN"
    postal_code = "12345"
    user = factory.SubFactory(UserFactory)


class TelephoneFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'myprofile.Telephone'

    use_code = "Home"
    area_dialing = "(123)"
    number = "456-7890"
    user = factory.SubFactory(UserFactory)


class EmploymentHistoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'myprofile.EmploymentHistory'

    position_title = "Handler"
    organization_name = "Mr. Wrench"
    start_date = datetime.date(2005, 3, 4)
    current_indicator = True
    user = factory.SubFactory(UserFactory)


class MilitaryServiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'myprofile.MilitaryService'

    country_code = "USA"
    branch = "Navy"
    department = "CVN"
    division = "Engineering"
    expertise = "Tech"
    service_start_date = datetime.date(2005, 1, 2)
    service_end_date = datetime.date(2007, 1, 2)
    end_rank = "E-7"
    user = factory.SubFactory(UserFactory)


class WebsiteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'myprofile.Website'

    display_text = "My Jobs"
    uri = 'my.jobs'
    uri_active = True
    description = "The site we work on."
    site_type = "Other"
    user = factory.SubFactory(UserFactory)


class LicenseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'myprofile.License'
    
    license_type = "Type"
    license_name = "Name"
    user = factory.SubFactory(UserFactory)


class SummaryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'myprofile.Summary'

    headline = 'My Summary'
    the_summary = "One day I knew I'd work for Mr. Wrench"
    user = factory.SubFactory(UserFactory)


class VolunteerHistoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = 'myprofile.VolunteerHistory'

    position_title = "Title"
    organization_name = "DirectEmployers"
    start_date = datetime.date(2005, 3, 4)
    current_indicator = True
    user = factory.SubFactory(UserFactory)
