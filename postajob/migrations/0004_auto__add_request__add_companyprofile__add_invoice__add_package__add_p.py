# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.conf import settings
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        if settings.DATABASES['default']['ENGINE'] == 'django.db.backends.mysql':
            db.delete_foreign_key('postajob_product', 'site_package_id')
            db.delete_foreign_key('postajob_job_site_packages', 'sitepackage_id')
            db.delete_foreign_key('postajob_sitepackage_sites', 'sitepackage_id')
            db.delete_foreign_key('seo_company', 'site_package_id')
            db.delete_foreign_key('seo_seosite', 'site_package_id')
            db.execute('ALTER TABLE postajob_sitepackage CHANGE id id INT(10) UNSIGNED NOT NULL')
        db.delete_primary_key('postajob_sitepackage')


        # Adding model 'Request'
        db.create_table(u'postajob_request', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.IntegerField')()),
            ('action_taken', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'postajob', ['Request'])

        # Adding model 'CompanyProfile'
        db.create_table(u'postajob_companyprofile', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('company', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['mydashboard.Company'], unique=True)),
            ('address_line_one', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('address_line_two', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('zipcode', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('authorize_net_login', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('authorize_net_transaction_key', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal(u'postajob', ['CompanyProfile'])

        # Adding M2M table for field customer_of on 'CompanyProfile'
        m2m_table_name = db.shorten_name(u'postajob_companyprofile_customer_of')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('companyprofile', models.ForeignKey(orm[u'postajob.companyprofile'], null=False)),
            ('company', models.ForeignKey(orm[u'mydashboard.company'], null=False))
        ))
        db.create_unique(m2m_table_name, ['companyprofile_id', 'company_id'])

        # Adding model 'Invoice'
        db.create_table(u'postajob_invoice', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('transaction', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('card_last_four', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('card_exp_date', self.gf('django.db.models.fields.DateField')()),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('address_line_one', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('address_line_two', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('city', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('state', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('country', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('zipcode', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='owner', to=orm['mydashboard.Company'])),
        ))
        db.send_create_signal(u'postajob', ['Invoice'])

        # Adding model 'Package'
        db.create_table(u'postajob_package', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
        ))
        db.send_create_signal(u'postajob', ['Package'])

        # Adding model 'ProductOrder'
        db.create_table(u'postajob_productorder', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['postajob.Product'])),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['postajob.ProductGrouping'])),
            ('display_order', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
        ))
        db.send_create_signal(u'postajob', ['ProductOrder'])

        # Adding unique constraint on 'ProductOrder', fields ['product', 'group']
        db.create_unique(u'postajob_productorder', ['product_id', 'group_id'])

        # Adding model 'OfflineProduct'
        db.create_table(u'postajob_offlineproduct', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['postajob.Product'])),
            ('offline_purchase', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['postajob.OfflinePurchase'])),
            ('product_quantity', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
        ))
        db.send_create_signal(u'postajob', ['OfflineProduct'])

        # Adding model 'OfflinePurchase'
        db.create_table(u'postajob_offlinepurchase', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('invoice', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['postajob.Invoice'])),
            ('redemption_uid', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name='created', to=orm['mydashboard.CompanyUser'])),
            ('created_on', self.gf('django.db.models.fields.DateField')(auto_now_add=True, blank=True)),
            ('redeemed_by', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='redeemed', null=True, to=orm['mydashboard.CompanyUser'])),
            ('redeemed_on', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'postajob', ['OfflinePurchase'])

        # Adding field 'PurchasedProduct.invoice'
        db.add_column(u'postajob_purchasedproduct', 'invoice',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['postajob.Invoice']),
                      keep_default=False)

        # Adding field 'PurchasedProduct.is_approved'
        db.add_column(u'postajob_purchasedproduct', 'is_approved',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'PurchasedProduct.paid'
        db.add_column(u'postajob_purchasedproduct', 'paid',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'PurchasedProduct.purchase_amount'
        db.add_column(u'postajob_purchasedproduct', 'purchase_amount',
                      self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=20, decimal_places=2),
                      keep_default=False)

        # Adding field 'PurchasedProduct.expiration_date'
        db.add_column(u'postajob_purchasedproduct', 'expiration_date',
                      self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2014, 7, 1, 0, 0)),
                      keep_default=False)

        # Adding field 'PurchasedProduct.num_jobs_allowed'
        db.add_column(u'postajob_purchasedproduct', 'num_jobs_allowed',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'PurchasedProduct.max_job_length'
        db.add_column(u'postajob_purchasedproduct', 'max_job_length',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'PurchasedProduct.jobs_remaining'
        db.add_column(u'postajob_purchasedproduct', 'jobs_remaining',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Deleting field 'ProductGrouping.score'
        db.delete_column(u'postajob_productgrouping', 'score')

        # Deleting field 'ProductGrouping.grouping_name'
        db.delete_column(u'postajob_productgrouping', 'grouping_name')

        # Adding field 'ProductGrouping.display_order'
        db.add_column(u'postajob_productgrouping', 'display_order',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'ProductGrouping.display_title'
        db.add_column(u'postajob_productgrouping', 'display_title',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255),
                      keep_default=False)

        # Adding field 'ProductGrouping.explanation'
        db.add_column(u'postajob_productgrouping', 'explanation',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)

        # Adding field 'ProductGrouping.name'
        db.add_column(u'postajob_productgrouping', 'name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255),
                      keep_default=False)

        # Adding field 'ProductGrouping.owner'
        db.add_column(u'postajob_productgrouping', 'owner',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['mydashboard.Company']),
                      keep_default=False)

        # Adding field 'ProductGrouping.is_displayed'
        db.add_column(u'postajob_productgrouping', 'is_displayed',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Removing M2M table for field products on 'ProductGrouping'
        db.delete_table(db.shorten_name(u'postajob_productgrouping_products'))

        # Deleting field 'Product.site_package'
        db.delete_column(u'postajob_product', 'site_package_id')

        # Adding field 'Product.package'
        db.add_column(u'postajob_product', 'package',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['postajob.Package']),
                      keep_default=False)

        # Adding field 'Product.name'
        db.add_column(u'postajob_product', 'name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True),
                      keep_default=False)

        # Adding field 'Product.description'
        db.add_column(u'postajob_product', 'description',
                      self.gf('django.db.models.fields.TextField')(default=''),
                      keep_default=False)

        # Adding field 'Product.featured'
        db.add_column(u'postajob_product', 'featured',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Product.requires_approval'
        db.add_column(u'postajob_product', 'requires_approval',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'Product.is_archived'
        db.add_column(u'postajob_product', 'is_archived',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Product.is_displayed'
        db.add_column(u'postajob_product', 'is_displayed',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Product.notes'
        db.add_column(u'postajob_product', 'notes',
                      self.gf('django.db.models.fields.TextField')(default='', blank=True),
                      keep_default=False)

        # Adding field 'SitePackage.package_ptr'
        db.add_column(u'postajob_sitepackage', u'package_ptr',
                      self.gf('django.db.models.fields.related.OneToOneField')(default=1, to=orm['postajob.Package'], unique=True, primary_key=True),
                      keep_default=False)

        # Adding field 'SitePackage.owner'
        db.add_column(u'postajob_sitepackage', 'owner',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['mydashboard.Company'], null=True, blank=True),
                      keep_default=False)

        # Deleting field 'Job.company'
        db.delete_column(u'postajob_job', 'company_id')

        # Adding field 'Job.owner'
        db.add_column(u'postajob_job', 'owner',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['mydashboard.Company']),
                      keep_default=False)

        # Adding field 'Job.created_by'
        db.add_column(u'postajob_job', 'created_by',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['myjobs.User']),
                      keep_default=False)


    def backwards(self, orm):
        # Removing unique constraint on 'ProductOrder', fields ['product', 'group']
        db.delete_unique(u'postajob_productorder', ['product_id', 'group_id'])

        # Deleting model 'Request'
        db.delete_table(u'postajob_request')

        # Deleting model 'CompanyProfile'
        db.delete_table(u'postajob_companyprofile')

        # Removing M2M table for field customer_of on 'CompanyProfile'
        db.delete_table(db.shorten_name(u'postajob_companyprofile_customer_of'))

        # Deleting model 'Invoice'
        db.delete_table(u'postajob_invoice')

        # Deleting model 'Package'
        db.delete_table(u'postajob_package')

        # Deleting model 'ProductOrder'
        db.delete_table(u'postajob_productorder')

        # Deleting model 'OfflineProduct'
        db.delete_table(u'postajob_offlineproduct')

        # Deleting model 'OfflinePurchase'
        db.delete_table(u'postajob_offlinepurchase')

        # Deleting field 'PurchasedProduct.invoice'
        db.delete_column(u'postajob_purchasedproduct', 'invoice_id')

        # Deleting field 'PurchasedProduct.is_approved'
        db.delete_column(u'postajob_purchasedproduct', 'is_approved')

        # Deleting field 'PurchasedProduct.paid'
        db.delete_column(u'postajob_purchasedproduct', 'paid')

        # Deleting field 'PurchasedProduct.purchase_amount'
        db.delete_column(u'postajob_purchasedproduct', 'purchase_amount')

        # Deleting field 'PurchasedProduct.expiration_date'
        db.delete_column(u'postajob_purchasedproduct', 'expiration_date')

        # Deleting field 'PurchasedProduct.num_jobs_allowed'
        db.delete_column(u'postajob_purchasedproduct', 'num_jobs_allowed')

        # Deleting field 'PurchasedProduct.max_job_length'
        db.delete_column(u'postajob_purchasedproduct', 'max_job_length')

        # Deleting field 'PurchasedProduct.jobs_remaining'
        db.delete_column(u'postajob_purchasedproduct', 'jobs_remaining')

        # Adding field 'ProductGrouping.score'
        db.add_column(u'postajob_productgrouping', 'score',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'ProductGrouping.grouping_name'
        db.add_column(u'postajob_productgrouping', 'grouping_name',
                      self.gf('django.db.models.fields.CharField')(default='', max_length=255),
                      keep_default=False)

        # Deleting field 'ProductGrouping.display_order'
        db.delete_column(u'postajob_productgrouping', 'display_order')

        # Deleting field 'ProductGrouping.display_title'
        db.delete_column(u'postajob_productgrouping', 'display_title')

        # Deleting field 'ProductGrouping.explanation'
        db.delete_column(u'postajob_productgrouping', 'explanation')

        # Deleting field 'ProductGrouping.name'
        db.delete_column(u'postajob_productgrouping', 'name')

        # Deleting field 'ProductGrouping.owner'
        db.delete_column(u'postajob_productgrouping', 'owner_id')

        # Deleting field 'ProductGrouping.is_displayed'
        db.delete_column(u'postajob_productgrouping', 'is_displayed')

        # Adding M2M table for field products on 'ProductGrouping'
        m2m_table_name = db.shorten_name(u'postajob_productgrouping_products')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('productgrouping', models.ForeignKey(orm[u'postajob.productgrouping'], null=False)),
            ('product', models.ForeignKey(orm[u'postajob.product'], null=False))
        ))
        db.create_unique(m2m_table_name, ['productgrouping_id', 'product_id'])

        # Adding field 'Product.site_package'
        db.add_column(u'postajob_product', 'site_package',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['postajob.SitePackage'], null=True),
                      keep_default=False)

        # Deleting field 'Product.package'
        db.delete_column(u'postajob_product', 'package_id')

        # Deleting field 'Product.name'
        db.delete_column(u'postajob_product', 'name')

        # Deleting field 'Product.description'
        db.delete_column(u'postajob_product', 'description')

        # Deleting field 'Product.featured'
        db.delete_column(u'postajob_product', 'featured')

        # Deleting field 'Product.requires_approval'
        db.delete_column(u'postajob_product', 'requires_approval')

        # Deleting field 'Product.is_archived'
        db.delete_column(u'postajob_product', 'is_archived')

        # Deleting field 'Product.is_displayed'
        db.delete_column(u'postajob_product', 'is_displayed')

        # Deleting field 'Product.notes'
        db.delete_column(u'postajob_product', 'notes')

        # Deleting field 'SitePackage.package_ptr'
        db.delete_column(u'postajob_sitepackage', u'package_ptr_id')

        # Deleting field 'SitePackage.owner'
        db.delete_column(u'postajob_sitepackage', 'owner_id')

        # Adding field 'Job.company'
        db.add_column(u'postajob_job', 'company',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=1, to=orm['mydashboard.Company']),
                      keep_default=False)

        # Deleting field 'Job.owner'
        db.delete_column(u'postajob_job', 'owner_id')

        # Deleting field 'Job.created_by'
        db.delete_column(u'postajob_job', 'created_by_id')


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
            'Meta': {'object_name': 'Company', 'db_table': "'seo_company'"},
            'admins': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['myjobs.User']", 'through': u"orm['mydashboard.CompanyUser']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'}),
            'job_source_ids': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['mydashboard.BusinessUnit']", 'symmetrical': 'False'}),
            'member': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '200'}),
            'prm_access': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'product_access': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'site_package': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['postajob.SitePackage']", 'null': 'True', 'on_delete': 'models.SET_NULL'})
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
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['postajob.Invoice']"}),
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
            'max_job_length': ('django.db.models.fields.IntegerField', [], {'default': '30'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'notes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'num_jobs_allowed': ('django.db.models.fields.IntegerField', [], {'default': '5'}),
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
            'object_id': ('django.db.models.fields.IntegerField', [], {})
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