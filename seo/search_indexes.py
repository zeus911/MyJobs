from django.utils.encoding import force_unicode

from haystack import indexes
from haystack.constants import ID, DJANGO_CT, DJANGO_ID
from haystack.fields import CharField
from slugify import slugify

from moc_coding import models as moc_models
from seo.models import jobListing, BusinessUnit
from seo.search_backend import get_identifier


class LocationCharField(CharField):
    """Requires a case for location_char in our search backend"""
    field_type = 'location_char'


class TextAndSymbols(CharField):
    """
    Splits only on whitespace, and preserves common symbols.

    """
    field_type = 'text_and_symbols'


class KeywordSearchField(CharField):
    """
    For exact keyword/tag matching. No stemming, case insensitive,
    and preserves common tag chacters # and @
    """
    field_type = 'keyword_query'


class ExactStringField(CharField):
    """
    An exact string field that doesn't need to be faceted or create a duplicate
    text_en and _exact field
    """
    field_type = 'string'

    def __init__(self, *args, **kwargs):
        super(ExactStringField, self).__init__(*args, **kwargs)
        # This attribute is checked in the search backend. If facet_for is
        # blank, the type gets overridden from string to text_en
        self.facet_for = self.model_attr


class StringField(CharField):
    """
    Duplicate of ExactStringField, but doesn't require facet_for, since
    not everything matches up with the model. Doesn't work for indexed fields,
    likely because of some setting in search_backends.py.

    """
    field_type = 'string'


class MultiValueIntegerField(indexes.MultiValueField):
        field_type = 'int'


class JobIndex(indexes.SearchIndex, indexes.Indexable):
    """
    All fields that you want stored will be put here, in django model form
    """
    job_source_name = indexes.CharField()
    buid = indexes.IntegerField(model_attr='buid_id')
    city = LocationCharField(faceted=True, model_attr='city', null=True)
    city_ac = indexes.EdgeNgramField(model_attr='city', null=True, stored=False)
    city_slab = indexes.CharField(faceted=True)
    city_slug = indexes.CharField(model_attr="citySlug", stored=False)
    company = indexes.CharField(faceted=True)
    company_canonical_microsite = indexes.CharField(faceted=True)
    company_enhanced = indexes.BooleanField(indexed=True, stored=True)
    company_member = indexes.BooleanField(indexed=True, stored=True)
    company_digital_strategies_customer = indexes.BooleanField(indexed=True,
                                                               stored=True)
    company_ac = indexes.EdgeNgramField(null=True, stored=False)
    company_slab = indexes.CharField(faceted=True)
    country = LocationCharField(model_attr='country', faceted=True, null=True)
    country_ac = indexes.EdgeNgramField(model_attr='country', null=True)
    country_short = indexes.CharField(model_attr='country_short')
    country_slab = indexes.CharField(faceted=True)
    country_slug = indexes.CharField(model_attr="countrySlug", stored=False)
    date_new = indexes.DateTimeField(model_attr='date_new', null=True,
                                     faceted=True)
    date_updated = indexes.DateTimeField(model_attr='date_updated', null=True,
                                         faceted=True)
    description = KeywordSearchField(model_attr="description", stored=True,
                                     indexed=True)
    full_loc = indexes.CharField(faceted=True, stored=False)
    html_description = indexes.CharField(model_attr="html_description", 
                                         stored=True,
                                         indexed=False)
    link = indexes.CharField(stored=True, indexed=False) 
    location = LocationCharField(model_attr='location', faceted=True, null=True)
    GeoLocation = indexes.LocationField(model_attr='location')
    lat_long_buid_slab = indexes.CharField(faceted=True)
    moc = indexes.MultiValueField(faceted=True, null=True, stored=False)
    mocid = indexes.MultiValueField(null=True)
    moc_slab = indexes.MultiValueField(faceted=True, null=True, stored=False)
    mapped_moc = indexes.MultiValueField(faceted=True, null=True, stored=False)
    mapped_mocid = indexes.MultiValueField(null=True, stored=False)
    mapped_moc_slab = indexes.MultiValueField(faceted=True, null=True,
                                              stored=False)
    onet = indexes.MultiValueField(model_attr='onet_id', faceted=True,
                                   null=True)
    reqid = ExactStringField(model_attr='reqid', null=True)
    salted_date = indexes.DateTimeField(stored=False, null=True)
    state = LocationCharField(model_attr='state', faceted=True, null=True)
    state_ac = indexes.EdgeNgramField(model_attr='state', null=True,
                                      stored=False)
    state_short = indexes.CharField(model_attr='state_short', faceted=True,
                                    null=True)
    state_slab = indexes.CharField(faceted=True)
    state_slug = indexes.CharField(model_attr="stateSlug", stored=False)
    text = TextAndSymbols(document=True, use_template=True, stored=False)
    title = TextAndSymbols(model_attr='title', faceted=True)
    title_ac = indexes.EdgeNgramField(model_attr='title', null=True,
                                      stored=False)
    title_slab = indexes.CharField(faceted=True)
    title_slug = indexes.CharField(model_attr='titleSlug')
    uid = indexes.IntegerField(model_attr='uid')
    guid = ExactStringField(model_attr='guid')
    zipcode = indexes.CharField(model_attr='zipcode', null=True)

    # Fields for post-a-job
    is_posted = indexes.BooleanField()
    on_sites = MultiValueIntegerField()
    apply_info = StringField(indexed=False)

    def get_model(self):
        return jobListing

    def prepare(self, obj):
        """
        Fetches and adds/alters data before indexing.
        """
        self.prepared_data = {
            ID: get_identifier(obj),
            DJANGO_CT: "%s.%s" % (obj._meta.app_label, obj._meta.module_name),
            DJANGO_ID: force_unicode(obj.pk),
        }

        for field_name, field in self.fields.items():
            # Use the possibly overridden name, which will default to the
            # variable name of the field.
            self.prepared_data[field.index_fieldname] = field.prepare(obj)

            if hasattr(self, "prepare_%s" % field_name):
                value = getattr(self, "prepare_%s" % field_name)(obj)
                self.prepared_data[field.index_fieldname] = value

        bu = BusinessUnit.objects.get(id=obj.buid_id)
        co_name = bu.title
        co_slug = bu.title_slug or slugify(co_name)
        co_slab = u"{cs}/careers::{cn}".format(cs=co_slug, cn=co_name)
        self.prepared_data['company'] = co_name
        self.prepared_data['company_ac'] = co_name
        self.prepared_data['company_slab'] = co_slab

        if obj.onet_id:
            mocs = moc_models.Moc.objects.filter(onets__joblisting=obj)
            moc_slab = ["%s/%s/%s/vet-jobs::%s - %s" %
                        (moc.title_slug, moc.code, moc.branch, moc.code,
                         moc.title)
                        for moc in mocs]
            moc_set = [moc.code for moc in mocs]
            mocids = [moc.id for moc in mocs]
            self.prepared_data['mocid'] = mocids
            self.prepared_data['moc_slab'] = moc_slab
            self.prepared_data['moc'] = moc_set

        return self.prepared_data

    def prepare_full_loc(self, obj):
        fields = ['city', 'state', 'location', 'country']
        strings = ['%s::%s' % (f, getattr(obj, f)) for f in fields if
                   getattr(obj, f)]
        return '@@'.join(strings)

    def prepare_country_slab(self, obj):
        return "%s/jobs::%s" % (obj.country_short.lower(), obj.country)

    def prepare_state_slab(self, obj):
        if obj.stateSlug:
            url = "%s/%s/jobs" % (obj.stateSlug, obj.country_short.lower())
            return "%s::%s" % (url, obj.state)

    def prepare_city_slab(self, obj):
        """
        See prepare_state_slab for the reason being the "none"

        The rest of this is storing the facet with or with out state data
        to go along with the city data.

        """
        url = "%s/%s/%s/jobs" % (obj.citySlug, obj.stateSlug,
                                 obj.country_short.lower())
        return "%s::%s" % (url, obj.location)

    def prepare_title_slab(self, obj):
        """
        Creates title slab.

        """
        if obj.titleSlug and obj.titleSlug != "none":
            return "%s/jobs-in::%s" % (obj.titleSlug.strip('-'), obj.title)
