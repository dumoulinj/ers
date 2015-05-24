from swampdragon.serializers.model_serializer import ModelSerializer

class DatasetSerializer(ModelSerializer):
    class Meta:
        model = 'dataset_manager.Dataset'
        publish_fields = ('id', 'name', 'description', 'available_features', 'base_path', 'video_path', 'audio_path', 'frame_path', 'ground_truth_path', 'shot_boundaries_ground_truth_path', 'nb_videos', 'preparation_state', 'scan_state', 'videos_preparation_state', 'videos_preparation_nb_videos_done', 'shot_boundaries_detection_state', 'shot_boundaries_detection_nb_videos_done', 'feature_extraction_state', 'feature_extraction_nb_videos_done', 'arousal_modeling_state', 'arousal_modeling_nb_videos_done', )
        update_fields = ('id', 'name', 'description', )


class VideoSerializer(ModelSerializer):
    class Meta:
        model = 'dataset_manager.Video'
        publish_fields = ('id', 'name', 'format', 'duration', 'emotion', 'preparation_state', 'shot_boundaries_detection_state', 'feature_extraction_state', 'arousal_modeling_state', 'available_features', )

class FeaturesSerializer(ModelSerializer):
    class Meta:
        model = 'dataset_manager.Features'
        publish_fields = ('id', 'type', 'values', 'values_normalized', 'values_processed', )