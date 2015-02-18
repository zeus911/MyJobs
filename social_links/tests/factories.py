import factory


class SocialLinkFactory(factory.django.DjangoModelFactory):
    class Meta:
        user = 'social_links.SocialLink'

    link_url = 'google.com'
    link_title = 'Link Title'
    link_type = 'DirectEmployers'
    link_icon = 'www.example.com'
    content_type_id = 1


class SocialLinkTypeFactory(factory.django.DjangoModelFactory):
    class Meta:
        user = 'social_links.SocialLinkType'

    site = 'Social Site'
    icon = factory.django.FileField(filename='icon.png')
