
from ietf.help import views
from ietf.utils.urls import url

urlpatterns = [
    url(r'^state/(?P<doc>[-\w]+)/(?P<type>[-\w]+)/?$', views.state),
    url(r'^state/(?P<doc>[-\w]+)/?$', views.state),
    url(r'^state/?$', views.state_index),
]

