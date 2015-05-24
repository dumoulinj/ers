from rest_framework import serializers
from emotion_annotator.models import FrameEmotions




class FrameEmotionsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FrameEmotions
        fields = ('video', 'frameTime', 'emotionType')

