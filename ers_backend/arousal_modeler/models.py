import numpy
from jsonfield.fields import JSONField
from django.db import models
from arousal_modeler.utils import list_normalization, smooth_kaiser
from dataset_manager.enums import FeatureType, FeatureFunctionType
from math import fabs


class ArousalModeler():
    """
    Affection arousal modeling class, used to simulate the variation of affection states in the multimedia element.
    Modeling consists of two steps: features pre-processing and curves generation.
    """
    def __init__(self, feature_types):
        self.features = dict()
        self.normalized_features = dict()
        self.processed_features = dict()
        self.arousal_curve = numpy.array([])
        self.arousal_crests = list()
        self.arousal_troughs = list()
        self.arousal_partitions = list()
        self.arousal_diff = numpy.array([])

        #self.audio_feature_types = (FeatureType.SOUND_ENERGY,)
        #self.video_feature_types = (FeatureType.SHOT_CUT_DENSITY,)
        self.feature_types = feature_types
        # self.feature_functions = dict()
        # for feature_type in feature_types:
        #     self.feature_functions[feature_type] = FeatureType.functions[feature_type]


    def _get_features(self, video):
        """
        Simply add the different video and audio features to a single list.
        """

        for feature_type in self.feature_types:
            feature_function = FeatureFunctionType.VALUE
            u_feature_function = str(feature_function)
            values = list()
            if feature_type in FeatureType.audio_features:
                multimedia_part = video.audio_part
            elif feature_type in FeatureType.video_features:
                multimedia_part = video.video_part

            feature = multimedia_part.features.get(type=feature_type)
            values = feature.values[u_feature_function]

            # Keep only values in the list (throw away index)
            values = [sublist[1] for sublist in values]

            # Control number of entries
            if len(values) < video.nb_frames:
                # Add Nones if not enough values
                values.extend([None]*(video.nb_frames - len(values)))
            elif len(values) > video.nb_frames:
                # Remove if too many values
                del values[video.nb_frames:]

            if not self.features.has_key(feature_type):
                self.features[feature_type]= dict()
            self.features[feature_type][feature_function] = values


    def _pre_processing(self):
        """
        Pre-processing of the features: normalization and smoothing. This allows to satisfy the two affection arousal
        criterions: comparability and smoothness.
        """
        # pre_processed_features = list()

        # Smoothing parameters
        window_len = 1000 #200
        beta = 8#4

        # Apply normalization and smoothing to each features lists
        for feature_type, feature_functions in self.features.iteritems():
            for feature_function, values in feature_functions.iteritems():
                # Normalization
                normalized_features = list_normalization(values)
                if not self.normalized_features.has_key(feature_type):
                    self.normalized_features[feature_type]= dict()
                self.normalized_features[feature_type][feature_function] = normalized_features

                # Smoothing
                smoothed_features = smooth_kaiser(normalized_features, window_len, beta)

                # Smoothed values normalization
                if len(smoothed_features) > 0:
                    norm_factor = max(numpy.absolute(normalized_features)) / max(numpy.absolute(smoothed_features))
                    smoothed_features *= norm_factor
                else:
                    smoothed_features = normalized_features

                # Add the preprocessed features
                if not self.processed_features.has_key(feature_type):
                    self.processed_features[feature_type]= dict()
                self.processed_features[feature_type][feature_function] = smoothed_features


    def _curves_generation(self,window_len,beta):
        """
        Affection arousal curves generation.
        """
        # Fuse all features into one numpy array
        features = list()
        for feature_type, functions_features in self.processed_features.iteritems():
            for function, values in functions_features.iteritems():
                features.append(values)

        fused_features = numpy.array(features)

        # Fusion (using linear weighted summarization)
        fused_features *= 1./ len(features)
        fused_features = numpy.sum(fused_features, axis=0)

        # Smoothing
        window_len = window_len #1000#400
        beta = beta #8#4

        smoothed_features = smooth_kaiser(fused_features, window_len, beta)

        # Smoothed values normalization
        try:
            norm_factor = max(numpy.absolute(fused_features)) / max(numpy.absolute(smoothed_features))
        except Exception as e:
            norm_factor = 1.

        smoothed_features *= norm_factor

        # Set the arousal curve
        self.arousal_curve = smoothed_features

    def _detect_crests(self,wsize,wstep,crest_intensity_threshold):
        """
        Crest detection. First, we detect the crest with a sliding window algorithm. Then, we remove the not-exciting-
        enough crests, compared to a threshold.
        """
        W_SIZE = wsize#10
        W_STEP = wstep#3

        CREST_INTENSITY_THRESHOLD = crest_intensity_threshold#0.1

        start = 0

        datas = list(self.arousal_curve)

        # Crest detection with slinding window algorithm
        while start + W_SIZE < len(datas):
            # Get the subwindow values
            _values = datas[start:start+W_SIZE]

            # Get the value and index of the max element (potential crest)
            max_val = max(_values)
            max_idx = _values.index(max_val)

            # If the element is in the middle of the subwindow, it's a crest, and we add it if not already done before
            if max_idx >= W_STEP and max_idx <= (W_SIZE - W_STEP):
                crest_idx = max_idx + start
                if crest_idx not in self.arousal_crests:
                    self.arousal_crests.append(crest_idx)

            # Go to the next subwindow
            start += W_STEP

        # Crest filtering with a threshold
        crests_to_keep = list()
        # First valley is the first element value
        valley1 = self.arousal_curve[0]

        # Prepare the list of crest idxs (add the last element, that would be the last valley)
        crest_idxs = list(self.arousal_crests[:])
        crest_idxs.append(len(self.arousal_curve-1))

        # Iterate over the different crest indexes, and verify that the crest is exciting enough
        for idx, crest_idx in enumerate(crest_idxs[:-1]):
            valley2 = min(self.arousal_curve[crest_idx:crest_idxs[idx+1]])
            crest_value = self.arousal_curve[crest_idx]

            # Difference of excitement between the crest and the lowest valley
            diff = max(crest_value - valley1, crest_value - valley2)

            # If not exciting enough, we will not keep it, so we store in this list only the exciting enough crests
            if diff >= CREST_INTENSITY_THRESHOLD:
                crests_to_keep.append(crest_idx)

            # The next valley is the current right valley
            valley1 = valley2

        # Assign the only crests that we keep
        self.arousal_crests = crests_to_keep

    def _detect_troughs(self,wsize,wstep,crest_intensity_threshold):
        """
        Troughs detection. First, we detect the troughs with a sliding window algorithm. Then, we remove the not-exciting-
        enough troughs, compared to a threshold.
        """
        W_SIZE = wsize#10
        W_STEP = wstep#3

        TROUGHS_INTENSITY_THRESHOLD = crest_intensity_threshold#0.1

        start = 0

        datas = list(self.arousal_curve)

        # Troughs detection with slinding window algorithm
        while start + W_SIZE < len(datas):
            # Get the subwindow values
            _values = datas[start:start+W_SIZE]

            # Get the value and index of the min element (potential trough)
            min_val = min(_values)
            min_idx = _values.index(min_val)

            # If the element is in the middle of the subwindow, it's a trough, and we add it if not already done before
            if min_idx >= W_STEP and min_idx <= (W_SIZE - W_STEP):
                trough_idx = min_idx + start
                if trough_idx not in self.arousal_troughs:
                    self.arousal_troughs.append(trough_idx)

            # Go to the next subwindow
            start += W_STEP

        # Troughs filtering with a threshold
        troughs_to_keep = list()
        # First valley is the first element value
        crest1 = self.arousal_curve[0]

        # Prepare the list of trough idxs (add the last element, that would be the last valley)
        trough_idxs = list(self.arousal_troughs[:])
        trough_idxs.append(len(self.arousal_curve-1))

        # Iterate over the different trough indexes, and verify that the trough is deep enough
        for idx, trough_idx in enumerate(trough_idxs[:-1]):
            crest2 = max(self.arousal_curve[trough_idx:trough_idxs[idx+1]])
            trough_value = self.arousal_curve[trough_idx]

            # Difference of excitement between the trough and the highest crest
            #diff = max(trough_value - crest1, trough_value - crest2)
            diff = max(crest1 - trough_value, crest2 - trough_value)

            # If not deep enough, we will not keep it, so we store in this list only the deep enough troughs
            if diff >= TROUGHS_INTENSITY_THRESHOLD:
                troughs_to_keep.append(trough_idx)

            # The next valley is the current right valley
            crest1 = crest2

        # Assign the only troughs that we keep
        self.arousal_troughs = troughs_to_keep


    def _detect_arousal_partitions(self):
        """
        Compute semi standard deviation (68%) range around each crest and trough that will be used to define different arousal partitions
        """
        extremities_list = self.arousal_crests + self.arousal_troughs
        if(len(extremities_list) > 0):
            extremities_list.sort()
            for extremity in extremities_list:
                # get ranges for crests
                if extremity in self.arousal_crests:
                    min_bound = 0
                    if len(self.arousal_partitions) > 0:
                        min_bound = self.arousal_partitions[-1][1]
                    for i in reversed(range(min_bound, extremity)):
                        if self.arousal_diff[i] <= 0:
                            min_bound = i
                            break
                    max_bound = len(self.arousal_curve) -1
                    for i in range(extremity, len(self.arousal_curve)-1):
                        if self.arousal_diff[i] >= 0:
                            max_bound = i
                            break
                    if (max_bound - extremity) > (extremity - min_bound) and (extremity + (extremity - min_bound)) <= (len(self.arousal_curve) -1):
                        max_bound = extremity + (extremity - min_bound)
                    else:
                        min_bound = extremity - (max_bound - extremity)


                        # max_slope = max(diff_partition)
                        # threshold = max_slope * 0.68
                        # for i in range(partition[0],partition[1]):
                        #     if fabs(self.arousal_diff[i]) >= threshold:
                        #         partition[0] = i
                        #         break
                        # for i in reversed(range(partition[0],partition[1])):
                        #     if fabs(self.arousal_diff[i]) >= threshold:
                        #         partition[0] = i
                        #         break

                #get ranges for troughs
                else:
                    min_bound = 0
                    if len(self.arousal_partitions) > 0:
                        min_bound = self.arousal_partitions[-1][1]
                    for i in reversed(range(min_bound, extremity)):
                        if self.arousal_diff[i] >= 0:
                            min_bound = i
                            break
                    max_bound = len(self.arousal_curve) -1
                    for i in range(extremity, len(self.arousal_curve)-1):
                        if self.arousal_diff[i] <= 0:
                            max_bound = i
                            break
                    if (max_bound - extremity) > (extremity - min_bound) and (extremity + (extremity - min_bound)) <= (len(self.arousal_curve) -1):
                        max_bound = extremity + (extremity - min_bound)
                    else:
                        min_bound = extremity - (max_bound - extremity)

                curve_partition = [fabs(x) for x in self.arousal_curve[min_bound:max_bound]]
                curve = list()
                for i, val in enumerate(curve_partition):
                    curve.append([i, val])
                std = numpy.std(curve,0)
                min_bound = int(extremity - std[0])
                max_bound = int(extremity + std[0])
                self.arousal_partitions.append([min_bound,max_bound])


    def _compute_arousal_diff(self):
        """
        Compute first derivative of the arousal curve
        """
        if(len(self.arousal_curve) > 0):
            self.arousal_diff = numpy.diff(self.arousal_curve)


    @staticmethod
    def transform_to_list_with_idx(list_to_transform):
        # If numpy array, convert to list
        if isinstance(list_to_transform, list):
            input_list = list_to_transform
        else:
            input_list = list_to_transform.tolist()

        result = list()

        # Add index
        for i, val in enumerate(input_list):
            result.append([i, val])

        return result


class Arousal(models.Model):
    """
    Emotional part of the video, containing arousal curve, arousal_crests.
    """
    video = models.OneToOneField("dataset_manager.Video", related_name='arousal')
    arousal_curve = JSONField()
    arousal_crests = JSONField()
    arousal_troughs = JSONField()
    arousal_diff = JSONField()
    arousal_partitions = JSONField()

    used_features = JSONField(default={})

    def model(self, feature_types, configuration=None):
        window_len=1000
        wsize=10
        wstep=3
        crest_intensity_threshold=0.1
        beta=8

        if configuration:
            window_len = configuration["window_len"]
            wsize = configuration["wsize"]
            wstep = configuration["wstep"]
            crest_intensity_threshold = ["crest_intensity_threshold"]
            beta = ["beta"]

        arousal_modeler = ArousalModeler(feature_types)
        arousal_modeler._get_features(self.video)
        arousal_modeler._pre_processing()
        arousal_modeler._curves_generation(window_len, beta)

        if len(arousal_modeler.arousal_curve) > 0:
            arousal_modeler._detect_crests(wsize,wstep,crest_intensity_threshold)
            arousal_modeler._detect_troughs(wsize,wstep,crest_intensity_threshold)
            arousal_modeler._compute_arousal_diff()
            arousal_modeler._detect_arousal_partitions()

        # Prepare data to return in a usable format for the web interface
        curve = list()
        crests = list()
        troughs = list()
        diff = list()
        partitions = list()

        for i, val in enumerate(arousal_modeler.arousal_curve.tolist()):
            curve.append([i, val])

        for crest in arousal_modeler.arousal_crests:
            crests.append([crest, arousal_modeler.arousal_curve[crest]])

        for trough in arousal_modeler.arousal_troughs:
            troughs.append([trough, arousal_modeler.arousal_curve[trough]])

        for i, val in enumerate(arousal_modeler.arousal_diff.tolist()):
            diff.append([i, val*1000])

        for min_range, max_range in arousal_modeler.arousal_partitions:
            partitions.append([[min_range,arousal_modeler.arousal_curve[min_range]],[max_range, arousal_modeler.arousal_curve[max_range]]])

        used_features = dict()
        # Processed features
        for feature_type in arousal_modeler.feature_types:
            processed_values = dict()
            normalized_values = dict()

            function_type = FeatureFunctionType.VALUE
            transformed = ArousalModeler.transform_to_list_with_idx(arousal_modeler.processed_features[feature_type][function_type])
            processed_values[function_type] = transformed

            transformed = ArousalModeler.transform_to_list_with_idx(arousal_modeler.normalized_features[feature_type][function_type])
            normalized_values[function_type] = transformed

            if feature_type in FeatureType.audio_features:
                multimedia_part = self.video.audio_part
            elif feature_type in FeatureType.video_features:
                multimedia_part = self.video.video_part

            features = multimedia_part.features.get(type=feature_type)
            features.values_processed = processed_values
            features.values_normalized = normalized_values
            features.save()

            used_features[feature_type] = processed_values

        self.used_features = used_features
        # processed_shot_cut_density = ArousalModeler.transform_to_list_with_idx(arousal_modeler.processed_features[FeatureType.SHOT_CUT_DENSITY])
        # processed_sound_energy = ArousalModeler.transform_to_list_with_idx(arousal_modeler.processed_features[FeatureType.SOUND_ENERGY])
        #
        # # Normalized features
        # normalized_shot_cut_density = ArousalModeler.transform_to_list_with_idx(arousal_modeler.normalized_features[FeatureType.SHOT_CUT_DENSITY])
        # normalized_sound_energy = ArousalModeler.transform_to_list_with_idx(arousal_modeler.normalized_features[FeatureType.SOUND_ENERGY])
        #
        # # Save processed features for shot cut density
        # video_part_features = self.video.video_part.features.get(features_type=FeatureType.SHOT_CUT_DENSITY)
        # video_part_features.values_processed = processed_shot_cut_density
        # video_part_features.values_normalized = normalized_shot_cut_density
        # video_part_features.save()
        #
        # # Save processed features for sound energy
        # audio_part_features = self.video.audio_part.features.get(features_type=FeatureType.SOUND_ENERGY)
        # audio_part_features.values_processed = processed_sound_energy
        # audio_part_features.values_normalized = normalized_sound_energy
        # audio_part_features.save()

        # Save model
        self.arousal_curve = curve
        self.arousal_crests = crests
        self.arousal_troughs = troughs
        self.arousal_diff = diff
        self.arousal_partitions = partitions
        self.save()

