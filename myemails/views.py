import json

from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic import TemplateView


def get_fields(request):
    model = request.GET.get('model')
    content_type = ContentType.objects.get(pk=model)
    model_class = content_type.model_class()
    return HttpResponse(json.dumps(getattr(model_class, 'EVENT_FIELDS', {})))


class Overview(TemplateView):
    template_name = "myemails/email-overview.html"


class ManageHeaderFooter(TemplateView):
    template_name = "myemails/footer-header.html"


def manage_template(request):
    ctx = {
        "mmm": ["Event1", "Event2", "Event3", "Event4"]
    }
    return render_to_response('myemails/manage-template.html',
                              ctx, RequestContext(request))


class ViewTemplate(TemplateView):
    template_name = "myemails/view-template.html"


class IframeView(TemplateView):
    template_name = "myemails/iframe-view.html"


class EditTemplate(TemplateView):
    template_name = "myemails/edit-template.html"