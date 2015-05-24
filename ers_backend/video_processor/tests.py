import os

from django.test import TestCase
from django.test.utils import override_settings
from dataset_manager.enums import FeatureType, ComputingStateType
from dataset_manager.models import Dataset
from django.conf import settings

test_path = os.path.join(settings.DATASET_DEFAULT_PATH, 'test_dataset')

class VideoProcessorTestCase(TestCase):
    def setUp(self):
        self.dataset, self.created = Dataset.objects.get_or_create(name="test_dataset", description="Dataset for tests")

        self.dataset.scan_video_folder()
        self.video = self.dataset.videos.get(full_name='1_shot.avi')
        self.video.prepare(overwrite=True)

    def test_detect_shot_boundaries(self):
        """Verify that the shot boundary detection works as expected"""
        self.video.detect_shot_boundaries()
        self.assertEqual(self.video.shot_boundaries_detection_state, ComputingStateType.SUCCESS, "Shot boundary detection state of video {} should be 'success'. {} instead".format(self.video.full_name, ComputingStateType.label(self.video.shot_boundaries_detection_state)))

        video = self.dataset.videos.get(full_name='neutral.avi')
        video.prepare()
        video.detect_shot_boundaries()
        self.assertEqual(video.shot_boundaries_detection_state, ComputingStateType.WARNING, "Shot boundary detection state of video {} should be 'success'. {} instead".format(video.full_name, ComputingStateType.label(video.shot_boundaries_detection_state)))

    def test_compute_video_features(self):
        """Verify the computation of video features"""
        OVERWRITE = True
        feature_types = [FeatureType.SHOT_CUT_DENSITY]

        self.video.extract_features(feature_types=feature_types, overwrite=OVERWRITE)

        self.assertEqual(self.video.video_part.features.count(), len(feature_types), "Video {} should have {} video features entry. {} instead".format(self.video.full_name, len(feature_types), self.video.video_part.features.count()))
        self.assertEqual(self.video.feature_extraction_state, ComputingStateType.SUCCESS, "Feature extraction state of video {} should be 'success'. {} instead".format(self.video.full_name, ComputingStateType.label(self.video.feature_extraction_state)))

        for feature_type in feature_types:
            functional_values = self.video.video_part.features.get(type=feature_type).values
            for functional, values in functional_values.iteritems():
                self.assertEqual(len(values), self.video.nb_frames, "Video features ({}) size of video {} should be {}. {} instead".format(functional, self.video.full_name, self.video.nb_frames, len(values)))



VideoProcessorTestCase = override_settings(WEBCLIENT_VIDEOS_PATH=os.path.join(test_path, "web"))(VideoProcessorTestCase)

# from django.test import TestCase
# from dataset_manager.models import Dataset
# from video_processor.models import ShotsDetection, ECR, ColorHistograms
#
#
# class VideoProcessorModelsTestCase(TestCase):
#     def setUp(self):
#         self.dataset = Dataset.objects.create(name="test_dataset", base_path="/Users/djo3l/Dev/Datasets/TestDataset")
#         self.dataset.prepare(overwrite=False)
#         self.shots_detection = ShotsDetection(algos=[ECR(threshold=0.61),])
#         #self.shots_detection = ShotsDetection(algos=[ECR(threshold=0.61), ColorHistograms(threshold=0.7),])
#         #self.shots_detection = ShotsDetection(algos=[ColorHistograms(threshold=0.7),])
#
#     def test_shots_detection(self):
#         MIN_PRECISION = 0.5
#         MIN_RECALL = 0.5
#
#         for video in self.dataset.video_set.all():
#             # Detect shot boundaries
#             self.shots_detection.detect(video)
#             video_shots = self.shots_detection.videoshots_set.get(video=video)
#
#             self.assertGreater(len(video_shots.shots), 0, "Number of shots should be > 0")
#             self.assertGreater(len(video_shots.shot_boundaries), 0, "Number of shot boundaries should be > 0")
#             self.assertEqual(len(video_shots.shots), len(video_shots.shot_boundaries) + 1, "Number of shots should be number of shot boundaries + 1")
#
#             # Evaluate the result
#             self.shots_detection.evaluate(video)
#             video_shots = self.shots_detection.videoshots_set.get(video=video)
#
#             self.assertGreaterEqual(video_shots.precision, MIN_PRECISION, "Precision has to be >= {}".format(MIN_PRECISION))
#             self.assertGreaterEqual(video_shots.recall, MIN_RECALL, "Recall has to be >= {}".format(MIN_RECALL))
