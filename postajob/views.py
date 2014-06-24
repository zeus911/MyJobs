import json

from django.core.urlresolvers import Http404, reverse_lazy, resolve
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.decorators import method_decorator

from universal.helpers import get_company
from universal.views import RequestFormViewBase
from universal.decorators import company_has_access
from mydashboard.models import CompanyUser
from postajob.forms import (JobForm, ProductForm, ProductGroupingForm,
                            PurchasedJobForm, PurchasedProductForm)
from postajob.models import (Job, Product, ProductGrouping, PurchasedJob,
                             PurchasedProduct)


@company_has_access('prm_access')
def jobs_overview(request):
    company = get_company(request)
    data = {'jobs': Job.objects.filter(owner=company)}
    return render_to_response('postajob/jobs_overview.html', data,
                              RequestContext(request))

@company_has_access(None)
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


@company_has_access('product_access')
def order_postajob(request):
    """
    This view will always get two variables and always switches display_order.

    """
    company = get_company(request)
    obj_type = request.GET.get('obj_type')
    # Variables
    if obj_type == "groupings":
        a = ProductGrouping.objects.get(pk=request.GET.get('a'))
        b = ProductGrouping.objects.get(pk=request.GET.get('b'))

        # Swap two variables
        a.display_order, b.display_order = b.display_order, a.display_order

        # Save Objects
        a.save()
        b.save()

    data = {
        'product_groupings': ProductGrouping.objects.filter(owner=company),
        'order': True
    }

    # Render updated rows
    html = render_to_response('postajob/includes/productgroup_rows.html', data,
                              RequestContext(request))
    return html


@company_has_access('product_access')
def is_company_user(request):
    email = request.REQUEST.get('email')
    exists = CompanyUser.objects.filter(user__email=email).exists()
    return HttpResponse(json.dumps(exists))


class PurchaseFormViewBase(RequestFormViewBase):
    purchase_field = None
    purchase_model = None

    def dispatch(self, *args, **kwargs):
        """
        Decorators on this function will be run on every request that
        goes through this class.

        Determine and set which product is attempting to be purchased.

        """
        # The add url also has the pk for the product they're attempting
        # to purchase.
        if kwargs.get('product'):
            self.product = get_object_or_404(self.purchase_model,
                                             pk=kwargs.get('product'))
        else:
            obj = get_object_or_404(self.model, pk=kwargs.get('pk'))
            self.product = getattr(obj, self.purchase_field, None)

        # Set the display name based on the model
        self.display_name = self.display_name.format(product=self.product)

        return super(PurchaseFormViewBase, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(PurchaseFormViewBase, self).get_form_kwargs()
        kwargs['product'] = self.product
        return kwargs


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


class PurchasedJobFormView(PostajobModelFormMixin, PurchaseFormViewBase):
    form_class = PurchasedJobForm
    model = PurchasedJob
    display_name = '{product} Job'

    success_url = reverse_lazy('purchasedjobs_overview')
    add_name = 'purchasedjob_add'
    update_name = 'purchasedjob_update'
    delete_name = 'purchasedjob_delete'

    purchase_field = 'purchased_product'
    purchase_model = PurchasedProduct

    def set_object(self, *args, **kwargs):
        if (not self.product.can_post_more()
                and resolve(self.request.path).url_name == self.add_name):
            # If more jobs can't be posted to the project, don't allow
            # the user to access the add view.
            raise Http404
        return super(PurchasedJobFormView, self).set_object(*args, **kwargs)


class ProductFormView(PostajobModelFormMixin, RequestFormViewBase):
    form_class = ProductForm
    model = Product
    display_name = 'Product'

    success_url = reverse_lazy('product')
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

    success_url = reverse_lazy('productgrouping')
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


class PurchasedProductFormView(PostajobModelFormMixin, PurchaseFormViewBase):
    form_class = PurchasedProductForm
    model = PurchasedProduct
    # The display name is determined by the product id and set in dispatch().
    display_name = '{product} - Billing Information'

    success_url = reverse_lazy('purchasedjobs_overview')
    add_name = 'purchasedproduct_add'
    update_name = 'purchasedproduct_update'
    delete_name = 'purchasedproduct_delete'

    purchase_field = 'product'
    purchase_model = Product

    def set_object(self, request):
        """
        Purchased products can't be edited or deleted, so prevent anyone
        getting an actual object to edit/delete.

        """
        self.object = None
        if resolve(request.path).url_name != 'purchasedproduct_add':
            raise Http404