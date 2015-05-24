from django.conf.urls import patterns, url, include
from rest_framework.routers import DefaultRouter
from timeframe_annotator import views


router = DefaultRouter()
router.register(r'timeframe_annotations', views.TimeframeAnnotationViewSet)

urlpatterns = patterns('',
    url(r'^', include(router.urls)),
)