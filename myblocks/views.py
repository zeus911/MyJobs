from django.conf import settings
from django.contrib.auth import authenticate
from django.core.urlresolvers import resolve
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic import View

from myblocks.models import Page
from myjobs.helpers import expire_login
from myjobs.models import User
from registration.forms import CustomAuthForm, RegistrationForm


class BlockView(View):
    page = None
    page_type = None

    def get(self, request):
        return self.handle_request(request)

    def handle_request(self, request):
        self.set_page()
        context = {
            'content': self.page.render(request),
            'page': self.page
        }
        return render_to_response('myblocks/myblocks_base.html', context,
                                  context_instance=RequestContext(request))

    def post(self, request):
        return self.handle_request(request)

    def set_page(self):
        try:
            page = Page.objects.filter(site=settings.SITE,
                                       page_type=self.page_type)[0]
        except (Page.DoesNotExist, Page.MultipleObjectsReturned):
            raise Http404
        setattr(self, 'page', page)


class LoginView(BlockView):
    page_type = 'login'

    @staticmethod
    def success_url(request):
        # If a nexturl is specified, use that as the success url.
        if request.REQUEST.get('nexturl'):
            return request.REQUEST.get('nexturl')

        # If we're on a login page, use the homepage as the success url.
        if resolve(request.path).url_name == 'login':
            return '/'

        # If neither of those, we're probably on a standard page that just
        # happens to have a login box, so refresh the current page.
        return request.path

    def post(self, request):
        if request.POST.get('action') == "register":
            form = RegistrationForm(request.POST, auto_id=False)
            if form.is_valid():
                data = form.cleaned_data
                new_user, created = User.objects.create_user(request=request,
                                                             **data)
                user_cache = authenticate(username=data.get('email'),
                                          password=data.get('password1'))
                expire_login(request, user_cache)
                response = HttpResponseRedirect(self.success_url(request))
                response.set_cookie('myguid', new_user.user_guid,
                                    expires=365*24*60*60, domain='.my.jobs')
                return response
            else:
                return HttpResponse(json.dumps(
                    {'errors': form.errors.items()}))

        elif request.POST.get('action') == "login":
            form = CustomAuthForm(data=request.POST)
            if form.is_valid():
                expire_login(request, form.get_user())
                url = request.POST.get('nexturl')
                response = HttpResponseRedirect(self.success_url())
                response.set_cookie('myguid', form.get_user().user_guid,
                                    expires=365*24*60*60, domain='.my.jobs')
                return response
            else:
                return HttpResponse(json.dumps({'errors':
                                                    form.errors.items()}))