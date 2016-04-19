from django.conf.urls import url

from practicas import views

urlpatterns = [
    url(r'^$', views.index, name='index'),  # TODO: Unir URLs
    url(r'^index/$', views.index, name='index'),
    url(r'^projects/$', views.projects_available, name='available_projects'),
    url(r'^projects/(?P<project_name_slug>[-\w]+)/$', views.project_detail, name='project-detail'),
    url(r'^projects/(?P<project_name_slug>[-\w]+)/remove_request/$', views.request_remove, name='request-remove'),
    url(r'^archive/projects/$', views.ProjectArchive.as_view(), name='archive-projects'),
    url(r'^archive/projects/(?P<slug>[-\w]+)/$', views.ArchiveProjectDetailView.as_view(),
        name='archive-project-detail'),
    url(r'^participations/(?P<participation_id>[0-9]+)/$', views.evaluate_participation, name='participation-evaluate')
]
