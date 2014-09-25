# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'jobListing'
        db.create_table('seo_joblisting', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('titleSlug', self.gf('django.db.models.fields.SlugField')(db_index=True, max_length=200, null=True, blank=True)),
            ('f_title', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('countrySlug', self.gf('django.db.models.fields.SlugField')(db_index=True, max_length=50, null=True, blank=True)),
            ('f_country', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('country_short', self.gf('django.db.models.fields.CharField')(max_length=3, null=True, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('stateSlug', self.gf('django.db.models.fields.SlugField')(db_index=True, max_length=50, null=True, blank=True)),
            ('f_state', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('state_short', self.gf('django.db.models.fields.CharField')(max_length=3, null=True, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('citySlug', self.gf('django.db.models.fields.SlugField')(db_index=True, max_length=50, null=True, blank=True)),
            ('f_city', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('onet_code', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('onet_title', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('onetTitleSlug', self.gf('django.db.models.fields.SlugField')(db_index=True, max_length=200, null=True, blank=True)),
            ('f_onet_title', self.gf('django.db.models.fields.CharField')(max_length=200, null=True, blank=True)),
            ('uid', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
            ('link', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('date_updated', self.gf('django.db.models.fields.DateTimeField')()),
            ('buid', self.gf('django.db.models.fields.IntegerField')()),
            ('hitkey', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('reqid', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('date_new', self.gf('django.db.models.fields.DateTimeField')()),
            ('description', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('seo', ['jobListing'])

        # Adding model 'facet'
        db.create_table('seo_facet', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('facetSlug', self.gf('django.db.models.fields.SlugField')(db_index=True, max_length=200, null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('jobCount', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('seo', ['facet'])

        # Adding M2M table for field childFacet on 'facet'
        db.create_table('seo_facet_childFacet', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_facet', models.ForeignKey(orm['seo.facet'], null=False)),
            ('to_facet', models.ForeignKey(orm['seo.facet'], null=False))
        ))
        db.create_unique('seo_facet_childFacet', ['from_facet_id', 'to_facet_id'])

        # Adding model 'facetRule'
        db.create_table('seo_facetrule', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('facet', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['seo.facet'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('titleTerm', self.gf('django.db.models.fields.CharField')(max_length=800, blank=True)),
            ('cityTerm', self.gf('django.db.models.fields.CharField')(max_length=800, blank=True)),
            ('stateTerm', self.gf('django.db.models.fields.CharField')(max_length=800, blank=True)),
            ('countryTerm', self.gf('django.db.models.fields.CharField')(max_length=800, blank=True)),
            ('keywordTerm', self.gf('django.db.models.fields.CharField')(max_length=800, blank=True)),
        ))
        db.send_create_signal('seo', ['facetRule'])

        # Adding model 'facetJob'
        db.create_table('seo_facetjob', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('facet', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['seo.facet'])),
            ('jobListing', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['seo.jobListing'])),
            ('facetRule', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['seo.facetRule'])),
        ))
        db.send_create_signal('seo', ['facetJob'])

        # Adding model 'styleSheet'
        db.create_table('seo_stylesheet', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('css_body', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('selected', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('useCssBody', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('backgroundColor', self.gf('django.db.models.fields.CharField')(max_length=6, null=True, blank=True)),
            ('fontColor', self.gf('django.db.models.fields.CharField')(default='666666', max_length=6)),
            ('primaryColor', self.gf('django.db.models.fields.CharField')(default='990000', max_length=6)),
            ('secondaryColor', self.gf('django.db.models.fields.CharField')(max_length=6, null=True, blank=True)),
        ))
        db.send_create_signal('seo', ['styleSheet'])

        # Adding model 'Configuration'
        db.create_table('seo_configuration', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('is_staging', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('is_production', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('defaultBlurb', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('defaultBlurbTitle', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('browse_country_show', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('browse_state_show', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('browse_city_show', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('browse_title_show', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('browse_facet_show', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('browse_country_text', self.gf('django.db.models.fields.CharField')(default='Country', max_length=50)),
            ('browse_state_text', self.gf('django.db.models.fields.CharField')(default='State', max_length=50)),
            ('browse_city_text', self.gf('django.db.models.fields.CharField')(default='City', max_length=50)),
            ('browse_title_text', self.gf('django.db.models.fields.CharField')(default='Title', max_length=50)),
            ('browse_facet_text', self.gf('django.db.models.fields.CharField')(default='Job Profiles', max_length=50)),
            ('browse_country_order', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('browse_state_order', self.gf('django.db.models.fields.IntegerField')(default=2)),
            ('browse_city_order', self.gf('django.db.models.fields.IntegerField')(default=3)),
            ('browse_title_order', self.gf('django.db.models.fields.IntegerField')(default=4)),
            ('browse_facet_order', self.gf('django.db.models.fields.IntegerField')(default=5)),
            ('browse_country_default', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('browse_state_default', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('browse_city_default', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('browse_title_default', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('browse_facet_default', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('subNavNumber', self.gf('django.db.models.fields.IntegerField')(default=20)),
            ('disambigNumber', self.gf('django.db.models.fields.IntegerField')(default=10)),
            ('listingNumber', self.gf('django.db.models.fields.IntegerField')(default=10)),
            ('location_tag', self.gf('django.db.models.fields.CharField')(default='jobs', max_length=50)),
            ('title_tag', self.gf('django.db.models.fields.CharField')(default='jobs-in', max_length=50)),
            ('facet_tag', self.gf('django.db.models.fields.CharField')(default='new-jobs', max_length=50)),
            ('meta', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('wide_header', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('header', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('wide_footer', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('footer', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
        ))
        db.send_create_signal('seo', ['Configuration'])

        # Adding M2M table for field styleSheets on 'Configuration'
        db.create_table('seo_configuration_styleSheets', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('configuration', models.ForeignKey(orm['seo.configuration'], null=False)),
            ('stylesheet', models.ForeignKey(orm['seo.stylesheet'], null=False))
        ))
        db.create_unique('seo_configuration_styleSheets', ['configuration_id', 'stylesheet_id'])

        # Adding model 'BusinessUnit'
        db.create_table('seo_businessunit', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('unit_id', self.gf('django.db.models.fields.IntegerField')(max_length=10)),
            ('date_crawled', self.gf('django.db.models.fields.DateTimeField')()),
            ('active', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('seo', ['BusinessUnit'])


    def backwards(self, orm):
        
        # Deleting model 'jobListing'
        db.delete_table('seo_joblisting')

        # Deleting model 'facet'
        db.delete_table('seo_facet')

        # Removing M2M table for field childFacet on 'facet'
        db.delete_table('seo_facet_childFacet')

        # Deleting model 'facetRule'
        db.delete_table('seo_facetrule')

        # Deleting model 'facetJob'
        db.delete_table('seo_facetjob')

        # Deleting model 'styleSheet'
        db.delete_table('seo_stylesheet')

        # Deleting model 'Configuration'
        db.delete_table('seo_configuration')

        # Removing M2M table for field styleSheets on 'Configuration'
        db.delete_table('seo_configuration_styleSheets')

        # Deleting model 'BusinessUnit'
        db.delete_table('seo_businessunit')


    models = {
        'seo.businessunit': {
            'Meta': {'object_name': 'BusinessUnit'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'date_crawled': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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
            'defaultBlurb': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'defaultBlurbTitle': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
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
            'childFacet': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['seo.facet']", 'symmetrical': 'False', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'facetSlug': ('django.db.models.fields.SlugField', [], {'db_index': 'True', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jobCount': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'jobListing': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['seo.jobListing']", 'symmetrical': 'False', 'through': "orm['seo.facetJob']", 'blank': 'True'}),
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
            'link': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
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
