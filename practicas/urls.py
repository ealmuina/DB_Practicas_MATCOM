from django.conf.urls import url

from practicas import views

urlpatterns = [
    url(r'^$', views.index, name='index'),  # TODO: Unir URLs
    url(r'^index/$', views.index, name='index'),
    url(r'^projects/$', views.projects, name='projects'),
    url(r'^projects/create_project/$', views.project, name='project-create'),
    url(r'^projects/(?P<slug>[-\w]+)/$', views.ProjectDetailView.as_view(), name='project-detail'),
    url(r'^projects/(?P<project_name_slug>[-\w]+)/request/$', views.request, name='request'),
]
