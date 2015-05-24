from rest_framework import viewsets, filters
from timeframe_annotator.models import TimeframeAnnotation
from timeframe_annotator.serializers import TimeframeAnnotationSerializer


class TimeframeAnnotationViewSet(viewsets.ModelViewSet):
    queryset = TimeframeAnnotation.objects.all()
    serializer_class = TimeframeAnnotationSerializer
    filter_backends = (filters.OrderingFilter,)
    ordering = ('start_frame',)