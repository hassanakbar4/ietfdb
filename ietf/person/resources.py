# Autogenerated by the mkresources management command 2014-11-13 23:53
from ietf.api import ModelResource
from tastypie.fields import ToOneField
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.cache import SimpleCache

from ietf import api

from ietf.person.models import (Person, Email, Alias, PersonHistory, PersonalApiKey, PersonEvent, PersonApiKeyEvent)


from ietf.utils.resources import UserResource
class PersonResource(ModelResource):
    user             = ToOneField(UserResource, 'user', null=True)
    class Meta:
        cache = SimpleCache()
        queryset = Person.objects.all()
        serializer = api.Serializer()
        #resource_name = 'person'
        ordering = ['id', ]
        filtering = { 
            "id": ALL,
            "time": ALL,
            "name": ALL,
            "ascii": ALL,
            "ascii_short": ALL,
            "address": ALL,
            "affiliation": ALL,
            "photo": ALL,
            "biography": ALL,
            "user": ALL_WITH_RELATIONS,
        }
api.person.register(PersonResource())

class EmailResource(ModelResource):
    person           = ToOneField(PersonResource, 'person', null=True)
    class Meta:
        cache = SimpleCache()
        queryset = Email.objects.all()
        serializer = api.Serializer()
        #resource_name = 'email'
        filtering = { 
            "address": ALL,
            "time": ALL,
            "active": ALL,
            "person": ALL_WITH_RELATIONS,
        }
api.person.register(EmailResource())

class AliasResource(ModelResource):
    person           = ToOneField(PersonResource, 'person')
    class Meta:
        cache = SimpleCache()
        queryset = Alias.objects.all()
        serializer = api.Serializer()
        #resource_name = 'alias'
        filtering = { 
            "id": ALL,
            "name": ALL,
            "person": ALL_WITH_RELATIONS,
        }
api.person.register(AliasResource())

from ietf.utils.resources import UserResource
class PersonHistoryResource(ModelResource):
    person           = ToOneField(PersonResource, 'person')
    user             = ToOneField(UserResource, 'user', null=True)
    class Meta:
        cache = SimpleCache()
        queryset = PersonHistory.objects.all()
        serializer = api.Serializer()
        #resource_name = 'personhistory'
        filtering = { 
            "id": ALL,
            "time": ALL,
            "name": ALL,
            "ascii": ALL,
            "ascii_short": ALL,
            "address": ALL,
            "affiliation": ALL,
            "person": ALL_WITH_RELATIONS,
            "user": ALL_WITH_RELATIONS,
        }
api.person.register(PersonHistoryResource())


class PersonalApiKeyResource(ModelResource):
    person           = ToOneField(PersonResource, 'person')
    class Meta:
        queryset = PersonalApiKey.objects.all()
        serializer = api.Serializer()
        cache = SimpleCache()
        #resource_name = 'personalapikey'
        filtering = { 
            "id": ALL,
            "endpoint": ALL,
            "created": ALL,
            "valid": ALL,
            "salt": ALL,
            "count": ALL,
            "latest": ALL,
            "person": ALL_WITH_RELATIONS,
        }
api.person.register(PersonalApiKeyResource())


class PersonEventResource(ModelResource):
    person           = ToOneField(PersonResource, 'person')
    class Meta:
        queryset = PersonEvent.objects.all()
        serializer = api.Serializer()
        cache = SimpleCache()
        #resource_name = 'personevent'
        filtering = { 
            "id": ALL,
            "time": ALL,
            "type": ALL,
            "desc": ALL,
            "person": ALL_WITH_RELATIONS,
        }
api.person.register(PersonEventResource())


class PersonApiKeyEventResource(ModelResource):
    person           = ToOneField(PersonResource, 'person')
    personevent_ptr  = ToOneField(PersonEventResource, 'personevent_ptr')
    key              = ToOneField(PersonalApiKeyResource, 'key')
    class Meta:
        queryset = PersonApiKeyEvent.objects.all()
        serializer = api.Serializer()
        cache = SimpleCache()
        #resource_name = 'personapikeyevent'
        filtering = { 
            "id": ALL,
            "time": ALL,
            "type": ALL,
            "desc": ALL,
            "person": ALL_WITH_RELATIONS,
            "personevent_ptr": ALL_WITH_RELATIONS,
            "key": ALL_WITH_RELATIONS,
        }
api.person.register(PersonApiKeyEventResource())
