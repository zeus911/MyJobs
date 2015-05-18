#! /usr/bin/python
import csv

from django.utils import simplejson

from slugify import slugify

"""
CSV parser for MOC --> Onet codes

"""
MOC_BRANCH_ORDINAL = 0
MOC_CODE_ORDINAL = 2
MOC_TITLE_ORDINAL = 3
ONET1_ORDINAL = 4
ONET2_ORDINAL = 5
ONET3_ORDINAL = 6
ONET4_ORDINAL = 7


def parse_moc_data(file_in, file_out):
    """
    Parses the csv file.
    
    file_in: csv formatted file
    file_out: outputted JSON
    
    Returns JSON of this format:
    [
        "model": "seo.moc",
        "pk": 1,
        "fields": {
            "code": 0107,
            "title": "Undersea Medical Officer",
            "branch": "navy",
            "title_slug": "undersea-medical-officer",
            "onets": "29106300"
        },
        "model": "seo.moc",
        "pk": 2,
        "fields": {
            "code": 1234,
            "title": "Radiologist",
            "branch": "army",
            "title_slug": "radiologist",
            "onets": "29134300"
        }
    ]
    
    """
    branch_translations = {
        "N": "navy",
        "F": "air-force",
        "M": "marines",
        "C": "coast-guard",
        "A": "army"
    }
    mocs = []
    moc_file = open(file_in, "rU")
    csv_reader = csv.reader(moc_file)
    i = 1
    dupe_list = []
    for line in csv_reader:
        branch = branch_translations[line[MOC_BRANCH_ORDINAL]]
        code = line[MOC_CODE_ORDINAL]
        title = line[MOC_TITLE_ORDINAL]
        # we dont want to reprocess any moc/branches that might have
        # already been mapped earlier in the file
        dupe_string = "{code}-{branch}".format(code=code, branch=branch)
        if dupe_string not in dupe_list:
            onets = []
            # This all just needs to be factored out into its own function.
            # This is just terrible.
            if line[ONET1_ORDINAL]:
                try:
                    onet_code = line[ONET1_ORDINAL]
                    # we dont use the .99 convention anymore and it was still
                    # in the Excel crosswalk, so we change it to .00 instead
                    onet_code = onet_code.replace('.99','.00')
                    # the next two lines just strip the - and . out of the
                    # onet code so that we just use it as an integer
                    onet_code = onet_code.replace('-','')
                    onet_code = onet_code.replace('.', '')
                    onets.append(onet_code)
                except KeyError, e:
                    print e
            if line[ONET2_ORDINAL]:
                    try:
                        onet_code = line[ONET2_ORDINAL]
                        onet_code = onet_code.replace('.99','.00')
                        onet_code = onet_code.replace('-','')
                        onet_code = onet_code.replace('.', '')
                        onets.append(onet_code)
                    except KeyError, e:
                        print e
            if line[ONET3_ORDINAL]:
                try:
                    onet_code = line[ONET3_ORDINAL]
                    onet_code = onet_code.replace('.99','.00')
                    onet_code = onet_code.replace('-','')
                    onet_code = onet_code.replace('.', '')
                    onets.append(onet_code)
                except KeyError, e:
                    print e
            if line[ONET4_ORDINAL]:
                try:
                    onet_code = line[ONET4_ORDINAL]
                    onet_code = onet_code.replace('.99','.00')
                    onet_code = onet_code.replace('-','')
                    onet_code = onet_code.replace('.', '')
                    onets.append(onet_code)
                except KeyError, e:
                    print e
            moc = {
                "model": "seo.moc",
                "pk": i,
                "fields": {
                    "code": code,
                    "title": title,
                    "branch": branch,
                    "title_slug": slugify(title),
                    "onets": onets
                }
            }
            mocs.append(moc)
            dupe_list.append(dupe_string)
            i += 1
            
        moc_file.close()
        # The crosswalk file size is pretty large, so we just create a file
        # with the JSON in it.
        fixture_file = open(file_out, 'w')
        fixture_file.write(simplejson.dumps(mocs))
        fixture_file.close()

        
def parse_onet_codes(file_name):
    """
    Parses a tab delimited file of:
    Onet_Code: Onet_Title
    
    We reformat the ONET code to an integer:
    12-3456.78 ---> 12345678
    
    Returns JSON of this format:
    [
        "model": "seo.onet",
        "pk": 12345678,
        "fields": {
            "title": "job title #1"
        },
        "model": "seo.onet",
        "pk": 23456781,
        "fields": {
            "title": "job title #2"
        }
    ]
    """
    mappings = []
    map_file = open(file_name, "rU")
    i = 1

    for line in map_file:
        onet_code, onet_title = line.split('\t')
        onet_code = onet_code.replace('-','')
        onet_code = onet_code.replace('.', '')
        mapping = {
            "model": "seo.onet",
            "pk": onet_code,
            "fields": {
                "title": onet_title.rstrip()
            }
        }
        mappings.append(mapping)
        i = i+1

    map_file.close()
    return simplejson.dumps(mappings)
        
def find_moc_with_non_matching_onet(onet_file, moc_file):
    """
    This function is used to find any MOCs, from the Excel spreadsheet
    I was given, that have an ONET code mapped to it that does NOT exist
    in the database that Kyle uses to classify jobs in the XML feed.
    
    Outputs a list of ONETs that do not exist.

    """
    non_matches = []
    # we create the onet list from the file Kyle gave us
    onets = []
    map_file = open(onet_file, "rU")
    
    for line in map_file:
        onet_code, onet_title = line.split('\t')
        # Do we really need these two commented lines in the code?
        #onet_code = onet_code.replace('-','')
        #onet_code = onet_code.replace('.', '')
        onets.append(onet_code)
        
    map_file.close()
    # parse the Excel spreadsheet, looking for not matching ONETs
    mocs = open(moc_file, "rU")
    csv_reader = csv.reader(mocs)
    # This for loop can be cleaned up considerably given how repetitive
    # it is.
    for line in csv_reader:
        onet1 = line[ONET1_ORDINAL]
        onet2 = line[ONET2_ORDINAL]
        onet3 = line[ONET3_ORDINAL]
        onet4 = line[ONET4_ORDINAL]
        if onet1 and onet1 not in onets + non_matches:
            non_matches.append(onet1)
        if onet2 and onet2 not in onets + non_matches:
            non_matches.append(onet2)
        if onet3 and onet3 not in onets + non_matches:
            non_matches.append(onet3)
        if onet4 and onet4 not in onets + non_matches:
            non_matches.append(onet4)
                        
    for match in non_matches:
        print match
