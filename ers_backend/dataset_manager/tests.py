"""

"""
import os

from django.test import TestCase
from django.test.utils import override_settings
from dataset_manager.enums import FeatureType, ComputingStateType
from dataset_manager.models import Dataset
from django.conf import settings

test_path = os.path.join(settings.DATASET_DEFAULT_PATH, 'test_dataset')


class DatasetModelTestCase(TestCase):
    def setUp(self):
        self.dataset, self.created = Dataset.objects.get_or_create(name="test_dataset", description="Dataset for tests")

    def test_dataset_prepare(self):
        """Directories are created correctly4"""
        directories = [
            self.dataset.base_path,
            self.dataset.video_path,
            self.dataset.audio_path,
            self.dataset.converted_video_path,
            self.dataset.frame_path,
            self.dataset.ground_truth_path,
            self.dataset.shot_boundaries_ground_truth_path
        ]

        for directory in directories:
            self.assertTrue(os.path.isdir(directory), "{} should exists".format(directory))

        self.assertEqual(self.dataset.preparation_state, ComputingStateType.SUCCESS, "Preparation state of dataset should be SUCCESS. {} instead".format(ComputingStateType.label(self.dataset.preparation_state)))

    def test_scan_video_folder(self):
        """Video folder is correctly scanned, and the video instances are correctly created"""
        nb_videos = 3

        [created_videos, updated_videos] = self.dataset.scan_video_folder()

        self.assertEqual(self.dataset.videos.count(), nb_videos, "Should have created 3 new videos. {} instead".format(len(created_videos)))
        self.assertEqual(len(created_videos), nb_videos, "Should have created 3 new videos. {} instead".format(len(created_videos)))
        self.assertEqual(len(updated_videos), 0, "Should have updated 0 new videos. {} instead".format(len(updated_videos)))

        self.assertEqual(self.dataset.scan_state, ComputingStateType.SUCCESS, "Scanning state of dataset {} should be 'success'. {} instead".format(self.dataset.name, ComputingStateType.label(self.dataset.scan_state)))

        [created_videos, updated_videos] = self.dataset.scan_video_folder()

        self.assertEqual(self.dataset.videos.count(), nb_videos, "Should have still 3. {} instead".format(len(created_videos)))
        self.assertEqual(len(created_videos), 0, "Should have created 0 new videos. {} instead".format(len(created_videos)))
        self.assertEqual(len(updated_videos), nb_videos, "Should have updated 3 new videos. {} instead".format(len(updated_videos)))

        self.assertEqual(self.dataset.scan_state, ComputingStateType.SUCCESS, "Scanning state of dataset {} should be 'success'. {} instead".format(self.dataset.name, ComputingStateType.label(self.dataset.scan_state)))


class VideoModelTestCase(TestCase):
    def setUp(self):
        self.dataset, self.created = Dataset.objects.get_or_create(name="test_dataset", description="Dataset for tests")

        self.dataset.scan_video_folder()
        self.video = self.dataset.videos.get(full_name='1_shot.avi')
        self.video.prepare(overwrite=True)

    def test_videos_prepare(self):
        """Extract audio, convert video to web formats"""
        OVERWRITE = False

        for video in self.dataset.videos.all():
            video.prepare(overwrite=OVERWRITE)

        # Check files and folders
        converted_folder = self.dataset.converted_video_path
        web_folder = self.dataset.web_video_path

        paths = [
            os.path.join(test_path, "audio", "1_shot.wav"),
            os.path.join(test_path, "audio", "anger.wav"),
            os.path.join(test_path, "audio", "neutral.wav"),


            os.path.join(converted_folder, "1_shot.mp4"),
            os.path.join(converted_folder, "1_shot.webm"),

            os.path.join(converted_folder, "anger.mp4"),
            os.path.join(converted_folder, "anger.webm"),

            os.path.join(converted_folder, "neutral.mp4"),
            os.path.join(converted_folder, "neutral.webm"),


            os.path.join(web_folder, "1_shot.mp4"),
            os.path.join(web_folder, "1_shot.webm"),

            os.path.join(web_folder, "anger.mp4"),
            os.path.join(web_folder, "anger.webm"),

            os.path.join(web_folder, "neutral.mp4"),
            os.path.join(web_folder, "neutral.webm"),
        ]

        for path in paths:
            self.assertTrue(os.path.exists(path), "{} should exists".format(path))

        # Check db entries
        no_emotion = self.dataset.videos.get(full_name="1_shot.avi")
        anger = self.dataset.videos.get(full_name="anger.avi")
        neutral = self.dataset.videos.get(full_name="neutral.avi")

        videos = [
            no_emotion,
            anger,
            neutral
        ]

        for video in videos:
            self.assertIsNotNone(video, "{} does not exists".format(video.name))
            self.assertGreater(video.duration, 0, "{} duration should be greater than 0".format(video.name))
            self.assertEqual(video.preparation_state, ComputingStateType.SUCCESS, "Preparation state of video {} should be 'success'. {} instead".format(video.full_name, ComputingStateType.label(video.preparation_state)))


DatasetModelTestCase = override_settings(WEBCLIENT_VIDEOS_PATH=os.path.join(test_path, "web"))(DatasetModelTestCase)
VideoModelTestCase = override_settings(WEBCLIENT_VIDEOS_PATH=os.path.join(test_path, "web"))(VideoModelTestCase)