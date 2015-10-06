from django.conf.urls import patterns

urlpatterns = patterns('',
    (r'^$', 'ietf.group.info.group_home', None, "group_home"),
    (r'^documents/txt/$', 'ietf.group.info.group_documents_txt'),
    (r'^documents/$', 'ietf.group.info.group_documents', None, "group_docs"),
    (r'^charter/$', 'ietf.group.info.group_about', None, 'group_charter'),
    (r'^about/$', 'ietf.group.info.group_about', None, 'group_about'),
    (r'^history/$','ietf.group.info.history'),
    (r'^deps/dot/$', 'ietf.group.info.dependencies_dot'),
    (r'^deps/pdf/$', 'ietf.group.info.dependencies_pdf'),
    (r'^edit/$', 'ietf.group.edit.edit', {'action': "edit"}, "group_edit"),
    (r'^conclude/$', 'ietf.group.edit.conclude'),
    (r'^milestones/$', 'ietf.group.milestones.edit_milestones', {'milestone_set': "current"}, "group_edit_milestones"),
    (r'^milestones/charter/$', 'ietf.group.milestones.edit_milestones', {'milestone_set': "charter"}, "group_edit_charter_milestones"),
    (r'^milestones/charter/reset/$', 'ietf.group.milestones.reset_charter_milestones', None, "group_reset_charter_milestones"),
    (r'^workflow/$', 'ietf.group.edit.customize_workflow'),
    (r'^materials/$', 'ietf.group.info.materials', None, "group_materials"),
    (r'^materials/new/$', 'ietf.doc.views_material.choose_material_type'),
    (r'^materials/new/(?P<doc_type>[\w-]+)/$', 'ietf.doc.views_material.edit_material', { 'action': "new" }, "group_new_material"),
    (r'^/email-aliases/$', 'ietf.group.info.email_aliases'),
)
