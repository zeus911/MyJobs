from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView, ModelFormMixin
from django.views.generic.detail import SingleObjectMixin

from myjobs.decorators import user_is_allowed
from postajob.forms import JobForm
from postajob.models import Job


is_company_user = lambda u: u.companyuser_set.all().count() >= 1


@user_is_allowed()
@user_passes_test(is_company_user)
def jobs_overview(request):
    data = {}
    return render_to_response('postajob/jobs_overview.html', data,
                              RequestContext(request))


class JobFormView(FormView, ModelFormMixin, SingleObjectMixin):
    context_object_name = 'job'
    form_class = JobForm
    model = Job
    success_url = reverse_lazy('jobs_overview')
    template_name = 'postajob/form.html'

    def delete(self):
        """
        Calls the delete() method on the fetched object and then
        redirects to the success URL.

        """
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)

    def get_form_kwargs(self):
        """
        Allows for passing the request along to the JobForm so the JobForm
        can have access to the user.

        """
        kwargs = super(JobFormView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get(self, request, *args, **kwargs):
        if not request.path.startswith(reverse('job_add')):
            self.object = self.get_object()
            pk = {'pk': self.object.pk}
            if request.path.startswith(reverse('job_delete', kwargs=pk)):
                return self.delete()
        else:
            self.object = None
        return super(JobFormView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not request.path.startswith(reverse('job_add')):
            self.object = self.get_object()
            pk = {'pk': self.object.pk}
            if request.path.startswith(reverse('job_delete', kwargs=pk)):
                return self.delete()
        else:
            self.object = None
        return super(JobFormView, self).post(request, *args, **kwargs)

    @method_decorator(user_is_allowed())
    @method_decorator(user_passes_test(is_company_user))
    def dispatch(self, *args, **kwargs):
        """
        Decorators on this function will be run on every request that
        goes through this class.

        """
        return super(JobFormView, self).dispatch(*args, **kwargs)

