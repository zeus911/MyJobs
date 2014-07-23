""" OFCCP Directory 

    This module is just a utility module which coverts the HTML generated
    from www.dol-esa.gov/errd/resources.html to more manageable formats.
"""

from collections import namedtuple
import os

from lxml import html
from lxml.cssselect import CSSSelector

__ALL__ = ["JSP_FILE", "ofccps"]

# because exporting as Excel apparently means download a HTML table
JSP_FILE = os.path.join(os.path.dirname(__file__), "resourceexcel.jsp")

tree = html.fromstring(open(JSP_FILE, "r").read())
select = lambda sel, html=tree: CSSSelector(sel)(html)

# convert column headers to valid Python identifiers, and rename duplicates
cols = []
for th in select("p ~ table th"):
    col = th.text.lower()
    if col in cols:
        cols.append(col[:2])
    else:
        cols.append(col.replace(" ", "_"))

OFCCP = namedtuple("OFCCP", cols)

ofccps = []
for row in select("p ~ table tr"):
    cols = [td.text for td in select("td", row)]

    if len(cols) == 34:
        ofccps.append(OFCCP(*[col.replace(u"\xa0", " ") for col in cols]))
