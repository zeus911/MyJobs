from django.core.urlresolvers import reverse, resolve
from django.http import HttpResponseRedirect, Http404
from django.views.generic.edit import FormView, ModelFormMixin
from django.views.generic.detail import SingleObjectMixin


class FormViewBase(FormView, ModelFormMixin, SingleObjectMixin):
    """
    A FormView built to handle a single instance of a model.

    """
    request = None
    add_name = None
    update_name = None
    delete_name = None
    display_name = None

    context_object_name = 'item'

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
        if not resolve(self.request.path).url_name == self.add_name:
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