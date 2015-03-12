from django.db.models import Sum

from report_tools import charts
from report_tools.chart_data import ChartData
from report_tools.renderers.googlecharts import GoogleChartsRenderer
from report_tools.reports import Report

from mypartners.models import CONTACT_TYPE_CHOICES


class PRMReport(Report):

    renderer = GoogleChartsRenderer

    communication_activity = charts.PieChart(
        title='Communication Activity',
        height=330,
        width=350,
        renderer_options={
            'legend': 'none',
            'pieSliceText': 'none',
            'pieHole': 0.6,
            'chartArea': {
                'top': 12,
                'left': 12,
                'height': 300,
                'width': 330},
            'colors': ['#4bb1cf', '#faa732', '#5f6c82', '#5eb95e']
            })

    referral_activity = charts.ColumnChart(
        title='Referral Activity',
        height=356,
        width=360,
        renderer_options={
            'legend': 'none',
            'chartArea': {
                'top': 22,
                'left': 37,
                'height': 270,
                'width': 290},
            'colors': ['#08c']})

    def __init__(self, records, *args, **kwargs):
        self.records = records
        super(PRMReport, self).__init__(*args, **kwargs)

    def get_data_for_communication_activity(self):
        data = ChartData()

        data.add_columns(['Contact Type', 'Count'])

        for contact_type, label in CONTACT_TYPE_CHOICES:
            if label != 'Job Followup':
                count = self.records.filter(contact_type=contact_type).count()
                data.add_row([label, count])

        return data

    def get_data_for_referral_activity(self):
        data = ChartData()
        data.add_columns(['Referral Type', 'Count'])

        referrals = self.records.aggregate(
            applications=Sum('job_applications'),
            interviews=Sum('job_interviews'),
            hires=Sum('job_hires'))

        data.add_row(['Applications', referrals['applications']])
        data.add_row(['Inteviews', referrals['interviews']])
        data.add_row(['Hires', referrals['hires']])
        data.add_row(['Records', self.records.filter(
            contact_type='job').count()])

        return data
