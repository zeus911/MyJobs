from django.core.exceptions import ValidationError
from django.forms import (DateInput, FileField, FileInput, MultiValueField,
                          MultiWidget, Select, fields)

from datetime import datetime, time

hour_choices = [(str(x).zfill(2), str(x).zfill(2)) for x in range(1, 13)]
length_hour_choices = [(str(x).zfill(2), str(x).zfill(2)) for x in range(0, 24)]
minute_choices = [(str(x).zfill(2), str(x).zfill(2)) for x in range(0, 60)]
time_choices = [('AM', 'AM'), ('PM', 'PM')]


class MultipleFileWidget(FileInput):
    def render(self, name, value, attrs={}):
        attrs['multiple'] = 'multiple'
        return super(MultipleFileWidget, self).render(name, None, attrs=attrs)

    def value_from_datadict(self, data, files, name):
        if files:
            return list(files.get(name))
        else:
            return None


class SplitDateTimeDropDownWidget(MultiWidget):
    def __init__(self, attrs=None):
        widgets = (
            DateInput(attrs=attrs, format=None),
            Select(attrs=attrs, choices=hour_choices),
            Select(attrs=attrs, choices=minute_choices),
            Select(attrs=attrs, choices=time_choices)
        )
        super(SplitDateTimeDropDownWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            date = datetime.strftime(value, '%d-%b-%Y')
            hour = datetime.strftime(value, '%I')
            minutes = datetime.strftime(value, '%M')
            am_pm = datetime.strftime(value, '%p')
            return [date, hour, minutes, am_pm]
        return [None, None, None, None]


class TimeDropDownWidget(MultiWidget):
    def __init__(self, attrs=None):
        widgets = (
            Select(attrs=attrs, choices=length_hour_choices),
            Select(attrs=attrs, choices=minute_choices)
        )
        super(TimeDropDownWidget, self).__init__(widgets, attrs)

    def format_output(self, rendered_widgets):
        return ''.join([rendered_widgets[0],
                        '<b> hours</b>', '&nbsp;&nbsp;&nbsp;',
                        rendered_widgets[1], '<b> minutes</b>'])

    def decompress(self, value):
        if value:
            return [value.hour, value.minute]
        return [None, None]


class SplitDateTimeDropDownField(MultiValueField):
    widget = SplitDateTimeDropDownWidget

    def __init__(self, *args, **kwargs):
        list_fields = (
            fields.CharField(max_length=255, required=True),
            fields.ChoiceField(choices=hour_choices),
            fields.ChoiceField(choices=minute_choices),
            fields.ChoiceField(choices=time_choices),
        )
        super(SplitDateTimeDropDownField, self). __init__(
            fields=list_fields,
            *args, **kwargs
        )

    def compress(self, data_list):
        date = data_list[0]
        hour = data_list[1]
        minutes = data_list[2]
        am_pm = data_list[3]
        date_string = " ".join([date, hour, minutes, am_pm])
        try:
            date_time = datetime.strptime(date_string, "%d-%b-%Y %I %M %p")
        except ValueError:
            raise ValidationError('Invalid date format.')
        return date_time


class TimeDropDownField(MultiValueField):
    widget = TimeDropDownWidget

    def __init__(self, *args, **kwargs):

        list_fields = (
            fields.ChoiceField(required=False, choices=length_hour_choices),
            fields.ChoiceField(required=False, choices=minute_choices),
        )

        super(TimeDropDownField, self). __init__(
            fields=list_fields,
            *args, **kwargs
        )

    def compress(self, data_list):
        hours = int(data_list[0])
        minutes = int(data_list[1])
        return time(hours, minutes)


class MultipleFileField(FileField):
    widget = MultipleFileWidget

    def __init__(self, *args, **kwargs):
        self.maximum_file_size = kwargs.pop('maximum_file_size', 4194304)
        super(MultipleFileField, self).__init__(*args, **kwargs)

    def to_python(self, data):
        if not data:
            return None
        file_fields = []
        for item in data:
            file_fields.append(super(MultipleFileField, self).to_python(item))
        return file_fields

    def validate(self, data):
        if not data:
            return None
        super(MultipleFileField, self).validate(data)
        for uploaded_file in data:
            if uploaded_file.size > self.maximum_file_size:
                raise ValidationError('File %s too large.' % uploaded_file.name)