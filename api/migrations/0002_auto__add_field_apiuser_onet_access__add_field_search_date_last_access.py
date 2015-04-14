# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'APIUser.onet_access'
        db.add_column(u'api_apiuser', 'onet_access',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Search.date_last_accessed'
        db.add_column(u'api_search', 'date_last_accessed',
                      self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'APIUser.onet_access'
        db.delete_column(u'api_apiuser', 'onet_access')

        # Deleting field 'Search.date_last_accessed'
        db.delete_column(u'api_search', 'date_last_accessed')


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
            'view_source': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.ViewSource']", 'null': 'True'})
        },
        u'api.citytocentroidmapping': {
            'Meta': {'object_name': 'CityToCentroidMapping'},
            'centroid_lat': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'centroid_lon': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '3'})
        },
        u'api.country': {
            'Meta': {'object_name': 'Country'},
            'country': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'country_code': ('django.db.models.fields.IntegerField', [], {'max_length': '255', 'primary_key': 'True'})
        },
        u'api.industry': {
            'Meta': {'object_name': 'Industry'},
            'industry': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'industry_id': ('django.db.models.fields.IntegerField', [], {'max_length': '255', 'primary_key': 'True'})
        },
        u'api.moc': {
            'Meta': {'ordering': "['branch', 'code']", 'unique_together': "(('code', 'branch'),)", 'object_name': 'Moc', 'db_table': "'moc_coding_moc'"},
            'branch': ('django.db.models.fields.CharField', [], {'max_length': '11'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '20', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'onets': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['api.Onet']", 'symmetrical': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'title_slug': ('django.db.models.fields.SlugField', [], {'max_length': '300'})
        },
        u'api.onet': {
            'Meta': {'unique_together': "(('title', 'code'),)", 'object_name': 'Onet', 'db_table': "'moc_coding_onet'"},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        },
        u'api.search': {
            'Meta': {'object_name': 'Search'},
            'date_last_accessed': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'query': ('django.db.models.fields.TextField', [], {}),
            'solr_params': ('django.db.models.fields.TextField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['api.APIUser']"})
        },
        u'api.user': {
            'Meta': {'object_name': 'User', 'db_table': "'myjobs_user'"},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_disabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_guid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
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
            'zip_code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '7'})
        },
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['api']