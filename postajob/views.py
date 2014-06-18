from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.decorators import method_decorator

from universal.helpers import get_company
from universal.views import RequestFormViewBase
from universal.decorators import company_has_access
from postajob.forms import (JobForm, ProductForm, ProductGroupingForm,
                            PurchasedProductForm)
from postajob.models import (Job, Product, ProductGrouping, PurchasedJob,
                             PurchasedProduct)


@company_has_access('prm_access')
def jobs_overview(request):
    company = get_company(request)
    data = {'jobs': Job.objects.filter(owner=company)}
    return render_to_response('postajob/jobs_overview.html', data,
                              RequestContext(request))


def purchasedjobs_overview(request):
    company = get_company(request)
    data = {
        'jobs': PurchasedJob.objects.filter(owner=company),
        'products': PurchasedProduct.objects.filter(owner=company),
    }
    return render_to_response('postajob/purchasedjobs_overview.html', data,
                              RequestContext(request))


@company_has_access('product_access')
def products_overview(request):
    company = get_company(request)
    data = {
        'products': Product.objects.filter(owner=company)[:3],
        'product_groupings': ProductGrouping.objects.filter(owner=company)[:3],
        'company': company
    }
    return render_to_response('postajob/products_overview.html', data,
                              RequestContext(request))


@company_has_access('product_access')
def admin_products(request):
    company = get_company(request)
    data = {
        'products': Product.objects.filter(owner=company),
        'company': company,
    }
    return render_to_response('postajob/products.html', data,
                              RequestContext(request))


@company_has_access('product_access')
def admin_groupings(request):
    company = get_company(request)
    data = {
        'product_groupings': ProductGrouping.objects.filter(owner=company),
        'company': company,
    }
    return render_to_response('postajob/productgroups.html', data,
                              RequestContext(request))


class PostajobModelFormMixin(object):
    """
    A mixin for postajob models, since nearly all of them rely on
    owner for filtering by company.

    """
    model = None
    template_name = 'postajob/form.html'

    def get_queryset(self, request):
        kwargs = {'owner__in': request.user.get_companies()}
        self.queryset = self.model.objects.filter(**kwargs)
        return self.queryset

    def get_success_url(self):
        return self.success_url


class JobFormView(PostajobModelFormMixin, RequestFormViewBase):
    form_class = JobForm
    model = Job
    display_name = 'Job'

    success_url = reverse_lazy('jobs_overview')
    add_name = 'job_add'
    update_name = 'job_update'
    delete_name = 'job_delete'

    @method_decorator(company_has_access('prm_access'))
    def dispatch(self, *args, **kwargs):
        """
        Decorators on this function will be run on every request that
        goes through this class.

        """
        return super(JobFormView, self).dispatch(*args, **kwargs)


class ProductFormView(PostajobModelFormMixin, RequestFormViewBase):
    form_class = ProductForm
    model = Product
    display_name = 'Product'

    success_url = reverse_lazy('products_overview')
    add_name = 'product_add'
    update_name = 'product_update'
    delete_name = 'product_delete'

    @method_decorator(company_has_access('product_access'))
    def dispatch(self, *args, **kwargs):
        """
        Decorators on this function will be run on every request that
        goes through this class.

        """
        return super(ProductFormView, self).dispatch(*args, **kwargs)


class ProductGroupingFormView(PostajobModelFormMixin, RequestFormViewBase):
    form_class = ProductGroupingForm
    model = ProductGrouping
    display_name = 'Product Grouping'

    success_url = reverse_lazy('products_overview')
    add_name = 'productgrouping_add'
    update_name = 'productgrouping_update'
    delete_name = 'productgrouping_delete'

    @method_decorator(company_has_access('product_access'))
    def dispatch(self, *args, **kwargs):
        """
        Decorators on this function will be run on every request that
        goes through this class.

        """
        return super(ProductGroupingFormView, self).dispatch(*args, **kwargs)


class PurchasedProductFormView(PostajobModelFormMixin, RequestFormViewBase):
    form_class = PurchasedProductForm
    model = PurchasedProduct
    # The display name is determined by the product id and set in dispatch().
    display_name = '{product} - Billing Information'

    success_url = reverse_lazy('purchasedjobs_overview')
    add_name = 'purchasedproduct_add'
    update_name = 'purchasedproduct_update'
    delete_name = 'purchasedproduct_delete'

    def set_object(self, request):
        self.object = None

    def dispatch(self, *args, **kwargs):
        """
        Decorators on this function will be run on every request that
        goes through this class.

        Determine and set which product is attempting to be purchased.

        """
        # The add url also has the pk for the product they're attempting
        # to purchase.
        self.product = get_object_or_404(Product, pk=kwargs.get('product'))
        self.display_name = self.display_name.format(product=self.product.name)
        return super(PurchasedProductFormView, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(PurchasedProductFormView, self).get_form_kwargs()
        kwargs['product'] = self.product
        return kwargs