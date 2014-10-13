from django.conf import settings
from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic import View

from myblocks.models import Page


class BlockView(View):
    page = None

    def set_page(self, request):
        return NotImplementedError

    def get(self, request):
        self.set_page(request)
        context = {
            'content': self.page.render(request),
            'page': self.page
        }
        return render_to_response('myblocks/myblocks_base.html', context,
                                  context_instance=RequestContext(request))


class LoginView(BlockView):
    def set_page(self, request):
        try:
            page = Page.objects.filter(site=settings.SITE, page_type='login')[2]
            #page = Page.objects.filter(site=settings.SITE, page_type='job_listing')[0]
        except (Page.DoesNotExist, Page.MultipleObjectsReturned):
            raise Http404
        setattr(self, 'page', page)