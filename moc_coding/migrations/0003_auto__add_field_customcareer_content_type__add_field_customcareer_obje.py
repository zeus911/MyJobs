# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'CustomCareer.content_type'
        db.add_column('moc_coding_customcareer', 'content_type', self.gf('django.db.models.fields.related.ForeignKey')(default=0, to=orm['contenttypes.ContentType']), keep_default=False)

        # Adding field 'CustomCareer.object_id'
        db.add_column('moc_coding_customcareer', 'object_id', self.gf('django.db.models.fields.PositiveIntegerField')(default=0), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'CustomCareer.content_type'
        db.delete_column('moc_coding_customcareer', 'content_type_id')

        # Deleting field 'CustomCareer.object_id'
        db.delete_column('moc_coding_customcareer', 'object_id')


    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'moc_coding.customcareer': {
            'Meta': {'object_name': 'CustomCareer'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'moc': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['moc_coding.Moc']"}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'onet': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['moc_coding.Onet']"})
        },
        'moc_coding.moc': {
            'Meta': {'ordering': "['branch', 'code']", 'unique_together': "(('code', 'branch'),)", 'object_name': 'Moc'},
            'branch': ('django.db.models.fields.CharField', [], {'max_length': '11'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '20', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'moc_detail': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['moc_coding.MocDetail']", 'unique': 'True', 'null': 'True'}),
            'onets': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['moc_coding.Onet']", 'symmetrical': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '300'}),
            'title_slug': ('django.db.models.fields.SlugField', [], {'max_length': '300', 'db_index': 'True'})
        },
        'moc_coding.mocdetail': {
            'Meta': {'object_name': 'MocDetail'},
            'civilian_description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'military_description': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'primary_value': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'service_branch': ('django.db.models.fields.CharField', [], {'max_length': '2'})
        },
        'moc_coding.onet': {
            'Meta': {'unique_together': "(('title', 'code'),)", 'object_name': 'Onet'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        }
    }

    complete_apps = ['moc_coding']
