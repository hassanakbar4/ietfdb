# Autogenerated by the mkresources management command 2014-11-13 23:53
from tastypie.resources import ModelResource
from tastypie.fields import ToOneField, ToManyField
from tastypie.constants import ALL, ALL_WITH_RELATIONS

from ietf import api

from ietf.community.models import *     # pyflakes:ignore


from ietf.doc.resources import DocumentResource
from ietf.group.resources import GroupResource
from ietf.utils.resources import UserResource
class CommunityListResource(ModelResource):
    user             = ToOneField(UserResource, 'user', null=True)
    group            = ToOneField(GroupResource, 'group', null=True)
    added_ids        = ToManyField(DocumentResource, 'added_ids', null=True)
    class Meta:
        queryset = CommunityList.objects.all()
        serializer = api.Serializer()
        #resource_name = 'communitylist'
        filtering = { 
            "id": ALL,
            "secret": ALL,
            "cached": ALL,
            "user": ALL_WITH_RELATIONS,
            "group": ALL_WITH_RELATIONS,
            "added_ids": ALL_WITH_RELATIONS,
        }
api.community.register(CommunityListResource())

class DisplayConfigurationResource(ModelResource):
    community_list   = ToOneField(CommunityListResource, 'community_list')
    class Meta:
        queryset = DisplayConfiguration.objects.all()
        serializer = api.Serializer()
        #resource_name = 'displayconfiguration'
        filtering = { 
            "id": ALL,
            "sort_method": ALL,
            "display_fields": ALL,
            "community_list": ALL_WITH_RELATIONS,
        }
api.community.register(DisplayConfigurationResource())

from ietf.doc.resources import DocEventResource
class ListNotificationResource(ModelResource):
    event            = ToOneField(DocEventResource, 'event')
    class Meta:
        queryset = ListNotification.objects.all()
        serializer = api.Serializer()
        #resource_name = 'listnotification'
        filtering = { 
            "id": ALL,
            "significant": ALL,
            "event": ALL_WITH_RELATIONS,
        }
api.community.register(ListNotificationResource())

from ietf.doc.resources import DocumentResource
class RuleResource(ModelResource):
    community_list   = ToOneField(CommunityListResource, 'community_list')
    cached_ids       = ToManyField(DocumentResource, 'cached_ids', null=True)
    class Meta:
        queryset = Rule.objects.all()
        serializer = api.Serializer()
        #resource_name = 'rule'
        filtering = { 
            "id": ALL,
            "rule_type": ALL,
            "value": ALL,
            "last_updated": ALL,
            "community_list": ALL_WITH_RELATIONS,
            "cached_ids": ALL_WITH_RELATIONS,
        }
api.community.register(RuleResource())

class EmailSubscriptionResource(ModelResource):
    community_list   = ToOneField(CommunityListResource, 'community_list')
    class Meta:
        queryset = EmailSubscription.objects.all()
        serializer = api.Serializer()
        #resource_name = 'emailsubscription'
        filtering = { 
            "id": ALL,
            "email": ALL,
            "significant": ALL,
            "community_list": ALL_WITH_RELATIONS,
        }
api.community.register(EmailSubscriptionResource())

from ietf.doc.resources import DocumentResource
class DocumentChangeDatesResource(ModelResource):
    document         = ToOneField(DocumentResource, 'document')
    class Meta:
        queryset = DocumentChangeDates.objects.all()
        serializer = api.Serializer()
        #resource_name = 'documentchangedates'
        filtering = { 
            "id": ALL,
            "new_version_date": ALL,
            "normal_change_date": ALL,
            "significant_change_date": ALL,
            "document": ALL_WITH_RELATIONS,
        }
api.community.register(DocumentChangeDatesResource())

