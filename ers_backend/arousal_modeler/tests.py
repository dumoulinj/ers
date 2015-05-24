import os

from django.test import TestCase
from django.test.utils import override_settings
from dataset_manager.enums import FeatureType, ComputingStateType
from dataset_manager.models import Dataset
from django.conf import settings

test_path = os.path.join(settings.DATASET_DEFAULT_PATH, 'test_dataset')

class ArousalModelerTestCase(TestCase):
    def setUp(self):
        self.dataset, self.created = Dataset.objects.get_or_create(name="test_dataset", description="Dataset for tests")

        self.dataset.scan_video_folder()
        self.video = self.dataset.videos.get(full_name='1_shot.avi')
        self.video.prepare()

        self.feature_types = [FeatureType.ENERGY, FeatureType.SHOT_CUT_DENSITY]

        self.video.extract_features(feature_types=self.feature_types)

    def test_compute_arousal(self):
        """Verify the computation of arousal"""
        self.video.model_arousal(self.feature_types, overwrite=True)

        arousal = self.video.arousal

        self.assertEqual(len(arousal.arousal_curve), self.video.nb_frames, "Arousal curve size of video {} should be {}. {} instead".format(self.video.full_name, len(arousal.arousal_curve), self.video.nb_frames))
        self.assertEqual(self.video.arousal_modeling_state, ComputingStateType.SUCCESS, "Arousal modeling state of video {} should be 'success'. {} instead".format(self.video.full_name, ComputingStateType.label(self.video.arousal_modeling_state)))


ArousalModelerTestCase = override_settings(WEBCLIENT_VIDEOS_PATH=os.path.join(test_path, "web"))(ArousalModelerTestCase)
