from django.conf import settings
from django.contrib.sites.models import Site
from django.shortcuts import redirect


class WildcardMiddleware:
    """
    This middleware class checks the host domain against the current site. If 
    the domain is not found, then it first checks if the domain is a holdover 
    from the .jobs universe with a corrasponding microsite domain. If it is 
    found, it redirect the browser to the microsite domain.
    
    If the domain is not a matching holdover, all subdomains and paths are
    stripped and the browser is redirected to the root domain.
    
    """
    def process_request(self, request):
        """
        Process all http requests and check them to see if the domain is
        invalid and needs to be redirected.
        
        Inputs:
        :self:      
        :request:   django request object
        
        """
        # only do this redirect if the toggle in settings is set to True
        if not settings.WILDCARD_REDIRECT:
            return

        host =  request.get_host()
        # strip the port number if present (usually because of runserver)
        if ":" in host:
            host = host.split(":")[0]

        if host == "localhost":
            return
        
        site = Site.objects.get_current().domain
        if site != host:
            host_root = host.split(".")
            # if there is no subdomain, do nothing
            if len(host_root) < 3: 
                return

            # if subdomain is a number, it's probably an IP address, do nothing
            if host_root[-1].isdigit():
                return

            root_domain = host_root[-2]
            if root_domain in settings.NEVER_REDIRECT:
                return
            tld = host_root[-1]
            redirect_url = "http://%s.%s" % (root_domain, tld)
            return redirect(redirect_url, permanent=True)
