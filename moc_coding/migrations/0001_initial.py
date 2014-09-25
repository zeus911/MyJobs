# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Onet'
        db.create_table('moc_coding_onet', (
            ('title', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=10, primary_key=True)),
        ))
        db.send_create_signal('moc_coding', ['Onet'])

        # Adding unique constraint on 'Onet', fields ['title', 'code']
        db.create_unique('moc_coding_onet', ['title', 'code'])

        # Adding model 'Moc'
        db.create_table('moc_coding_moc', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=20, db_index=True)),
            ('branch', self.gf('django.db.models.fields.CharField')(max_length=11)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('title_slug', self.gf('django.db.models.fields.SlugField')(max_length=300, db_index=True)),
            ('moc_detail', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['moc_coding.MocDetail'], unique=True, null=True)),
        ))
        db.send_create_signal('moc_coding', ['Moc'])

        # Adding unique constraint on 'Moc', fields ['code', 'branch']
        db.create_unique('moc_coding_moc', ['code', 'branch'])

        # Adding M2M table for field onets on 'Moc'
        db.create_table('moc_coding_moc_onets', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('moc', models.ForeignKey(orm['moc_coding.moc'], null=False)),
            ('onet', models.ForeignKey(orm['moc_coding.onet'], null=False))
        ))
        db.create_unique('moc_coding_moc_onets', ['moc_id', 'onet_id'])

        # Adding model 'MocDetail'
        db.create_table('moc_coding_mocdetail', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('primary_value', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('service_branch', self.gf('django.db.models.fields.CharField')(max_length=2)),
            ('military_description', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('civilian_description', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('moc_coding', ['MocDetail'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Moc', fields ['code', 'branch']
        db.delete_unique('moc_coding_moc', ['code', 'branch'])

        # Removing unique constraint on 'Onet', fields ['title', 'code']
        db.delete_unique('moc_coding_onet', ['title', 'code'])

        # Deleting model 'Onet'
        db.delete_table('moc_coding_onet')

        # Deleting model 'Moc'
        db.delete_table('moc_coding_moc')

        # Removing M2M table for field onets on 'Moc'
        db.delete_table('moc_coding_moc_onets')

        # Deleting model 'MocDetail'
        db.delete_table('moc_coding_mocdetail')


    models = {
        'moc_coding.moc': {
            'Meta': {'unique_together': "(('code', 'branch'),)", 'object_name': 'Moc'},
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
