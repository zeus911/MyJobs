import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from moc_coding.models import CustomCareer, Moc, Onet

def moc_data(request):
    branches = request.GET.get("branch", "").split(",")
    callback = request.GET.get("callback")
    
    if branches:
        mocs = Moc.objects.filter(branch__in=branches)
    else:
        mocs = Moc.objects.all()

    data_dict = {"mocs": [i for i in mocs.values("code", "branch", "title")]}
    res = json.dumps(data_dict)
    return HttpResponse(u"{jsonp}({res})".format(jsonp=callback, res=res),
                        content_type="application/json")

def onet_data(request):
    onet_codes = request.GET.get("onets", "").split(",")
    callback = request.GET.get("callback")

    onets = Onet.objects.filter(code__in=onet_codes).values("code", "title")
    res = json.dumps([i for i in onets])
    return HttpResponse(u"{jsonp}({res})".format(jsonp=callback, res=res),
                        content_type="application/json")
    
@login_required(login_url='/admin/')
def newmapping(request):
    if not request.user.is_superuser:
        return HttpResponse(json.dumps({"status": "Permission Denied"}),
                            content_type="application/json")
    moc = request.GET.get("moc")
    branch = request.GET.get("branch")
    moc = Moc.objects.get(code=moc, branch=branch).id
    onet = request.GET.get("onet")
    content_type = request.GET.get("ct")
    object_id = request.GET.get("oid")
    callback = request.GET.get("callback")
    cc = CustomCareer.objects.create(moc_id=moc, onet_id=onet,
                                     content_type_id=content_type,
                                     object_id=object_id)
    res = json.dumps({"status": "success", "id": cc.id})
    return HttpResponse(u"{jsonp}({res})".format(jsonp=callback, res=res),
                        content_type="application/json")

def maps_by_objid(request):
    content_type = request.GET.get("ct")
    object_id = request.GET.get("oid")
    callback = request.GET.get("callback")
    custcareers = CustomCareer.objects.filter(object_id=object_id,
                                              content_type=content_type)
    data_dict = custcareers.values("moc_id", "onet_id", "pk","moc__title","onet__title")
    res = json.dumps([i for i in data_dict])
    return HttpResponse(u"{jsonp}({res})".format(jsonp=callback, res=res))
    
@login_required(login_url='/admin/')
def delete(request):
    if not request.user.is_superuser:
       return HttpResponse(json.dumps({"status": "Permission Denied"}),
                           content_type="application/json")
    callback = request.GET.get("callback")
    instance_ids = request.GET.get("ids").split(",")
    CustomCareer.objects.filter(id__in=instance_ids).delete()
    del_ids = json.dumps([{'id': i} for i in instance_ids])
    return HttpResponse(u"{jsonp}({ids})".format(jsonp=callback, ids=del_ids))
    
