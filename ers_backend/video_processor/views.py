import json
from rest_framework import viewsets

from rest_framework.response import Response
from rest_framework.views import APIView
from video_processor.enums import ShotBoundariesDetectionAlgorithmType
from video_processor.models import ShotsDetection, VideoShotsResult, ShotDetectionAlgo, Shot, ShotBoundary

from video_processor.serializers import ShotsDetectionSerializer, VideoShotsResultSerializer, \
    ShotDetectionAlgoSerializer, ShotSerializer, ShotBoundarySerializer


class ShotDetectionAlgoViewSet(viewsets.ModelViewSet):
    queryset = ShotDetectionAlgo.objects.all().select_subclasses()
    serializer_class = ShotDetectionAlgoSerializer

class ShotsDetectionViewSet(viewsets.ModelViewSet):
    queryset = ShotsDetection.objects.all()
    serializer_class = ShotsDetectionSerializer


class ShotViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Shot.objects.all()
    serializer_class = ShotSerializer

class ShotBoundaryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ShotBoundary.objects.all()
    serializer_class = ShotBoundarySerializer

class VideoShotsResultViewSet(viewsets.ModelViewSet):
    queryset = VideoShotsResult.objects.all()
    serializer_class = VideoShotsResultSerializer

class AlgosListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ShotDetectionAlgo.get_AlgoList()
    model= ShotDetectionAlgo

    def list(self, request, *args, **kwargs):
        model = ShotDetectionAlgo
        return Response(ShotDetectionAlgo.get_AlgoList())

class SBDAlgorithmsViewSet(APIView):
    def get(self, request, format=None):
        algorithms = list()
        for choice in ShotBoundariesDetectionAlgorithmType.choices():
            algorithms.append({'value': choice[0], 'label': ShotBoundariesDetectionAlgorithmType.label(choice[0])})

        return Response(algorithms)


# class VideoFrameViewSet(viewsets.ModelViewSet):
#     queryset = VideoFrame.objects.all()
#     serializer_class = VideoFrameSerializer

# @api_view(('GET',))
# def api_root(request, format=None):
#     return Response({
#         'shots-detections': reverse('shotsdetection-list', request=request, format=format)
#     })
#
# class ShotsDetectionList(generics.ListAPIView):
#     queryset = ShotsDetection.objects.all()
#     serializer_class = ShotsDetectionSerializer
#
#
# class ShotsDetectionDetail(generics.RetrieveUpdateDestroyAPIView):
#     queryset = ShotsDetection.objects.all()
#     serializer_class = ShotsDetectionSerializer
#     lookup_field = 'id'
#
#
# class VideoShotsDetail(generics.RetrieveAPIView):
#     queryset = VideoShots.objects.all()
#     serializer_class = VideoShotsSerializer
#     lookup_field = 'id'
#
#
# class VideoShotsList_by_shots_detection(generics.ListAPIView):
#     model = VideoShots
#     serializer_class = VideoShotsSerializer
#
#     def get_queryset(self):
#         queryset = super(VideoShotsList_by_shots_detection, self).get_queryset()
#         return queryset.filter(shots_detection__id=self.kwargs.get('id'))
#
#
# class VideoShotsList_by_video(generics.ListAPIView):
#     model = VideoShots
#     serializer_class = VideoShotsSerializer
#
#     def get_queryset(self):
#         queryset = super(VideoShotsList_by_video, self).get_queryset()
#         return queryset.filter(video__id=self.kwargs.get('id'))
