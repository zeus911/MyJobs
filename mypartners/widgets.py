from django.core.exceptions import ValidationError
from django.forms import (FileField, FileInput, MultiValueField, MultiWidget,
                          Select,
                          fields)

from datetime import datetime, time

hour_choices = [(str(x).zfill(2), str(x).zfill(2)) for x in range(1, 13)]
length_hour_choices = [(str(x).zfill(2), str(x).zfill(2)) for x in range(0, 24)]
minute_choices = [(str(x).zfill(2), str(x).zfill(2)) for x in range(0, 60)]
time_choices = [('AM', 'AM'), ('PM', 'PM')]
month_choices = [
    ('Jan', 'Jan'),
    ('Feb', 'Feb'),
    ('Mar', 'Mar'),
    ('Apr', 'Apr'),
    ('May', 'May'),
    ('Jun', 'Jun'),
    ('Jul', 'Jul'),
    ('Aug', 'Aug'),
    ('Sep', 'Sep'),
    ('Oct', 'Oct'),
    ('Nov', 'Nov'),
    ('Dec', 'Dec'),
]
day_choices = [(str(x).zfill(2), str(x).zfill(2)) for x in range(1, 32)]
year_choices = [(str(x), str(x)) for x in range(2005, 2050)]


class MultipleFileInputWidget(FileInput):
    def render(self, name, value, attrs={}):
        attrs['multiple'] = 'multiple'
        return super(MultipleFileInputWidget, self).render(name, value, attrs)

    def value_from_datadict(self, data, files, name):
        if hasattr(files, 'getlist'):
            return files.getlist(name)
        return [files.get(name, None)]


class SplitDateTimeDropDownWidget(MultiWidget):
    def __init__(self, attrs=None):
        widgets = (
            Select(attrs=attrs, choices=month_choices),
            Select(attrs=attrs, choices=day_choices),
            Select(attrs=attrs, choices=year_choices),
            Select(attrs=attrs, choices=hour_choices),
            Select(attrs=attrs, choices=minute_choices),
            Select(attrs=attrs, choices=time_choices)
        )
        super(SplitDateTimeDropDownWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            month = datetime.strftime(value, '%b')
            day = datetime.strftime(value, '%d')
            year = datetime.strftime(value, '%Y')
            hour = datetime.strftime(value, '%I')
            minutes = datetime.strftime(value, '%M')
            am_pm = datetime.strftime(value, '%p')
            return [month, day, year, hour, minutes, am_pm]
        return [None, None, None, None, None, None]

    def format_output(self, rendered_widgets):
        return ''.join([
            '<div class="date-time">',
            rendered_widgets[0], rendered_widgets[1], rendered_widgets[2],
            '<br/>',
            rendered_widgets[3], rendered_widgets[4], rendered_widgets[5],
            '</div>'
        ])


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
            fields.ChoiceField(choices=month_choices),
            fields.ChoiceField(choices=day_choices),
            fields.ChoiceField(choices=year_choices),
            fields.ChoiceField(choices=hour_choices),
            fields.ChoiceField(choices=minute_choices),
            fields.ChoiceField(choices=time_choices),
        )
        super(SplitDateTimeDropDownField, self). __init__(
            fields=list_fields,
            *args, **kwargs
        )

    def compress(self, data_list):
        month = data_list[0]
        day = data_list[1]
        year = data_list[2]
        hour = data_list[3]
        minutes = data_list[4]
        am_pm = data_list[5]
        date_string = " ".join([month, day, year, hour, minutes, am_pm])
        try:
            date_time = datetime.strptime(date_string, "%b %d %Y %I %M %p")
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
    widget = MultipleFileInputWidget

    def to_python(self, data):
        if not data:
            return None

        datalist = []
        for f in data:
            datalist.append(super(MultipleFileField, self).to_python(f))

        return datalist