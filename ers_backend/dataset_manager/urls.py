from django.conf.urls import patterns, url, include
from rest_framework.routers import DefaultRouter
from dataset_manager import views

router = DefaultRouter()
router.register(r'datasets', views.DatasetViewSet)
router.register(r'videos', views.VideoViewSet)
router.register(r'audio_parts', views.AudioPartViewSet)
router.register(r'video_parts', views.VideoPartViewSet)
router.register(r'features', views.FeaturesViewSet)

urlpatterns = patterns('',
    url(r'^', include(router.urls)),
    url(r'^base_path/$', views.DatasetDefaultPathViewSet.as_view()),
    url(r'^emotions/$', views.EmotionsViewSet.as_view()),
    url(r'^feature_types/$', views.FeatureTypesViewSet.as_view()),
    url(r'^feature_function_types/$', views.FeatureFunctionTypesViewSet.as_view()),
)