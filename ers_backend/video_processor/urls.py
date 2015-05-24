from django.conf.urls import patterns, url, include
from rest_framework.routers import DefaultRouter
from video_processor import views
from video_processor.views import AlgosListViewSet


router = DefaultRouter()
router.register(r'shots_detections', views.ShotsDetectionViewSet)
router.register(r'video_shots_results', views.VideoShotsResultViewSet)
router.register(r'shot_detection_algos', views.ShotDetectionAlgoViewSet)
router.register(r'shots', views.ShotViewSet)
router.register(r'shot_boundaries', views.ShotBoundaryViewSet)
router.register(r'shots_algos_list',AlgosListViewSet)
#router.register(r'video_frames', views.VideoFrameViewSet)


urlpatterns = patterns('',
    url(r'^', include(router.urls)),
    url(r'^sbd_algorithms/$', views.SBDAlgorithmsViewSet.as_view()),
)