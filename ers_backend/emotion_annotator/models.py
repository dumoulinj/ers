__author__ = 'diana'

import logging
from dataset_manager.models import Video, Dataset
from django.db import models
from django_enumfield import enum
from jsonfield.fields import JSONField
from django.conf import settings
from emotion_annotator.enums import EmotionType
from arousal_modeler.utils import list_normalization, smooth_kaiser
import numpy as np


logger = logging.getLogger(__name__)

#-----------------------------------------------------------------------------------------------------------------------
# Class specifying the emotion for each frame
#-----------------------------------------------------------------------------------------------------------------------
class FrameEmotions:

    video = models.ForeignKey(Video, related_name='frameEmotions')
    frameTime = models.IntegerField() #in seconds
    emotion_type = enum.EnumField(EmotionType, default=EmotionType.NEUTRAL)


class Classification:

    all_features_normalized = list

    def _pre_processing(self):
        """
        Pre-processing of the features: normalization and smoothing. This allows to satisfy the two criteria:
        comparability and smoothness.
        """
        # pre_processed_features = list()

        # Smoothing parameters
        window_len = 1000 #200
        beta = 8#4

        # Apply normalization and smoothing to each features lists
        for features_type, values in self.video.features.iteritems():
            # Normalization
            normalized_features = list_normalization(values)

            # Smoothing
            smoothed_features = smooth_kaiser(normalized_features, window_len, beta)

            # Smoothed values normalization
            if len(smoothed_features) > 0:
                norm_factor = max(normalized_features) / max(smoothed_features)
                smoothed_features *= norm_factor
            else:
                smoothed_features = normalized_features

            # Add the preprocessed features
            self.all_normalized_features[features_type] = smoothed_features


    def _pre_processing(datasetNameList):
        """
        Pre-processing of all the videos in the dataset: feature normalization and smoothing
        """
        # pre_processed_features = list()

        training_data = np.array()

        # for name in datasetNameList:
        #     dataset, created = Dataset.objects(name=name)
        #     for video in dataset.videos.all()




def prepare_datasets_for_training(datasetNamesList):
    for name in datasetNamesList:
        dataset, created = Dataset.objects.get(name=name)
        logger.debug("Preparing dataset" + name + "for training...")
        #dataset.prepare(update=True, overwrite_converted=True, overwrite_audio=True)