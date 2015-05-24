from rest_framework import serializers
from dataset_manager.models import Dataset, Video, VideoPart, AudioPart, Features


class DatasetSerializer(serializers.HyperlinkedModelSerializer):
    #video_list = serializers.HyperlinkedIdentityField(view_name='dataset-videos-list')
    class Meta:
        model = Dataset
        fields = ('url', 'id', 'name', 'base_path', 'videos', )#, 'video_list')


class FeaturesSerializer(serializers.HyperlinkedModelSerializer):
    # def transform_values(self, obj, value):
    #     return obj.values
    #
    # def transform_values_normalized(self, obj, value):
    #     print(type(q.values_normalized))
    #     return obj.values_normalized
    #
    # def transform_values_processed(self, obj, value):
    #     return obj.values_processed

    def to_representation(self,instance):
        ret = super(FeaturesSerializer,self).to_representation(instance)
        ret['values_normalized'] = eval(ret['values_normalized'])
        ret['values'] = eval(ret['values'])
        ret['values_processed'] = eval(ret['values_processed'])
        # print(ret.items())
        return ret
    # type_name = serializers.Field()
    class Meta:

        model = Features
        fields = ('type', 'values', 'values_normalized', 'values_processed','type_name', )

class VideoPartSerializer(serializers.HyperlinkedModelSerializer):
    #features = FeaturesSerializer(many=True, read_only=True)

    class Meta:
        model = VideoPart
        fields = ('url', 'id', 'video', 'codec', 'width', 'height', 'fps', 'features', )


class AudioPartSerializer(serializers.HyperlinkedModelSerializer):
    #features = FeaturesSerializer(many=True, read_only=True)

    class Meta:
        model = AudioPart
        fields = ('url', 'id', 'video', 'codec', 'channels', 'samplerate', 'features', )


class VideoSerializer(serializers.HyperlinkedModelSerializer):
    shots_detections = serializers.HyperlinkedRelatedField(source='video_shots_results', many=True, read_only=True, view_name='videoshotsresult-detail')

    class Meta:
        model = Video
        fields = ('url', 'id', 'dataset', 'name', 'emotion', 'format', 'duration', 'bitrate', 'video_part', 'audio_part', 'shots_detections', 'arousal', 'shot_boundaries_ground_truth', 'preparation_state', 'shot_boundaries_detection_state', 'feature_extraction_state', 'arousal_modeling_state', 'available_features')
