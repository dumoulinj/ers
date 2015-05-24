import os

from django.test import TestCase
from django.test.utils import override_settings
import math
from dataset_manager.enums import FeatureType, ComputingStateType, FeatureFunctionType
from dataset_manager.models import Dataset
from django.conf import settings

test_path = os.path.join(settings.DATASET_DEFAULT_PATH, 'test_dataset')

class AudioProcessorTestCase(TestCase):
    def setUp(self):
        self.dataset, self.created = Dataset.objects.get_or_create(name="test_dataset", description="Dataset for tests")

        self.dataset.scan_video_folder()
        self.video = self.dataset.videos.get(full_name='1_shot.avi')
        self.video.prepare(overwrite=True)


    def test_compute_audio_features(self):
        """Verify the computation of audio features"""
        OVERWRITE = True
        feature_types = FeatureType.audio_features

        self.video.extract_features(feature_types=feature_types, overwrite=OVERWRITE)

        self.assertEqual(self.video.audio_part.features.count(), len(feature_types), "Video {} should have {} audio features entry. {} instead".format(self.video.full_name, len(feature_types), self.video.audio_part.features.count()))
        self.assertEqual(self.video.feature_extraction_state, ComputingStateType.SUCCESS, "Feature extraction state of video {} should be 'success'. {} instead".format(self.video.full_name, ComputingStateType.label(self.video.feature_extraction_state)))

        for feature_type in feature_types:
            functional_values = self.video.audio_part.features.get(type=feature_type).values
            for functional, values in functional_values.iteritems():
                if int(functional) == FeatureFunctionType.VALUE:
                    self.assertEqual(len(values), int(self.video.nb_frames), "Video features ({}) size of video {} should be {}. {} instead".format(functional, self.video.full_name, self.video.nb_frames, len(values)))
                else:
                    self.assertEqual(len(values), math.floor(self.video.nb_frames / self.video.video_part.fps), "Video features ({}) size of video {} should be {}. {} instead".format(functional, self.video.full_name, math.floor(self.video.nb_frames / self.video.video_part.fps), len(values)))
                
                
AudioProcessorTestCase = override_settings(WEBCLIENT_VIDEOS_PATH=os.path.join(test_path, "web"))(AudioProcessorTestCase)