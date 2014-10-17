from django.conf import settings
from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic import View

from myblocks.models import Page


class BlockView(View):
    page = None
    page_type = None

    def get(self, request):
        return self.handle_request(request)

    def handle_request(self, request):
        if not self.page:
            self.set_page()
        context = {
            'content': self.page.render(request),
            'page': self.page
        }
        return render_to_response('myblocks/myblocks_base.html', context,
                                  context_instance=RequestContext(request))

    def post(self, request):
        self.set_page()
        for block in self.page.all_blocks():
            if hasattr(block, 'handle_post'):
                response = block.handle_post(request)
                if response is not None:
                    return response

        return self.handle_request(request)

    def set_page(self):
        try:
            page = Page.objects.filter(site=settings.SITE,
                                       page_type=self.page_type)[0]
        except IndexError:
            try:
                page = Page.objects.filter(site_id=1,
                                           page_type=self.page_type)[0]
            except IndexError:
                raise Http404
        setattr(self, 'page', page)