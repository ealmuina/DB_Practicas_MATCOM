from django.conf.urls import url

from practicas import views

urlpatterns = [
    url(r'^$', views.index, name='index'),  # TODO: Unir URLs
    url(r'^index/$', views.index, name='index')
]
