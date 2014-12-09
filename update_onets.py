import csv

from django.utils.text import slugify

from moc_coding.models import *

reader = csv.DictReader(open("onets1.csv"))
# Maps MOC code and Branch as keys, sine they are defined as unique together in
# django.
mocs = {}
branches = {
    'A': u'army',
    'C': u'coast-guard',
    'F': u'air-force',
    'M': u'marines',
    'N': u'navy'
}

for row in reader:
    code = row['MOC Code']
    branch = branches[row['SVC']]
    onet = {
        'code': ''.join([c for c in row['O*NET-SOC Code'] if c.isdigit()]),
        'title': row['O*NET-SOC Title']
    }

    if (code, branch) in mocs:
        # Makes sure we don't add duplicate onets to an already existing MOC
        if onet not in mocs[(code, branch)]['onets']:
            mocs[(code, branch)]['onets'].append(onet)
    else:
        mocs[(code, branch)] = {
            'code': row['MOC Code'],
            'branch': branch,
            'title': row['MOC Title'],
            'title_slug': slugify(unicode(row['MOC Title'])),
            'onets': [onet],
            # Redundant, but this is how the moc_coding models are laid out
            'moc_detail': {
                'primary_value': row['MOC Code'],
                'service_branch': row['SVC'].lower(),
                'military_description': row['MOC Title']
            }
        }

def run():
    for key, moc in mocs.items():
        moc_detail = moc.pop('moc_detail')
        onets = moc.pop('onets')

        detail_exists = MocDetail.objects.filter(**moc_detail).exists()
        if detail_exists:
            moc_detail_record = MocDetail.objects.get(**moc_detail)
        else:
            moc_detail_record = MocDetail.objects.create(**moc_detail)

        moc_exists = Moc.objects.filter(
            code=moc['code'], branch=moc['branch']).exists()
        if moc_exists:
            moc_record = Moc.objects.filter(
                code=moc['code'], branch=moc['branch'])
            moc_record.update(**moc)
        else:
            moc = Moc.objects.create(moc_detail=moc_detail_record, **moc)

        onet_records = []
        for onet in onets:
            onet_exists = Onet.objects.filter(code=onet['code']).exists()

            if onet_exists:
                onet_records.append(Onet.objects.get(code=onet['code']))
            else:
                onet_records.append(Onetobjects.create(**onet))

