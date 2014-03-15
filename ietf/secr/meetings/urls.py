from django.conf.urls import patterns, url

urlpatterns = patterns('ietf.secr.meetings.views',
    url(r'^$', 'main', name='meetings'),
    url(r'^add/$', 'add', name='meetings_add'),
    url(r'^ajax/get-times/(?P<meeting_id>\d{1,6})/(?P<day>\d)/$', 'ajax_get_times', name='meetings_ajax_get_times'),
    url(r'^blue_sheet/$', 'blue_sheet_redirect', name='meetings_blue_sheet_redirect'),
    url(r'^(?P<meeting_id>\d{1,6})/$', 'view', name='meetings_view'),
    url(r'^(?P<meeting_id>\d{1,6})/blue_sheet/$', 'blue_sheet', name='meetings_blue_sheet'),
    url(r'^(?P<meeting_id>\d{1,6})/blue_sheet/generate/$', 'blue_sheet_generate', name='meetings_blue_sheet_generate'),
    url(r'^(?P<meeting_id>\d{1,6})/edit/$', 'edit_meeting', name='meetings_edit_meeting'),
    url(r'^(?P<meeting_id>\d{1,6})/rooms/$', 'rooms', name='meetings_rooms'),
    url(r'^(?P<meeting_id>\d{1,6})/times/$', 'times', name='meetings_times'),
    url(r'^(?P<meeting_id>\d{1,6})/times/delete/(?P<time>[0-9\:]+)/$', 'times_delete', name='meetings_times_delete'),
    url(r'^(?P<meeting_id>\d{1,6})/non_session/$', 'non_session', name='meetings_non_session'),
    url(r'^(?P<meeting_id>\d{1,6})/non_session/edit/(?P<slot_id>\d{1,6})/$', 'non_session_edit', name='meetings_non_session_edit'),
    url(r'^(?P<meeting_id>\d{1,6})/non_session/delete/(?P<slot_id>\d{1,6})/$', 'non_session_delete', name='meetings_non_session_delete'),
    url(r'^(?P<meeting_id>\d{1,6})/select/$', 'select_group',
        name='meetings_select_group'),
    url(r'^(?P<meeting_id>\d{1,6})/(?P<acronym>[A-Za-z0-9_\-\+]+)/schedule/$', 'schedule', name='meetings_schedule'),
    url(r'^(?P<meeting_id>\d{1,6})/(?P<acronym>[A-Za-z0-9_\-\+]+)/remove/$', 'remove_session', name='meetings_remove_session'),
)
