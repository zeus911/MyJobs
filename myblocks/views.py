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
            self.set_page(request)
        head, body = self.page.render(request)
        context = {
            'body': body,
            'head': head,
            'page': self.page
        }
        return render_to_response('myblocks/myblocks_base.html', context,
                                  context_instance=RequestContext(request))

    def post(self, request):
        self.set_page(request)
        for block in self.page.all_blocks():
            # Checks to see if any blocks need to do any special handling of
            # posts.
            if hasattr(block, 'handle_post'):
                response = block.handle_post(request)
                # Some blocks redirect after appropriately handling posted
                # data. Allow the blocks to successfully redirect if they do.
                if response is not None:
                    return response

        return self.handle_request(request)

    def set_page(self, request):
        """
        Trys to set the page for this site by:
            1. If the user is staff, getting a staging page for the specific
                site matching the page_type.
            2. Getting a page for the specific site matching page_type.
            3. Getting a page for the default site matching this page_type.
            4. Giving up and returning a 404.

        """
        if request.user.is_authenticated() and request.user.is_staff:
            try:
                page = Page.objects.filter(site=settings.SITE,
                                           status=Page.STAGING,
                                           page_type=self.page_type)[0]
                setattr(self, 'page', page)
            except IndexError:
                pass

        try:
            page = Page.objects.filter(site=settings.SITE,
                                       status=Page.PRODUCTION,
                                       page_type=self.page_type)[0]
        except IndexError:
            try:
                page = Page.objects.filter(site_id=1,
                                           status=Page.PRODUCTION,
                                           page_type=self.page_type)[0]
            except IndexError:
                raise Http404
        setattr(self, 'page', page)