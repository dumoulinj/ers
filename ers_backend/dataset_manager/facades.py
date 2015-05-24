from dataset_manager import tasks
from dataset_manager.enums import FeatureType
from dataset_manager.models import Dataset, Video

use_celery = True

class DatasetFacade:
    def _get_dataset_by_id(dataset_id):
        return Dataset.objects.get(pk=dataset_id)
    _get_dataset_by_id = staticmethod(_get_dataset_by_id)


    def dataset_name_exists(dataset_name):
        """
        Check if a dataset exists with this name
        """
        return Dataset.objects.filter(name=dataset_name).exists()
    dataset_name_exists = staticmethod(dataset_name_exists)


    def prepare(dataset_id):
        """
        Prepare the dataset, create directories.
        """
        if use_celery:
            tasks.prepare.delay(dataset_id)
        else:
            dataset = DatasetFacade._get_dataset_by_id(dataset_id)
            dataset.prepare()
    prepare = staticmethod(prepare)


    def scan_video_folder(dataset_id):
        """
        Scan video folder, look for video files, and create video instances.
        """
        if use_celery:
            tasks.scan_video_folder.delay(dataset_id)
        else:
            dataset = DatasetFacade._get_dataset_by_id(dataset_id)
            dataset.scan_video_folder()
    scan_video_folder = staticmethod(scan_video_folder)


    def prepare_videos(dataset_id, overwrite=False):
        """
        Prepare all the videos of the dataset
        """
        if use_celery:
            tasks.prepare_videos.delay(dataset_id, overwrite=overwrite)
        else:
            dataset = DatasetFacade._get_dataset_by_id(dataset_id)
            dataset.prepare_videos(overwrite)
    prepare_videos = staticmethod(prepare_videos)


    def detect_shot_boundaries(dataset_id, configuration=None):
        """
        Detect shot boundaries
        """
        if use_celery:
            tasks.detect_shot_boundaries.delay(dataset_id, configuration)
        else:
            dataset = DatasetFacade._get_dataset_by_id(dataset_id)
            dataset.detect_shot_boundaries(configuration)
    detect_shot_boundaries = staticmethod(detect_shot_boundaries)


    def extract_features(dataset_id, feature_types=None, overwrite=False):
        """
        Extract features
        """
        if use_celery:
            tasks.extract_features.delay(dataset_id, feature_types=feature_types, overwrite=overwrite)
        else:
            dataset = DatasetFacade._get_dataset_by_id(dataset_id)
            dataset.extract_features(feature_types=feature_types, overwrite=overwrite)
    extract_features = staticmethod(extract_features)


    def model_arousal(dataset_id, feature_types=None, overwrite=False):
        """
        Model arousal
        """
        if use_celery:
            tasks.model_arousal.delay(dataset_id, feature_types=feature_types, overwrite=overwrite)
        else:
            dataset = DatasetFacade._get_dataset_by_id(dataset_id)
            dataset.model_arousal(feature_types=feature_types, overwrite=overwrite)
    model_arousal = staticmethod(model_arousal)
    
class VideoFacade:
    def _get_video_by_id(video_id):
        return Video.objects.get(pk=video_id)
    _get_video_by_id = staticmethod(_get_video_by_id)


    def get_video_feature(video_id, feature_type):
        """
        Get specific video features
        """
        video = VideoFacade._get_video_by_id(video_id)

        multimedia_part = None
        if feature_type in FeatureType.audio_features:
            multimedia_part = video.audio_part
        elif feature_type in FeatureType.video_features:
            multimedia_part = video.video_part

        return multimedia_part.features.get(type=feature_type)
    get_video_feature = staticmethod(get_video_feature)


    def evaluate_sbd(video_id):
        """
        Evaluate the shot boundaries detection results for a particular video
        """
        # if use_celery:
        #     tasks.evaluate_sbd.delay(video_id)
        # else:
        video = VideoFacade._get_video_by_id(video_id)
        video.evaluate_sbd()


    evaluate_sbd = staticmethod(evaluate_sbd)
    