# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'User'
        db.create_table('myjobs_user', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('is_superuser', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('email', self.gf('django.db.models.fields.EmailField')(unique=True, max_length=255, db_index=True)),
            ('date_joined', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('is_staff', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('is_disabled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('user_guid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100, db_index=True)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal(u'api', ['User'])

        # Adding M2M table for field groups on 'User'
        m2m_table_name = db.shorten_name('myjobs_user_groups')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user', models.ForeignKey(orm[u'api.user'], null=False)),
            ('group', models.ForeignKey(orm[u'auth.group'], null=False))
        ))
        db.create_unique(m2m_table_name, ['user_id', 'group_id'])

        # Adding M2M table for field user_permissions on 'User'
        m2m_table_name = db.shorten_name('myjobs_user_user_permissions')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user', models.ForeignKey(orm[u'api.user'], null=False)),
            ('permission', models.ForeignKey(orm[u'auth.permission'], null=False))
        ))
        db.create_unique(m2m_table_name, ['user_id', 'permission_id'])

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
            ('view_source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['api.ViewSource'], null=True)),
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
            ('city', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=3)),
            ('centroid_lat', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('centroid_lon', self.gf('django.db.models.fields.CharField')(max_length=25)),
        ))
        db.send_create_signal(u'api', ['CityToCentroidMapping'])

        # Adding model 'ZipCodeToCentroidMapping'
        db.create_table(u'api_zipcodetocentroidmapping', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('zip_code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=7)),
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
        ))
        db.send_create_signal(u'api', ['Search'])

        # Adding model 'Onet'
        db.create_table('moc_coding_onet', (
            ('title', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=10, primary_key=True)),
        ))
        db.send_create_signal(u'api', ['Onet'])

        # Adding unique constraint on 'Onet', fields ['title', 'code']
        db.create_unique('moc_coding_onet', ['title', 'code'])

        # Adding model 'Moc'
        db.create_table('moc_coding_moc', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=20, db_index=True)),
            ('branch', self.gf('django.db.models.fields.CharField')(max_length=11)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=300)),
            ('title_slug', self.gf('django.db.models.fields.SlugField')(max_length=300)),
        ))
        db.send_create_signal(u'api', ['Moc'])

        # Adding unique constraint on 'Moc', fields ['code', 'branch']
        db.create_unique('moc_coding_moc', ['code', 'branch'])

        # Adding M2M table for field onets on 'Moc'
        m2m_table_name = db.shorten_name('moc_coding_moc_onets')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('moc', models.ForeignKey(orm[u'api.moc'], null=False)),
            ('onet', models.ForeignKey(orm[u'api.onet'], null=False))
        ))
        db.create_unique(m2m_table_name, ['moc_id', 'onet_id'])

        # Adding model 'Industry'
        db.create_table(u'api_industry', (
            ('industry_id', self.gf('django.db.models.fields.IntegerField')(max_length=255, primary_key=True)),
            ('industry', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'api', ['Industry'])

        # Adding model 'Country'
        db.create_table(u'api_country', (
            ('country_code', self.gf('django.db.models.fields.IntegerField')(max_length=255, primary_key=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'api', ['Country'])


    def backwards(self, orm):
        # Removing unique constraint on 'Moc', fields ['code', 'branch']
        db.delete_unique('moc_coding_moc', ['code', 'branch'])

        # Removing unique constraint on 'Onet', fields ['title', 'code']
        db.delete_unique('moc_coding_onet', ['title', 'code'])

        # Deleting model 'User'
        db.delete_table('myjobs_user')

        # Removing M2M table for field groups on 'User'
        db.delete_table(db.shorten_name('myjobs_user_groups'))

        # Removing M2M table for field user_permissions on 'User'
        db.delete_table(db.shorten_name('myjobs_user_user_permissions'))

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

        # Deleting model 'Onet'
        db.delete_table('moc_coding_onet')

        # Deleting model 'Moc'
        db.delete_table('moc_coding_moc')

        # Removing M2M table for field onets on 'Moc'
        db.delete_table(db.shorten_name('moc_coding_moc_onets'))

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