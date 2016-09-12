from django.conf.urls import url
from django.contrib import admin
from portal import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^signup$', views.signup, name='signup'),
    url(r'^login$', views.login_path, name='login'),
    url(r'^logout$', views.logout_path, name='logout'),
    url(r'^stream$', views.stream, name='stream'),
    url(r'^stream_course/(?P<course_id>\d+)$', views.stream_course, name='stream_course'),
    url(r'^view_stream/(?P<stream_id>\d+)$', views.view_stream, name='view_stream'),
    url(r'^end_stream/(?P<stream_id>\d+)$', views.end_stream, name='end_stream'),
]
