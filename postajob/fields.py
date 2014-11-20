from django.forms import ChoiceField


class NoValidationChoiceField(ChoiceField):
    def validate(self, value):
        """
        Bypasses the typical choice field validation. Used in cases
        where choices have been inserted, removed, or re-invisioned using
        javascript.

        """
        pass