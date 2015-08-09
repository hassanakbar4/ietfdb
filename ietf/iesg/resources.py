# Autogenerated by the mkresources management command 2014-11-13 23:53
from tastypie.resources import ModelResource
from tastypie.constants import ALL

from ietf import api

from ietf.iesg.models import *          # pyflakes:ignore


class TelechatDateResource(ModelResource):
    class Meta:
        queryset = TelechatDate.objects.all()
        serializer = api.Serializer()
        #resource_name = 'telechatdate'
        filtering = { 
            "id": ALL,
            "date": ALL,
        }
api.iesg.register(TelechatDateResource())

class TelechatResource(ModelResource):
    class Meta:
        queryset = Telechat.objects.all()
        serializer = api.Serializer()
        #resource_name = 'telechat'
        filtering = { 
            "telechat_id": ALL,
            "telechat_date": ALL,
            "minute_approved": ALL,
            "wg_news_txt": ALL,
            "iab_news_txt": ALL,
            "management_issue": ALL,
            "frozen": ALL,
            "mi_frozen": ALL,
        }
api.iesg.register(TelechatResource())

class TelechatAgendaItemResource(ModelResource):
    class Meta:
        queryset = TelechatAgendaItem.objects.all()
        serializer = api.Serializer()
        #resource_name = 'telechatagendaitem'
        filtering = { 
            "id": ALL,
            "text": ALL,
            "type": ALL,
            "title": ALL,
        }
api.iesg.register(TelechatAgendaItemResource())

