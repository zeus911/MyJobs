from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.decorators import method_decorator

from universal.helpers import get_company
from universal.views import RequestFormViewBase
from myjobs.decorators import user_is_allowed
from postajob.forms import (JobForm, ProductForm, ProductGroupingForm)
from postajob.models import (Job, Product, ProductGrouping)


is_company_user = lambda u: u.companyuser_set.all().count() >= 1


@user_is_allowed()
@user_passes_test(is_company_user)
def jobs_overview(request):
    company = get_company(request)
    data = {'jobs': Job.objects.filter(owner=company)}
    return render_to_response('postajob/jobs_overview.html', data,
                              RequestContext(request))


@user_is_allowed()
@user_passes_test(is_company_user)
def products_overview(request):
    company = get_company(request)
    data = {
        'products': Product.objects.filter(owner=company),
        'product_groupings': ProductGrouping.objects.filter(owner=company)
    }
    return render_to_response('postajob/products_overview.html', data,
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


class JobFormView(PostajobModelFormMixin, RequestFormViewBase):
    form_class = JobForm
    model = Job
    display_name = 'Job'

    success_url = reverse_lazy('jobs_overview')
    add_name = 'job_add'
    update_name = 'job_update'
    delete_name = 'job_delete'

    @method_decorator(user_is_allowed())
    @method_decorator(user_passes_test(is_company_user))
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


class ProductGroupingFormView(PostajobModelFormMixin, RequestFormViewBase):
    form_class = ProductGroupingForm
    model = ProductGrouping
    display_name = 'Product Grouping'

    success_url = reverse_lazy('products_overview')
    add_name = 'productgrouping_add'
    update_name = 'productgrouping_update'
    delete_name = 'productgrouping_delete'