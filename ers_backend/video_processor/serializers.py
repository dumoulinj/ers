from rest_framework import serializers
from video_processor.models import ShotsDetection, VideoShotsResult, ShotDetectionAlgo, Shot, ShotBoundary


class ShotDetectionAlgoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ShotDetectionAlgo


class ShotsDetectionSerializer(serializers.HyperlinkedModelSerializer):
    #video_shots = serializers.HyperlinkedRelatedField(many=True, view_name='videoshots-detail', read_only=True)
    #video_shots = serializers.HyperlinkedIdentityField('video_shots')
    #video_shots = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = ShotsDetection
        fields = ('url', 'id', 'date', 'algos')


class ShotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shot
        fields = ('id','shot_nb', 'start_frame', 'end_frame')
        
class ShotBoundarySerializer(serializers.ModelSerializer):
    class Meta:
        model = ShotBoundary
        fields = ('frame', 'type')

class VideoShotsResultSerializer(serializers.HyperlinkedModelSerializer):
    shots = ShotSerializer(many=True)
    shot_boundaries = ShotBoundarySerializer(many=True)

    def update(self, instance, validated_data):
        instance.comment = validated_data.get('comment', instance.comment)
        instance.save()
        return instance

    class Meta:
        model = VideoShotsResult
        fields = ('url', 'id', 'shots_detection', 'video', 'precision', 'recall', 'shots', 'shot_boundaries', 'comment', 'date', 'configuration_as_string', )

# class VideoFrameSerializer(serializers.HyperlinkedModelSerializer):
#     #features = FeaturesSerializer(many=True, read_only=True)
#
#     class Meta:
#         model = VideoFrame
#         fields = ('url', 'id', 'video_part', 'index')


# class ShotSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Shot
#         fields = ('shot_nb', 'start_frame', 'end_frame')
#
#
# class ShotBoundarySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ShotBoundary
#         fields = ('frame', 'type')
#
#
# class VideoShotsSerializer(serializers.HyperlinkedModelSerializer):
#     shots = ShotSerializer(many=True)
#     shot_boundaries = ShotBoundarySerializer(many=True)
#
#     class Meta:
#         model = VideoShots
#         fields = ('url', 'id', 'shots_detection', 'video', 'precision', 'recall', 'shots', 'shot_boundaries')
#         lookup_field = 'id'

