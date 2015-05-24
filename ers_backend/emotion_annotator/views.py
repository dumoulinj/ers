from rest_framework import viewsets
from emotion_annotator.models import FrameEmotions
from emotion_annotator.serializers import FrameEmotionsSerializer


class FrameEmotionsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FrameEmotions.objects.all()
    serializer_class = FrameEmotionsSerializer
