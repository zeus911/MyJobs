from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView, ModelFormMixin
from django.views.generic.detail import SingleObjectMixin

from global_helpers import get_company
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


class FormViewBase(FormView, ModelFormMixin, SingleObjectMixin):
    """
    A FormView built to handle a single instance of a model.

    """
    add_name = None
    update_name = None
    delete_name = None
    display_name = None

    context_object_name = 'item'
    template_name = 'postajob/form.html'

    def get_context_data(self, **kwargs):
        if self.object:
            pk = {'pk': self.object.pk}
            kwargs['delete_url'] = reverse(self.delete_name, kwargs=pk)
        kwargs['success_url'] = self.success_url
        kwargs['display_name'] = self.display_name
        return super(FormViewBase, self).get_context_data(**kwargs)

    def delete(self):
        """
        Calls the delete() method on the fetched object and then
        redirects to the success URL.

        """
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)

    def get_queryset(self, request):
        raise NotImplementedError('FormViewBase requires get_queryset().')

    def set_object(self, request):
        if not request.path == reverse(self.add_name):
            queryset = self.get_queryset(request)
            self.object = self.get_object(queryset=queryset)
            if not self.object.user_has_access(request.user):
                raise Http404
        else:
            self.object = None

    def get(self, request, *args, **kwargs):
        self.set_object(request)
        if self.object:
            pk = {'pk': self.object.pk}
            if request.path == reverse(self.delete_name, kwargs=pk):
                    return self.delete()
        return super(FormViewBase, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.set_object(request)
        if self.object:
            pk = {'pk': self.object.pk}
            if request.path == reverse(self.delete_name, kwargs=pk):
                    return self.delete()
        return super(FormViewBase, self).post(request, *args, **kwargs)


class RequestFormViewBase(FormViewBase):
    """
    A FormView for a instance of a model that passes the request along to
    the form.

    """
    def get_form_kwargs(self):
        kwargs = super(RequestFormViewBase, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class PostajobModelFormMixin(object):
    """
    A mixin for postajob models, since nearly all of them rely on
    owner for filtering by company.

    """
    model = None

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