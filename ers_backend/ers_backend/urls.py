from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ers_backend.views.home', name='home'),
    # url(r'^ers_backend/', include('ers_backend.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^docs/', include('rest_framework_swagger.urls')),

    url(r'^dataset_manager/', include('dataset_manager.urls')),
    url(r'^video_processor/', include('video_processor.urls')),
    url(r'^arousal_modeler/', include('arousal_modeler.urls')),
    url(r'^timeframe_annotator/', include('timeframe_annotator.urls')),
    url(r'^testing/', include('testing.urls')),
)
