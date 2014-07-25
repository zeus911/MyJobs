""" OFCCP Directory

    This module is just a utility module which coverts the HTML generated
    from www.dol-esa.gov/errd/resources.html to more manageable formats.
"""

from collections import namedtuple
import os

from lxml import html
from lxml.cssselect import CSSSelector
import requests

__ALL__ = ["get_contacts"]

def get_contacts(text=None):
    """ Generator that produces OFCCP contact info from an HTML file.

        .. note:: If no HTML file is given, a local file named
        "ofccp_contacts.html" located in the same directory as this module is
        assumed.

        This generator yields an OFCCP namedtuple whose fields coincide with
        the table headers present in `html_file`. In the case of `state` there
        exists two fields:

        state
            The long version of the state. Presumably indicative of the state
            in which the organization operates in.

        st
            This is the two-letter state abbreviation. Unlike `state`, this
            field indicates the state in which the organization's home office
            resides.
    """
    text = text or open(os.path.join(os.path.dirname(__file__),
                                     "ofccp_contacts.html")).read()
    tree = html.fromstring(text)

    # convert column headers to valid Python identifiers, and rename duplicates
    cols = []
    for header in CSSSelector("p ~ table th")(tree):
        col = header.text.lower()
        if col in cols:
            cols.append(col[:2])
        else:
            cols.append(col.replace(" ", "_"))

    OFCCP = namedtuple("OFCCP", cols)
    for row in CSSSelector("p ~ table tr")(tree):
        fields = dict((cols[i], td.text) for i, td in 
                      enumerate(CSSSelector("td")(row)))

        for column, value in fields.items():
            if value in [u"\xa0", None]:
                fields[column] = ""
            elif value == "Y":
                fields[column] = True
            elif value == "N":
                fields[column] = False

            if column in ["minority", "female", "disabled", "veteran",
                          "exec_om", "first_om", "professional", "technician",
                          "sales", "admin_support", "craft", "operative", 
                          "labor", "service"]:
                fields[column] = bool(value.strip())

        if len(fields) > 1:
            yield OFCCP(**fields)

def get_html():
    """ Get OFCCP data in HTML format.

        The POST request is necessary in order to get the cookie required by
        the GET request in order to obtain useful results.
    """
    cookie_url = 'http://www.dol-esa.gov/errd/directory.jsp'
    excel_url = 'http://www.dol-esa.gov/errd/directoryexcel.jsp'
    response = requests.post(cookie_url, data=dict(
        reg='None', # Region
        stat='None', # State
        name='',
        city='',
        sht='None', # Contractor Type
        lst='None', # Resource Organization
        sortorder='asc'))

    return requests.get(excel_url, cookies=response.cookies).text
