import json
import requests
import time

missing_logos = []

r = requests.get('http://www.my.jobs/ajax/member-companies/jsonp')
cos = json.loads(r.text[25:-1])

print "Testing companies"
print len(cos)

for co in cos:
    # As of now, all image URLs have the format 
    # '//d2e48ltfsb5exy.cloudfront.net/100x50/seo/co-name.gif'. If this were ever to change, 
    # a more robust method of separating the protocol/host from the path would
    # be needed.
    print u"Testing {0}... ".format(co['image']),
    res = requests.head(co['image'])
    if res.status_code == 404:
        missing_logos.append(co)
        print u'failed'
    else:
        print u"success!"
    time.sleep(.25)

# companies missing logos
print
print "Companies missing logos:"
for co in missing_logos:
    print co['name']
