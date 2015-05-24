from django.conf.urls import patterns, url
from testing import views


urlpatterns = patterns('',
    url(r'^test_server/$', views.TestServerViewSet.as_view()),
)