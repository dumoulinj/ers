from swampdragon import route_handler
from swampdragon.route_handler import ModelRouter, BaseRouter
import time
from dataset_manager.enums import ComputingStateType
from dataset_manager.facades import DatasetFacade, VideoFacade
from dataset_manager.dragon_serializers import DatasetSerializer, VideoSerializer, FeaturesSerializer
from dataset_manager.models import Dataset, Video


class DatasetRouter(ModelRouter):
    route_name = 'dataset'
    serializer_class = DatasetSerializer
    model = Dataset
    valid_verbs = BaseRouter.valid_verbs + ['prepare_dataset', 'scan_video_folder', 'prepare_videos', 'detect_shot_boundaries', 'extract_features', 'model_arousal']

    def create(self, **kwargs):
        # Check if name already exists, return error if yes, create else
        name = kwargs["name"]
        if DatasetFacade.dataset_name_exists(name):
            self.send({"error": {"message": "A dataset with this name already exists.", "type": "dataset_name"}})
        else:
            try:
                super(DatasetRouter, self).create(**kwargs)
            except:
                self.send({"error": {"message": "A problem occured when trying to create the dataset.", "type": "creation_error"}})

    def get_object(self, **kwargs):
        return self.model.objects.get(pk=kwargs['id'])

    def get_query_set(self, **kwargs):
        return self.model.objects.all()

    def prepare_dataset(self, dataset_id):
        DatasetFacade.prepare(dataset_id)

    def scan_video_folder(self, dataset_id):
        DatasetFacade.scan_video_folder(dataset_id)

    def prepare_videos(self, dataset_id, overwrite=False):
        DatasetFacade.prepare_videos(dataset_id, overwrite=overwrite)

    def detect_shot_boundaries(self, dataset_id, configuration):
        DatasetFacade.detect_shot_boundaries(dataset_id, configuration)

    def extract_features(self, dataset_id, feature_types, overwrite=False):
        DatasetFacade.extract_features(dataset_id, feature_types, overwrite=overwrite)

    def model_arousal(self, dataset_id, feature_types, overwrite=False):
        DatasetFacade.model_arousal(dataset_id, feature_types, overwrite=overwrite)


class VideoRouter(ModelRouter):
    route_name = 'video'
    serializer_class = VideoSerializer
    model = Video

    valid_verbs = BaseRouter.valid_verbs + ['get_feature', 'evaluate_sbd']

    def get_object(self, **kwargs):
        return self.model.objects.get(pk=kwargs['id'])

    def get_query_set(self, **kwargs):
        return self.model.objects.filter(dataset__id=kwargs['dataset_id'])

    def get_feature(self, video_id, feature_type):
        feature = VideoFacade.get_video_feature(video_id, feature_type)
        serializer = FeaturesSerializer(instance=feature)
        serialized_feature = serializer.serialize()
        self.send(serialized_feature)

    def evaluate_sbd(self, video_id):
        try:
            VideoFacade.evaluate_sbd(video_id)
            self.send({"state": ComputingStateType.SUCCESS})
        except:
            self.send({"state": ComputingStateType.FAILED})

# Register routers
route_handler.register(DatasetRouter)
route_handler.register(VideoRouter)
