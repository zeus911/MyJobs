# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'APIUser'
        db.create_table(u'api_apiuser', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('company', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('key', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('first_name', self.gf('django.db.models.fields.CharField')(default='', max_length=200, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(default='', max_length=200, blank=True)),
            ('email', self.gf('django.db.models.fields.CharField')(default='', max_length=200, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(default='', max_length=30, blank=True)),
            ('scope', self.gf('django.db.models.fields.CharField')(default=1, max_length=1)),
            ('jv_api_access', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('onet_access', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('view_source', self.gf('django.db.models.fields.IntegerField')(null=True, db_column='view_source_id')),
            ('disable', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True)),
            ('date_disabled', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'api', ['APIUser'])

        # Adding model 'ViewSource'
        db.create_table('redirect_viewsource', (
            ('view_source_id', self.gf('django.db.models.fields.IntegerField')(default=None, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('friendly_name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal(u'api', ['ViewSource'])

        # Adding model 'CityToCentroidMapping'
        db.create_table(u'api_citytocentroidmapping', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=3, db_index=True)),
            ('centroid_lat', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('centroid_lon', self.gf('django.db.models.fields.CharField')(max_length=25)),
        ))
        db.send_create_signal(u'api', ['CityToCentroidMapping'])

        # Adding model 'ZipCodeToCentroidMapping'
        db.create_table(u'api_zipcodetocentroidmapping', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('zip_code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=7, db_index=True)),
            ('centroid_lat', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('centroid_lon', self.gf('django.db.models.fields.CharField')(max_length=25)),
        ))
        db.send_create_signal(u'api', ['ZipCodeToCentroidMapping'])

        # Adding model 'Search'
        db.create_table(u'api_search', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('query', self.gf('django.db.models.fields.TextField')()),
            ('solr_params', self.gf('django.db.models.fields.TextField')()),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.APIUser'])),
            ('date_last_accessed', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, db_index=True, blank=True)),
        ))
        db.send_create_signal(u'api', ['Search'])

        # Adding model 'Industry'
        db.create_table(u'api_industry', (
            ('industry_id', self.gf('django.db.models.fields.IntegerField')(max_length=255, primary_key=True)),
            ('industry', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
        ))
        db.send_create_signal(u'api', ['Industry'])

        # Adding model 'Country'
        db.create_table(u'api_country', (
            ('country_code', self.gf('django.db.models.fields.IntegerField')(max_length=255, primary_key=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=255, db_index=True)),
        ))
        db.send_create_signal(u'api', ['Country'])


    def backwards(self, orm):
        # Deleting model 'APIUser'
        db.delete_table(u'api_apiuser')

        # Deleting model 'ViewSource'
        db.delete_table('redirect_viewsource')

        # Deleting model 'CityToCentroidMapping'
        db.delete_table(u'api_citytocentroidmapping')

        # Deleting model 'ZipCodeToCentroidMapping'
        db.delete_table(u'api_zipcodetocentroidmapping')

        # Deleting model 'Search'
        db.delete_table(u'api_search')

        # Deleting model 'Industry'
        db.delete_table(u'api_industry')

        # Deleting model 'Country'
        db.delete_table(u'api_country')


    models = {
        u'api.apiuser': {
            'Meta': {'object_name': 'APIUser'},
            'company': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            'date_disabled': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'disable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'email': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'jv_api_access': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'last_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'onet_access': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'phone': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '30', 'blank': 'True'}),
            'scope': ('django.db.models.fields.CharField', [], {'default': '1', 'max_length': '1'}),
            'view_source': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'db_column': "'view_source_id'"})
        },
        u'api.citytocentroidmapping': {
            'Meta': {'object_name': 'CityToCentroidMapping'},
            'centroid_lat': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'centroid_lon': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '3', 'db_index': 'True'})
        },
        u'api.country': {
            'Meta': {'object_name': 'Country'},
            'country': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'country_code': ('django.db.models.fields.IntegerField', [], {'max_length': '255', 'primary_key': 'True'})
        },
        u'api.industry': {
            'Meta': {'object_name': 'Industry'},
            'industry': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'}),
            'industry_id': ('django.db.models.fields.IntegerField', [], {'max_length': '255', 'primary_key': 'True'})
        },
        u'api.search': {
            'Meta': {'object_name': 'Search'},
            'date_last_accessed': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'query': ('django.db.models.fields.TextField', [], {}),
            'solr_params': ('django.db.models.fields.TextField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.APIUser']"})
        },
        u'api.viewsource': {
            'Meta': {'object_name': 'ViewSource', 'db_table': "'redirect_viewsource'"},
            'friendly_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'view_source_id': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'primary_key': 'True'})
        },
        u'api.zipcodetocentroidmapping': {
            'Meta': {'object_name': 'ZipCodeToCentroidMapping'},
            'centroid_lat': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'centroid_lon': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'zip_code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '7', 'db_index': 'True'})
        }
    }

    complete_apps = ['api']