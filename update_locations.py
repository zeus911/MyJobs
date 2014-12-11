from mypartners.models import Contact, Location

def add_locations():
    """
    Converts contact address information into locations.
    """
    for contact in Contact.objects.all():
        contact.locations.add(Location.objects.create(
            label=contact.label,
            address_line_one=contact.address_line_one,
            address_line_two=contact.address_line_two,
            city=contact.city,
            state=contact.state,
            country_code=contact.country_code,
            postal_code=contact.postal_code))
        contact.save()
