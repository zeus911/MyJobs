# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'BusinessUnit.date_updated'
        db.add_column('seo_businessunit', 'date_updated', self.gf('django.db.models.fields.DateTimeField')(default=datetime.date(2011, 1, 25)), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'BusinessUnit.date_updated'
        db.delete_column('seo_businessunit', 'date_updated')


    models = {
        'seo.businessunit': {
            'Meta': {'object_name': 'BusinessUnit'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'associated_jobs': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'date_crawled': ('django.db.models.fields.DateTimeField', [], {}),
            'date_updated': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'scheduled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'unit_id': ('django.db.models.fields.IntegerField', [], {'max_length': '10'})
        },
        'seo.configuration': {
            'Meta': {'object_name': 'Configuration'},
            'browse_city_default': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'browse_city_order': ('django.db.models.fields.IntegerField', [], {'default': '3'}),
            'browse_city_show': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'browse_city_text': ('django.db.models.fields.CharField', [], {'default': "'City'", 'max_length': '50'}),
            'browse_country_default': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'browse_country_order': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'browse_country_show': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'browse_country_text': ('django.db.models.fields.CharField', [], {'default': "'Country'", 'max_length': '50'}),
            'browse_facet_default': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'browse_facet_order': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
            'browse_facet_show': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'browse_facet_text': ('django.db.models.fields.CharField', [], {'default': "'Job Profiles'", 'max_length': '50'}),
            'browse_state_default': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'browse_state_order': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'browse_state_show': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'browse_state_text': ('django.db.models.fields.CharField', [], {'default': "'State'", 'max_length': '50'}),
            'browse_title_default': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'browse_title_order': ('django.db.models.fields.IntegerField', [], {'default': '4'}),
            'browse_title_show': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'browse_title_text': ('django.db.models.fields.CharField', [], {'default': "'Title'", 'max_length': '50'}),
            'career_site_link': ('django.db.models.fields.URLField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'career_site_text': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'defaultBlurb': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'defaultBlurbTitle': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'directemployers_link': ('django.db.models.fields.URLField', [], {'default': "'http://directemployers.org'", 'max_length': '200'}),
            'disambigNumber': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'facet_tag': ('django.db.models.fields.CharField', [], {'default': "'new-jobs'", 'max_length': '50'}),
            'footer': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'header': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_production': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_staging': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'listingNumber': ('django.db.models.fields.IntegerField', [], {'default': '10'}),
            'location_tag': ('django.db.models.fields.CharField', [], {'default': "'jobs'", 'max_length': '50'}),
            'meta': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'styleSheets': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['seo.styleSheet']", 'symmetrical': 'False'}),
            'subNavNumber': ('django.db.models.fields.IntegerField', [], {'default': '20'}),
            'title_tag': ('django.db.models.fields.CharField', [], {'default': "'jobs-in'", 'max_length': '50'}),
            'wide_footer': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'wide_header': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'seo.facet': {
            'Meta': {'object_name': 'facet'},
            'always_show': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'childFacet': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['seo.facet']", 'symmetrical': 'False', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'facetSlug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jobListing': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['seo.jobListing']", 'symmetrical': 'False', 'through': "orm['seo.facetJob']", 'blank': 'True'}),
            'show_description': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'show_production': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'seo.facetjob': {
            'Meta': {'object_name': 'facetJob'},
            'facet': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['seo.facet']"}),
            'facetRule': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['seo.facetRule']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jobListing': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['seo.jobListing']"})
        },
        'seo.facetrule': {
            'Meta': {'object_name': 'facetRule'},
            'cityTerm': ('django.db.models.fields.CharField', [], {'max_length': '800', 'blank': 'True'}),
            'countryTerm': ('django.db.models.fields.CharField', [], {'max_length': '800', 'blank': 'True'}),
            'facet': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['seo.facet']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywordTerm': ('django.db.models.fields.CharField', [], {'max_length': '800', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'stateTerm': ('django.db.models.fields.CharField', [], {'max_length': '800', 'blank': 'True'}),
            'titleTerm': ('django.db.models.fields.CharField', [], {'max_length': '800', 'blank': 'True'})
        },
        'seo.googleanalytics': {
            'Meta': {'object_name': 'GoogleAnalytics'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'web_property_id': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'seo.joblisting': {
            'Meta': {'object_name': 'jobListing'},
            'buid': ('django.db.models.fields.IntegerField', [], {}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'citySlug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'countrySlug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'country_short': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'date_new': ('django.db.models.fields.DateTimeField', [], {}),
            'date_updated': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'f_city': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'f_country': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'f_onet_title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'f_state': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'f_title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'hitkey': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'onetTitleSlug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'onet_code': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'onet_title': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'reqid': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'stateSlug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'state_short': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'titleSlug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'uid': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'})
        },
        'seo.stylesheet': {
            'Meta': {'object_name': 'styleSheet'},
            'backgroundColor': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True', 'blank': 'True'}),
            'css_body': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'fontColor': ('django.db.models.fields.CharField', [], {'default': "'666666'", 'max_length': '6'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'primaryColor': ('django.db.models.fields.CharField', [], {'default': "'990000'", 'max_length': '6'}),
            'secondaryColor': ('django.db.models.fields.CharField', [], {'max_length': '6', 'null': 'True', 'blank': 'True'}),
            'selected': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'useCssBody': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['seo']
