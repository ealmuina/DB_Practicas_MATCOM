from django.conf.urls import url

from practicas import views

urlpatterns = [
    url(r'^$|^index/$', views.index, name='index'),

    url(r'^projects/$', views.projects_available, name='projects-available'),
    url(r'^projects/assign/$', views.assign_projects, name='projects-assign'),
    url(r'^projects/(?P<project_name_slug>[-\w]+)/$', views.project_detail, name='project-detail'),
    url(r'^projects/(?P<project_name_slug>[-\w]+)/remove_request/$', views.request_remove, name='request-remove'),
    url(r'^projects/(?P<project_name_slug>[-\w]+)/evaluate/$', views.evaluate_participations,
        name='participations-evaluate'),

    url(r'^upload_report/$', views.upload_report, name='upload-report'),

    url(r'^archive/projects/$', views.ProjectArchive.as_view(), name='archive-projects'),
    url(r'^archive/projects/(?P<slug>[-\w]+)/$', views.ArchiveProjectDetailView.as_view(),
        name='archive-project-detail')
]
