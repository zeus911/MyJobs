# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Education.degree_name'
        db.alter_column(u'myprofile_education', 'degree_name', self.gf('django.db.models.fields.CharField')(default='', max_length=255))

        # Changing field 'Education.education_level_code'
        db.alter_column(u'myprofile_education', 'education_level_code', self.gf('django.db.models.fields.IntegerField')(null=True))

        # Changing field 'Education.education_score'
        db.alter_column(u'myprofile_education', 'education_score', self.gf('django.db.models.fields.CharField')(default='', max_length=255))

        # Changing field 'Education.degree_date'
        db.alter_column(u'myprofile_education', 'degree_date', self.gf('django.db.models.fields.DateField')(null=True))

        # Changing field 'Education.city_name'
        db.alter_column(u'myprofile_education', 'city_name', self.gf('django.db.models.fields.CharField')(default='', max_length=255))

        # Changing field 'Education.degree_minor'
        db.alter_column(u'myprofile_education', 'degree_minor', self.gf('django.db.models.fields.CharField')(default='', max_length=255))

    def backwards(self, orm):

        # Changing field 'Education.degree_name'
        db.alter_column(u'myprofile_education', 'degree_name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'Education.education_level_code'
        db.alter_column(u'myprofile_education', 'education_level_code', self.gf('django.db.models.fields.IntegerField')(default=3))

        # Changing field 'Education.education_score'
        db.alter_column(u'myprofile_education', 'education_score', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'Education.degree_date'
        db.alter_column(u'myprofile_education', 'degree_date', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(1971, 1, 1, 0, 0)))

        # Changing field 'Education.city_name'
        db.alter_column(u'myprofile_education', 'city_name', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

        # Changing field 'Education.degree_minor'
        db.alter_column(u'myprofile_education', 'degree_minor', self.gf('django.db.models.fields.CharField')(max_length=255, null=True))

    models = {
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
        },
        u'myjobs.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'gravatar': ('django.db.models.fields.EmailField', [], {'db_index': 'True', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_disabled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'last_response': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now', 'blank': 'True'}),
            'opt_in_employers': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'opt_in_myjobs': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'password_change': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'profile_completion': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'user_guid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'myprofile.address': {
            'Meta': {'object_name': 'Address', '_ormbases': [u'myprofile.ProfileUnits']},
            'address_line_one': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'address_line_two': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'city_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'country_code': ('django.db.models.fields.CharField', [], {'max_length': '3', 'blank': 'True'}),
            'country_sub_division_code': ('django.db.models.fields.CharField', [], {'max_length': '5', 'blank': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '60', 'blank': 'True'}),
            'postal_code': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            u'profileunits_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['myprofile.ProfileUnits']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'myprofile.education': {
            'Meta': {'object_name': 'Education', '_ormbases': [u'myprofile.ProfileUnits']},
            'city_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'country_code': ('django.db.models.fields.CharField', [], {'max_length': '3', 'blank': 'True'}),
            'country_sub_division_code': ('django.db.models.fields.CharField', [], {'max_length': '5', 'blank': 'True'}),
            'degree_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'degree_major': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'degree_minor': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'degree_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'education_level_code': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'education_score': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'organization_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'profileunits_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['myprofile.ProfileUnits']", 'unique': 'True', 'primary_key': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        u'myprofile.employmenthistory': {
            'Meta': {'object_name': 'EmploymentHistory', '_ormbases': [u'myprofile.ProfileUnits']},
            'city_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'country_code': ('django.db.models.fields.CharField', [], {'max_length': '3', 'null': 'True', 'blank': 'True'}),
            'country_sub_division_code': ('django.db.models.fields.CharField', [], {'max_length': '5', 'blank': 'True'}),
            'current_indicator': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'industry_code': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'job_category_code': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'onet_code': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'organization_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'position_title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'profileunits_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['myprofile.ProfileUnits']", 'unique': 'True', 'primary_key': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {})
        },
        u'myprofile.license': {
            'Meta': {'object_name': 'License', '_ormbases': [u'myprofile.ProfileUnits']},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'license_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'license_type': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'profileunits_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['myprofile.ProfileUnits']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'myprofile.militaryservice': {
            'Meta': {'object_name': 'MilitaryService', '_ormbases': [u'myprofile.ProfileUnits']},
            'branch': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'campaign': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'country_code': ('django.db.models.fields.CharField', [], {'max_length': '3', 'blank': 'True'}),
            'department': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'division': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'end_rank': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'expertise': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'honor': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            u'profileunits_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['myprofile.ProfileUnits']", 'unique': 'True', 'primary_key': 'True'}),
            'service_end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'service_start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'start_rank': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'})
        },
        u'myprofile.name': {
            'Meta': {'object_name': 'Name', '_ormbases': [u'myprofile.ProfileUnits']},
            'family_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'given_name': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'primary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'profileunits_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['myprofile.ProfileUnits']", 'unique': 'True', 'primary_key': 'True'})
        },
        u'myprofile.profileunits': {
            'Meta': {'object_name': 'ProfileUnits'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'date_updated': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['myjobs.User']"})
        },
        u'myprofile.secondaryemail': {
            'Meta': {'object_name': 'SecondaryEmail', '_ormbases': [u'myprofile.ProfileUnits']},
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '255'}),
            'label': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            u'profileunits_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['myprofile.ProfileUnits']", 'unique': 'True', 'primary_key': 'True'}),
            'verified': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'verified_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'myprofile.summary': {
            'Meta': {'object_name': 'Summary', '_ormbases': [u'myprofile.ProfileUnits']},
            'headline': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'profileunits_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['myprofile.ProfileUnits']", 'unique': 'True', 'primary_key': 'True'}),
            'the_summary': ('django.db.models.fields.TextField', [], {'max_length': '2000', 'blank': 'True'})
        },
        u'myprofile.telephone': {
            'Meta': {'object_name': 'Telephone', '_ormbases': [u'myprofile.ProfileUnits']},
            'area_dialing': ('django.db.models.fields.CharField', [], {'max_length': '5', 'blank': 'True'}),
            'channel_code': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'country_dialing': ('django.db.models.fields.CharField', [], {'max_length': '3', 'blank': 'True'}),
            'extension': ('django.db.models.fields.CharField', [], {'max_length': '5', 'blank': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            u'profileunits_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['myprofile.ProfileUnits']", 'unique': 'True', 'primary_key': 'True'}),
            'use_code': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'})
        },
        u'myprofile.volunteerhistory': {
            'Meta': {'object_name': 'VolunteerHistory', '_ormbases': [u'myprofile.ProfileUnits']},
            'city_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'country_code': ('django.db.models.fields.CharField', [], {'max_length': '3', 'blank': 'True'}),
            'country_sub_division_code': ('django.db.models.fields.CharField', [], {'max_length': '5', 'blank': 'True'}),
            'current_indicator': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'organization_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'position_title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'profileunits_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['myprofile.ProfileUnits']", 'unique': 'True', 'primary_key': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {})
        },
        u'myprofile.website': {
            'Meta': {'object_name': 'Website', '_ormbases': [u'myprofile.ProfileUnits']},
            'description': ('django.db.models.fields.TextField', [], {'max_length': '500', 'blank': 'True'}),
            'display_text': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            u'profileunits_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['myprofile.ProfileUnits']", 'unique': 'True', 'primary_key': 'True'}),
            'site_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'uri': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'uri_active': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        }
    }

    complete_apps = ['myprofile']