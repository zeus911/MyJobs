# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Product.num_jobs_allowed'
        db.alter_column(u'postajob_product', 'num_jobs_allowed', self.gf('django.db.models.fields.PositiveIntegerField')())

        # Changing field 'Product.max_job_length'
        db.alter_column(u'postajob_product', 'max_job_length', self.gf('django.db.models.fields.PositiveIntegerField')())

    def backwards(self, orm):

        # Changing field 'Product.num_jobs_allowed'
        db.alter_column(u'postajob_product', 'num_jobs_allowed', self.gf('django.db.models.fields.IntegerField')())

        # Changing field 'Product.max_job_length'
        db.alter_column(u'postajob_product', 'max_job_length', self.gf('django.db.models.fields.IntegerField')())

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
        u'mydashboard.businessunit': {
            'Meta': {'object_name': 'BusinessUnit', 'db_table': "'seo_businessunit'"},
            'id': ('django.db.models.fields.IntegerField', [], {'max_length': '10', 'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'})
        },
        u'mydashboard.company': {
            'Meta': {'ordering': "['name']", 'object_name': 'Company', 'db_table': "'seo_company'"},
            'admins': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['myjobs.User']", 'through': u"orm['mydashboard.CompanyUser']", 'symmetrical': 'False'}),
            'canonical_microsite': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'company_slug': ('django.db.models.fields.SlugField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'digital_strategies_customer': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'enhanced': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'job_source_ids': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['mydashboard.BusinessUnit']", 'symmetrical': 'False'}),
            'linkedin_id': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'logo_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'member': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'og_img': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'prm_access': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'product_access': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'site_package': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['postajob.SitePackage']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            'user_created': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'mydashboard.companyuser': {
            'Meta': {'unique_together': "(('user', 'company'),)", 'object_name': 'CompanyUser'},
            'company': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mydashboard.Company']"}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['myjobs.User']"})
        },
        u'mydashboard.seosite': {
            'Meta': {'ordering': "(u'domain',)", 'object_name': 'SeoSite', 'db_table': "'seo_seosite'", '_ormbases': [u'sites.Site']},
            'business_units': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['mydashboard.BusinessUnit']", 'null': 'True', 'blank': 'True'}),
            'site_package': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['postajob.SitePackage']", 'null': 'True', 'on_delete': 'models.SET_NULL'}),
            u'site_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['sites.Site']", 'unique': 'True', 'primary_key': 'True'}),
            'site_title': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200', 'blank': 'True'}),
            'view_sources': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mydashboard.ViewSource']", 'null': 'True', 'blank': 'True'})
        },
        u'mydashboard.viewsource': {
            'Meta': {'object_name': 'ViewSource', 'db_table': "'seo_viewsource'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '200'}),
            'view_source': ('django.db.models.fields.IntegerField', [], {'default': "''", 'max_length': '20'})
        },
        u'myjobs.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'deactivate_type': ('django.db.models.fields.CharField', [], {'default': "'none'", 'max_length': '11'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'gravatar': ('django.db.models.fields.EmailField', [], {'db_index': 'True', 'max_length': '255', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
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
            'source': ('django.db.models.fields.CharField', [], {'default': "'https://secure.my.jobs'", 'max_length': '255'}),
            'timezone': ('django.db.models.fields.CharField', [], {'default': "'America/New_York'", 'max_length': '255'}),
            'user_guid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"})
        },
        u'postajob.companyprofile': {
            'Meta': {'object_name': 'CompanyProfile'},
            'address_line_one': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'address_line_two': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'authorize_net_login': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'authorize_net_transaction_key': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'company': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['mydashboard.Company']", 'unique': 'True'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'customer_of': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'customer'", 'null': 'True', 'symmetrical': 'False', 'to': u"orm['mydashboard.Company']"}),
            'email_on_request': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        u'postajob.invoice': {
            'Meta': {'object_name': 'Invoice'},
            'address_line_one': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'address_line_two': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'card_exp_date': ('django.db.models.fields.DateField', [], {}),
            'card_last_four': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owner'", 'to': u"orm['mydashboard.Company']"}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'transaction': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'postajob.job': {
            'Meta': {'object_name': 'Job'},
            'apply_info': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'apply_link': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'autorenew': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'country': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'country_short': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['myjobs.User']"}),
            'date_expired': ('django.db.models.fields.DateField', [], {}),
            'date_new': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'date_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'guid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_expired': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_syndicated': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mydashboard.Company']"}),
            'reqid': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'site_packages': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['postajob.SitePackage']", 'null': 'True', 'symmetrical': 'False'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'state_short': ('django.db.models.fields.CharField', [], {'max_length': '3'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'zipcode': ('django.db.models.fields.CharField', [], {'max_length': '15', 'blank': 'True'})
        },
        u'postajob.offlineproduct': {
            'Meta': {'object_name': 'OfflineProduct'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'offline_purchase': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['postajob.OfflinePurchase']"}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['postajob.Product']"}),
            'product_quantity': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'})
        },
        u'postajob.offlinepurchase': {
            'Meta': {'object_name': 'OfflinePurchase'},
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'created'", 'to': u"orm['mydashboard.CompanyUser']"}),
            'created_on': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['postajob.Invoice']", 'null': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mydashboard.Company']"}),
            'products': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['postajob.Product']", 'through': u"orm['postajob.OfflineProduct']", 'symmetrical': 'False'}),
            'redeemed_by': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'redeemed'", 'null': 'True', 'to': u"orm['mydashboard.CompanyUser']"}),
            'redeemed_on': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'redemption_uid': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'postajob.package': {
            'Meta': {'object_name': 'Package'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'postajob.product': {
            'Meta': {'object_name': 'Product'},
            'cost': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'featured': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_archived': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_displayed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'max_job_length': ('django.db.models.fields.PositiveIntegerField', [], {'default': '30'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'num_jobs_allowed': ('django.db.models.fields.PositiveIntegerField', [], {'default': '5'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mydashboard.Company']"}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['postajob.Package']"}),
            'posting_window_length': ('django.db.models.fields.IntegerField', [], {'default': '30'}),
            'requires_approval': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'postajob.productgrouping': {
            'Meta': {'ordering': "['display_order']", 'object_name': 'ProductGrouping'},
            'display_order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'display_title': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'explanation': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_displayed': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mydashboard.Company']"}),
            'products': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['postajob.Product']", 'null': 'True', 'through': u"orm['postajob.ProductOrder']", 'symmetrical': 'False'})
        },
        u'postajob.productorder': {
            'Meta': {'unique_together': "(('product', 'group'),)", 'object_name': 'ProductOrder'},
            'display_order': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['postajob.ProductGrouping']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['postajob.Product']"})
        },
        u'postajob.purchasedjob': {
            'Meta': {'object_name': 'PurchasedJob', '_ormbases': [u'postajob.Job']},
            'is_approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'job_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['postajob.Job']", 'unique': 'True', 'primary_key': 'True'}),
            'max_expired_date': ('django.db.models.fields.DateField', [], {}),
            'purchased_product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['postajob.PurchasedProduct']"})
        },
        u'postajob.purchasedproduct': {
            'Meta': {'object_name': 'PurchasedProduct'},
            'expiration_date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['postajob.Invoice']"}),
            'is_approved': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'jobs_remaining': ('django.db.models.fields.IntegerField', [], {}),
            'max_job_length': ('django.db.models.fields.IntegerField', [], {}),
            'num_jobs_allowed': ('django.db.models.fields.IntegerField', [], {}),
            'offline_purchase': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['postajob.OfflinePurchase']", 'null': 'True', 'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mydashboard.Company']"}),
            'paid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['postajob.Product']"}),
            'purchase_amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'purchase_date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        u'postajob.request': {
            'Meta': {'object_name': 'Request'},
            'action_taken': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'made_on': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mydashboard.Company']"})
        },
        u'postajob.sitepackage': {
            'Meta': {'object_name': 'SitePackage', '_ormbases': [u'postajob.Package']},
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['mydashboard.Company']", 'null': 'True', 'blank': 'True'}),
            u'package_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['postajob.Package']", 'unique': 'True', 'primary_key': 'True'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['mydashboard.SeoSite']", 'null': 'True', 'symmetrical': 'False'})
        },
        u'sites.site': {
            'Meta': {'ordering': "(u'domain',)", 'object_name': 'Site', 'db_table': "u'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['postajob']