from StringIO import StringIO
import datetime
import json
from xml.sax.xmlreader import AttributesImpl
from xml.sax.saxutils import unescape

from django.core.serializers.xml_serializer import Serializer
from django.utils.xmlutils import SimplerXMLGenerator
from django.utils.encoding import is_protected_type
from django.utils import datetime_safe
from django.conf import settings


class SimplerXMLGeneratorWithCDATA(SimplerXMLGenerator):
    def write_cdata(self, content):
        """wraps xml content in CDATA tags"""
        self._write('<![CDATA[%s]]>' % content)
        

class ExtraValue():
    """
    Stores an extra node's name, content, and attributes

    Attributes:
    :name: Node's name or tag, string
    :content: String content of the data
    :attributes: dictionary of {attribute:value} pairs

    """

    def __init__(self, name, content=None, attributes=None):
        if attributes:
            self.attributes = attributes
        else:
            self.attributes = {}
        self.__dict__.update(locals())


class ExtraValuesSerializer(Serializer):
    """
    Extends django's serializer to support several calculated fields and
    addition of extra nodes with attribute values

    """

    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%H:%M:%S"

    def __init__(self, feed_type='xml', publisher='', publisher_url='', 
                 last_build_date='', field_mapping=None, extra_values=None):
        """
        Inputs:
        :field_mapping: Dict that maps "object field name":"feed field name"
        :publisher: Name of feed source
        :last_build_date: When feed was last built 
        :publisher_url: Link to publisher
        :extra_values: A list of ExtraValue objects to add to serialized data

        """
        if field_mapping is None:
            field_mapping = {}
        if extra_values is None:
            extra_values = {} 
        self.extra_values = extra_values
        self.field_mapping = field_mapping
        self.publisher = publisher
        self.publisher_url = publisher_url
        self.last_build_date = last_build_date
        self.feed_type = feed_type

    def finish_handle_item(self, field_name, value, attributes=None):
        pass

    def handle_item(self, key, value, attributes=None):
        field_name = self.field_mapping.get(key, key)
        if isinstance(value, datetime.datetime):
            d = datetime_safe.new_datetime(value)
            value = d.strftime("%s %s" % (self.DATE_FORMAT, self.TIME_FORMAT))
        self.finish_handle_item(field_name=field_name, value=value,
                                attributes=attributes)
 
    def handle_item_url(self, item):
        is_posted = item.get('is_posted', False)
        if is_posted:
            # If an item is posted, instead of using the
            # redirect link we use the http://site.jobs/guid/jobs/ link
            # that goes directly to the microsite.
            item_url = "%s/%s/job/" % (self.publisher_url, item['guid'])
            self.finish_handle_item(field_name='url', value=item_url,
                                    attributes={})
        else:
            vs = settings.FEED_VIEW_SOURCES.get(self.feed_type, 20)
            item_url = "%s/%s%s" % (self.publisher_url, item['guid'], vs)
            self.finish_handle_item(field_name='url', value=item_url,
                                    attributes={})

    def build_link_name(self, link):
        name = "link href={l} rel={rel}".format(l=link.url, rel=link.rel)

    def serialize(self, queryset, **options):
        """
        Serialize a queryset.
        
        """
        self.options = options
        self.stream = options.get("stream", StringIO())
        #self.selected_fields = fields
        self.use_natural_keys = options.get("use_natural_keys", False)
        self.start_serialization()
        self.handle_item('publisher', self.publisher)
        self.handle_item('publisherurl', self.publisher_url)
        self.handle_item('lastBuildDate', self.last_build_date)
        for value in self.extra_values:
            self.handle_item(value.name, value.content, value.attributes)

        for obj in queryset:
            self.start_object(obj)
            for key, value in obj.iteritems():
                # The is_posted field is used only for building the
                # url and should not actually show up in the
                # final results.
                if key != 'is_posted':
                    self.handle_item(key, value)
            self.handle_item_url(obj)
            self.end_object(obj)
        self.end_serialization()
        return self.getvalue()


class XMLExtraValuesSerializer(ExtraValuesSerializer):
    """ 
    Give default serializer extra functionality. You must pass feed_type when
    calling this function or it will default to XML.
    
    Inputs:
    :ExtraValuesSerializer: object containing specific properites to use.

    The default serializer does not accept calculated values such as those from
    functions such as annotate() or extra(). The XMLExtraSerializer supports
    XML nodes with custom names, serializing of calculated fields, optional
    CDATA wrapping of text fields, as well as a slightly different xml structure
    that is more tailored to a job feed file.
    
    """
    def __init__(self, use_cdata=False, *args, **kwargs):
        super(XMLExtraValuesSerializer, self).__init__(*args, **kwargs)
        kwargs['feed_type'] = 'xml'
        self.use_cdata = use_cdata

    def indent(self, level):
        if self.options.get('indent', None) is not None:
            self.xml.ignorableWhitespace('\n' + ' ' * self.options.get('indent', None) * level)

    def start_serialization(self):
        """
        Start serialization -- open the XML document and the root element.
        """
        self.xml = SimplerXMLGeneratorWithCDATA(self.stream,
                                                self.options.get(
                                                    "encoding",
                                                    settings.DEFAULT_CHARSET))
        self.xml.startDocument()
        self.xml.startElement("source", {})

    def end_serialization(self):
        """
        End serialization -- end the document.
        """
        self.indent(0)
        self.xml.endElement("source")
        self.xml.endDocument()

    def start_object(self, obj):
        """
        Called as each object is handled.
        """
        self.indent(1)
        self.xml.startElement("job", {})

    def end_object(self, obj):
        """
        Called after handling all fields for an object.
        """
        self.indent(1)
        self.xml.endElement("job")

    def finish_handle_item(self, field_name, value, attributes=None):
        self.indent(2)
        if attributes:
            #AttributesImpl applies an xml character escape. & became &amp;
            #This repeated itself in 'next' links &amp;&amp;&amp
            #This is mostly a cosmetic fix, so if it causes problems in other
            #attributes, consider removing rather than trying to fix for
            #special cases
            for key in attributes:
                attributes[key] = unescape(attributes[key])
            attributes = AttributesImpl(attributes)
        else: attributes = {}
        self.xml.startElement(field_name, attributes)
        if self.use_cdata:
            self.xml.write_cdata(unicode(value))
        else:
            self.xml.characters(unicode(value))
        self.xml.endElement(field_name)


class JSONExtraValuesSerializer(ExtraValuesSerializer):
    def __init__(self, **kwargs):
        kwargs['feed_type'] = 'json'
        super(JSONExtraValuesSerializer, self).__init__(**kwargs)

    def start_serialization(self):
        self._current = {} 
        self.objects = []

    def start_object(self, obj):
        self._current = {}

    def end_object(self, obj):
        self.objects.append(self._current)
        self._current = None

    def finish_handle_item(self, field_name, value, attributes=None):
        # Protected types (i.e., primitives like None, numbers, dates,
        # and Decimals) are passed through as is. All other values are
        # converted to unicode string first.
        if attributes is None:
            attributes = {}
        if is_protected_type(value):
            self._current[field_name] = value
        else:
            self._current[field_name] = unicode(value)

    def end_serialization(self):
        json.dump(self.objects, self.stream, **self.options)

    def getvalue(self):
        if callable(getattr(self.stream, 'getvalue', None)):
            return self.stream.getvalue()
