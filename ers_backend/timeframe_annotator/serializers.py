from rest_framework import serializers
from timeframe_annotator.models import TimeframeAnnotation


class TimeframeAnnotationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TimeframeAnnotation