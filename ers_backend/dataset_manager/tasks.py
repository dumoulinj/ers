from __future__ import absolute_import

from celery import shared_task
from dataset_manager.models import Dataset, Video


def _get_dataset_by_id(dataset_id):
    return Dataset.objects.get(pk=dataset_id)

def _get_video_by_id(video_id):
    return Video.objects.get(pk=video_id)

@shared_task
def prepare(dataset_id):
    dataset = _get_dataset_by_id(dataset_id)
    dataset.prepare()


@shared_task
def scan_video_folder(dataset_id):
    dataset = _get_dataset_by_id(dataset_id)
    dataset.scan_video_folder()

@shared_task
def prepare_videos(dataset_id, overwrite=False):
    dataset = _get_dataset_by_id(dataset_id)
    dataset.prepare_videos(overwrite)

@shared_task
def detect_shot_boundaries(dataset_id, configuration):
    dataset = _get_dataset_by_id(dataset_id)
    dataset.detect_shot_boundaries(configuration)

@shared_task
def extract_features(dataset_id, feature_types, overwrite=False):
    dataset = _get_dataset_by_id(dataset_id)
    dataset.extract_features(feature_types=feature_types, overwrite=overwrite)

@shared_task
def model_arousal(dataset_id, feature_types, overwrite=False):
    dataset = _get_dataset_by_id(dataset_id)
    dataset.model_arousal(feature_types, overwrite=overwrite)

# @shared_task
# def evaluate_sbd(video_id):
#     video = _get_video_by_id(video_id)
#     video.evaluate_sbd()