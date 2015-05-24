from django.conf.urls import patterns, url, include
from rest_framework.routers import DefaultRouter
from arousal_modeler import views

router = DefaultRouter()
router.register(r'arousals', views.ArousalViewSet)

urlpatterns = patterns('',
    url(r'^', include(router.urls))
)