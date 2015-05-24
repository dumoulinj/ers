from django.conf.urls import patterns, url, include
from rest_framework.routers import DefaultRouter
from emotion_annotator import views

router = DefaultRouter()
router.register(r'frameEmotions', views.FeaturesViewSet)

urlpatterns = patterns('',
    url(r'^', include(router.urls))
)