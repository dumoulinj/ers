from rest_framework import viewsets, generics, status
from rest_framework.response import Response
from dataset_manager.enums import EmotionType, FeatureType, FeatureFunctionType
from dataset_manager.models import Dataset, Video, AudioPart, VideoPart, Features
from dataset_manager.serializers import DatasetSerializer, VideoSerializer, AudioPartSerializer, VideoPartSerializer, \
    FeaturesSerializer
from django.conf import settings
from rest_framework.views import APIView


class DatasetViewSet(viewsets.ModelViewSet):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer


class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer


class AudioPartViewSet(viewsets.ModelViewSet):
    queryset = AudioPart.objects.all()
    serializer_class = AudioPartSerializer


class VideoPartViewSet(viewsets.ModelViewSet):
    queryset = VideoPart.objects.all()
    serializer_class = VideoPartSerializer


class FeaturesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Features.objects.all()
    serializer_class = FeaturesSerializer


class DatasetDefaultPathViewSet(APIView):
    def get(self, request, format=None):
        result = {'path': settings.DATASET_DEFAULT_PATH}
        return Response(result)


class EmotionsViewSet(APIView):
    def get(self, request, format=None):
        emotions = list()
        for basic_emotion_name, emotions_list in EmotionType.basic_emotions.iteritems():
            for emotion in emotions_list:
                emotions.append({'value': emotion, 'label': EmotionType.label(emotion), 'type': basic_emotion_name})

        return Response(emotions)


class FeatureTypesViewSet(APIView):
    def get(self, request, format=None):
        feature_type = list()
        for choice in FeatureType.choices():
            type = ''
            if choice[0] in FeatureType.audio_features:
                type = 'audio'
            elif choice[0] in FeatureType.video_features:
                type = 'video'
            feature_type.append({'value': choice[0], 'label': FeatureType.label(choice[0]), 'type': type})

        return Response(feature_type)


class FeatureFunctionTypesViewSet(APIView):
    def get(self, request, format=None):
        feature_function_type = list()
        for choice in FeatureFunctionType.choices():
            feature_function_type.append({'value': choice[0], 'label': FeatureFunctionType.label(choice[0])})

        return Response(feature_function_type)


class VideoByNameViewSet(generics.RetrieveAPIView):
    """
    Get a video by filtering on dataset_name and video_name. Return only one video.
    """
    serializer_class = VideoSerializer

    def get(self, request):
        try:
            queryset = Video.objects.all()

            dataset_name = request.query_params.get('dataset_name', None)

            if dataset_name is not None:
                queryset = queryset.filter(dataset__name=dataset_name)


            video_name = request.query_params.get('video_name', None)

            if video_name is not None:
                queryset = queryset.get(full_name__contains=video_name)

            serializer = VideoSerializer(queryset, context={'request': request})

            return Response(serializer.data)
        except:
            return Response("No video found for dataset '{}' with name '{}'".format(dataset_name, video_name), status=status.HTTP_400_BAD_REQUEST)


