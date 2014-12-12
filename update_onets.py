import csv

from django.utils.text import slugify

from moc_coding.models import *

def get_mocs_from_csv(filename, columns):
    # Maps MOC code and Branch as keys, since they are defined as unique
    # together in django.
    mocs = {}
    branches = {
        'A': u'army',
        'C': u'coast-guard',
        'F': u'air-force',
        'M': u'marines',
        'N': u'navy'
    }

    with open(filename, "r") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            code = row[columns['moc_code']]
            branch = row[columns['svc']]
            title = row[columns['moc_title']]
            onet = {
                'code': ''.join(
                    [c for c in row[columns['onet_code']] if c.isdigit()]),
                'title': row[columns['onet_title']]
            }

            if (code, branches[branch]) in mocs:
                # Makes sure we don't add duplicate onets to an already
                # existing MOC
                if onet not in mocs[(code, branches[branch])]['onets']:
                    mocs[(code, branches[branch])]['onets'].append(onet)
            else:
                mocs[(code, branches[branch])] = {
                    'code': code,
                    'branch': branches[branch],
                    'title': title,
                    'title_slug': slugify(unicode(title)),
                    'onets': [onet],
                    # Redundant, but this is how the moc_coding models are laid
                    # out
                    'moc_detail': {
                        'primary_value': code,
                        'service_branch': branch.lower(),
                        'military_description': title
                    }
                }

    return mocs


def run(filename, cols=None):
    # Not all Excel sheets use the same column names
    columns = {
        'svc': 'SVC',
        'moc_code': 'MOC Code',
        'moc_title': 'MOC Title',
        'onet_code': 'O*NET-SOC Code',
        'onet_title': 'O*NET-SOC Title'
    }
    columns.update(cols or {})
    mocs = get_mocs_from_csv(filename, columns)

    new_mocs = []
    for moc in mocs.values():
        moc_detail = moc.pop('moc_detail')
        onets = moc.pop('onets')

        moc_detail_record, _ = MocDetail.objects.get_or_create(**moc_detail)

        moc_record, created = Moc.objects.get_or_create(
            code=moc['code'], branch=moc['branch'])

        if created:
            moc_record.title = moc['title']
            moc_record.title_slug = moc['title_slug']
            moc_record.moc_detail = moc_detail_record
            moc_record.save()
            
            # log change
            new_mocs.append(moc_record)

        onet_records = set()
        for onet in onets:
            onet_record, created = Onet.objects.get_or_create(
                code=onet['code'])

            if created:
                onet_record.title = onet['title']
                onet_record.save()

            onet_records.update([onet_record])

        moc_record.onets.add(*onet_records)

    return new_mocs

if __name__ == '__main__': 
    import sys

    for filename in sys.argv[1:]:
        new_mocs = run(filename)

        print new_mocs
    
