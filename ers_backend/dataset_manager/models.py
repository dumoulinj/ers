import os
import logging
import collections
import shutil
from PIL import Image, ImageStat
from converter.ffmpeg import FFMpeg
import cv2
from cv2 import cv
from django.db import models
from swampdragon.models import SelfPublishModel
from django_enumfield import enum
from jsonfield.fields import JSONField
from django.conf import settings
from arousal_modeler.models import Arousal
from audio_processor.models import OpensmileExtractor
from dataset_manager.dragon_serializers import VideoSerializer, DatasetSerializer
from dataset_manager.enums import FeatureType, ComputingStateType, EmotionType, FeatureFunctionType
from ers_backend.utils import is_video, convert_video_2_mp4, convert_video_2_webm, extract_wav_from_video, \
    mkdir_if_not_exists, is_emotion_dir, replace_right
from video_processor.enums import ShotBoundariesDetectionAlgorithmType
from video_processor.models import ShotsDetection, ECR, ColorHistograms


logger = logging.getLogger(__name__)

#-----------------------------------------------------------------------------------------------------------------------
# Dataset
#-----------------------------------------------------------------------------------------------------------------------
class Dataset(SelfPublishModel, models.Model):
    """
    Model representing a dataset. It contains a list of multimedia elements.
    The prepare() method is used to create the directory structure, list the videos, and create the database entries.
    """

    serializer_class = DatasetSerializer

    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(default="Dataset description...")

    # Monitoring
    preparation_state = enum.EnumField(ComputingStateType, default=ComputingStateType.NO)

    scan_state = enum.EnumField(ComputingStateType, default=ComputingStateType.NO)

    videos_preparation_state = enum.EnumField(ComputingStateType, default=ComputingStateType.NO)
    videos_preparation_nb_videos_done = models.IntegerField(default=0)

    shot_boundaries_detection_state = enum.EnumField(ComputingStateType, default=ComputingStateType.NO)
    shot_boundaries_detection_nb_videos_done = models.IntegerField(default=0)

    feature_extraction_state = enum.EnumField(ComputingStateType, default=ComputingStateType.NO)
    feature_extraction_nb_videos_done = models.IntegerField(default=0)

    arousal_modeling_state = enum.EnumField(ComputingStateType, default=ComputingStateType.NO)
    arousal_modeling_nb_videos_done = models.IntegerField(default=0)

    available_features = JSONField(default=[], blank=True)

    # Properties
    def _base_path(self):
        return os.path.join(settings.DATASET_DEFAULT_PATH, self.name)
    base_path = property(_base_path)

    def _video_path(self):
        return os.path.join(self.base_path, "video")
    video_path = property(_video_path)

    def _converted_video_path(self):
        return os.path.join(self.base_path, "converted")
    converted_video_path = property(_converted_video_path)

    def _web_video_path(self):
        return settings.WEBCLIENT_VIDEOS_PATH.replace("$datasetId$", str(self.id))
    web_video_path = property(_web_video_path)

    def _audio_path(self):
        return os.path.join(self.base_path, "audio")
    audio_path = property(_audio_path)

    def _frame_path(self):
        return os.path.join(self.base_path, "frames")
    frame_path = property(_frame_path)

    def _ground_truth_path(self):
        return os.path.join(self.base_path, "ground_truth")
    ground_truth_path = property(_ground_truth_path)

    def _shot_boundaries_ground_truth_path(self):
        return os.path.join(self.ground_truth_path, "shot_boundaries")
    shot_boundaries_ground_truth_path = property(_shot_boundaries_ground_truth_path)

    def _video_list(self):
        videos = list()
        for elt in os.listdir(self.video_path):
            if is_video(elt):
                videos.append((elt, None))
            elif is_emotion_dir(os.path.join(self.video_path, elt)):
                for sub_elt in os.listdir(os.path.join(self.video_path, elt)):
                    if is_video(sub_elt):
                        videos.append((sub_elt, EmotionType.get_enum_from_label(elt)))
        return videos
    video_list = property(_video_list)

    def _nb_videos(self):
        return self.videos.count()
    nb_videos = property(_nb_videos)


    # Methods
    def get_video_path(self, emotion):
        if emotion is not None:
            return os.path.join(self.video_path, EmotionType.labels[emotion])
        else:
            return self.video_path

    def prepare(self):
        """
        Prepare the dataset, create directories.
        """
        self.preparation_state = ComputingStateType.IN_PROGRESS
        self.save()

        logger.info("Preparing dataset %s...", self.name)

        # Check and create directories
        directories = [
            self.base_path,
            self.video_path,
            self.audio_path,
            self.converted_video_path,
            self.web_video_path,
            self.frame_path,
            self.ground_truth_path,
            self.shot_boundaries_ground_truth_path
        ]

        self.preparation_state = ComputingStateType.SUCCESS

        for directory in directories:
            if not mkdir_if_not_exists(directory):
                logger.error("Unable to create directory: %s", directory)
                self.preparation_state = ComputingStateType.FAILED

        self.save()
        logger.debug("Preparation for dataset %s done\n", self.name)


    def create_or_update_video(self, video_filename, emotion):
        """
        Create or update a video element, get information, and associate with the dataset
        """
        updated = False

        # Create/update the multimedia element
        if self.videos.filter(full_name=video_filename).exists():
            logger.debug("Updating multimedia element for: %s", video_filename)
            updated = True
            video = self.videos.get(full_name=video_filename)
            audio_part = video.audio_part
            video_part = video.video_part
        else:
            logger.debug("Creating multimedia element for: %s", video_filename)
            video = Video()
            audio_part = AudioPart()
            video_part = VideoPart()


        video.dataset = self
        video.full_name = video_filename
        video.emotion = emotion
        video.save()

        audio_part.video = video
        audio_part.save()

        video_part.video = video
        video_part.save()

        logger.info("Video created/updated: %s", video_filename)
        return updated


    def scan_video_folder(self):
        """
        Scan video folder, look for video files, and create video instances.
        """
        self.scan_state = ComputingStateType.IN_PROGRESS
        self.save()

        logger.info("Scanning video folder for dataset %s...", self.name)

        created_videos = list()
        updated_videos = list()

        # List videos
        for video_filename, emotion in self.video_list:
            if self.create_or_update_video(video_filename, emotion):
                updated_videos.append((video_filename, emotion))
            else:
                created_videos.append((video_filename, emotion))

        self.scan_state = ComputingStateType.SUCCESS
        self.save()

        logger.debug("Scanning video folder for dataset %s done\n", self.name)

        return [created_videos, updated_videos]

    def prepare_videos(self, overwrite=False):
        """
        Prepare each videos of the dataset
        """
        self.videos_preparation_nb_videos_done = 0
        self.videos_preparation_state = ComputingStateType.IN_PROGRESS
        self.save()

        logger.info("Preparing videos for dataset %s...", self.name)

        errors = False
        warnings = False

        for video in self.videos.all():
            video.prepare(overwrite=overwrite)
            if video.preparation_state == ComputingStateType.FAILED:
                errors = True
            elif video.preparation_state == ComputingStateType.WARNING:
                warnings = True

            self.videos_preparation_nb_videos_done += 1
            self.save()

        if errors:
            self.videos_preparation_state = ComputingStateType.FAILED
            logger.error("Error during the preparation of videos for dataset %s\n", self.name)
        elif warnings:
            self.videos_preparation_state = ComputingStateType.WARNING
            logger.warning("Control that the preparation of videos for dataset %s has worked\n", self.name)
        else:
            self.videos_preparation_state = ComputingStateType.SUCCESS
            logger.debug("Preparing videos for dataset %s done\n", self.name)

        self.save()



    def detect_shot_boundaries(self, configuration=None):
        """
        Detect shot boundaries for each videos of the dataset.
        """
        self.shot_boundaries_detection_nb_videos_done = 0
        self.shot_boundaries_detection_state = ComputingStateType.IN_PROGRESS
        self.save()

        logger.info("Detecting shot boundaries for dataset %s...", self.name)

        errors = False
        warnings = False

        # Prepare shot detection
        shots_detection = ShotsDetection()
        shots_detection.save()

        if configuration:
            for entry in configuration:
                algorithm = None
                if(entry['value'] == ShotBoundariesDetectionAlgorithmType.COLOR_HISTOGRAM):
                    algorithm = ColorHistograms()
                    algorithm.type = ShotBoundariesDetectionAlgorithmType.COLOR_HISTOGRAM
                else:
                    algorithm = ECR()
                    algorithm.type = ShotBoundariesDetectionAlgorithmType.ECR

                algorithm.threshold = entry['threshold']
                algorithm.shots_detection = shots_detection
                algorithm.save()
        else:
            # Prepare default algorithm
            algorithm = ECR()
            algorithm.type = ShotBoundariesDetectionAlgorithmType.ECR
            algorithm.shots_detection = shots_detection
            algorithm.threshold = 0.7
            algorithm.save()

            logger.debug("Using default configuration: ECR with threshold=%s" % (algorithm.threshold))

        for video in self.videos.all():
            try:
                video.detect_shot_boundaries(shots_detection)

                if video.shot_boundaries_detection_state == ComputingStateType.FAILED:
                    errors = True
                elif video.shot_boundaries_detection_state == ComputingStateType.WARNING:
                    warnings = True
            except:
                errors = True

            self.shot_boundaries_detection_nb_videos_done += 1
            self.save()

        if errors:
            self.shot_boundaries_detection_state = ComputingStateType.FAILED
            logger.error("Error during the detection of shot boundaries for dataset %s\n", self.name)
        elif warnings:
            self.shot_boundaries_detection_state = ComputingStateType.WARNING
            logger.warning("Control that the shot boundaries detection for dataset %s has worked\n", self.name)
        else:
            self.shot_boundaries_detection_state = ComputingStateType.SUCCESS
            logger.debug("Shot boundaries detection for dataset %s done", self.name)

        self.save()


    def extract_features(self, feature_types=None, overwrite=False):
        self.feature_extraction_state = ComputingStateType.IN_PROGRESS
        self.feature_extraction_nb_videos_done = 0
        self.save()

        logger.info("Extracting features for dataset %s...", self.name)

        errors = False
        warnings = False

        for video in self.videos.all():
            try:
                video.extract_features(feature_types=feature_types, overwrite=overwrite)

                if video.feature_extraction_state == ComputingStateType.FAILED:
                    errors = True
                elif video.feature_extraction_state == ComputingStateType.WARNING:
                    warnings = True
            except:
                errors = True

            self.feature_extraction_nb_videos_done += 1
            self.save()

        if errors:
            self.feature_extraction_state = ComputingStateType.FAILED
            logger.error("Error during the features extraction for dataset %s\n", self.name)
        elif warnings:
            self.feature_extraction_state = ComputingStateType.WARNING
            logger.warning("Control that the features extraction for dataset %s has worked\n", self.name)
        else:
            self.feature_extraction_state = ComputingStateType.SUCCESS
            logger.debug("Features extraction for dataset %s done", self.name)

        if not errors:
            if overwrite:
                self.available_features = feature_types
            else:
                self.available_features = list(set(feature_types + self.available_features))

        self.save()

    def model_arousal(self, feature_types, overwrite=False):
        self.arousal_modeling_state = ComputingStateType.IN_PROGRESS
        self.arousal_modeling_nb_videos_done = 0
        self.save()

        logger.info("Modeling arousal for dataset %s...", self.name)

        errors = False
        warnings = False

        for video in self.videos.all():
            try:
                video.model_arousal(feature_types, overwrite=overwrite)

                if video.arousal_modeling_state == ComputingStateType.FAILED:
                    errors = True
                elif video.arousal_modeling_state == ComputingStateType.WARNING:
                    warnings = True
            except:
                errors = True

            self.arousal_modeling_nb_videos_done += 1
            self.save()

        if errors:
            self.arousal_modeling_state = ComputingStateType.FAILED
            logger.error("Error during the arousal modeling for dataset %s\n", self.name)
        elif warnings:
            self.arousal_modeling_state = ComputingStateType.WARNING
            logger.warning("Control that the arousal modeling for dataset %s has worked\n", self.name)
        else:
            self.arousal_modeling_state = ComputingStateType.SUCCESS
            logger.debug("Arousal modeling for dataset %s done", self.name)

        self.save()


#-----------------------------------------------------------------------------------------------------------------------
# Video
#-----------------------------------------------------------------------------------------------------------------------

class Video(SelfPublishModel, models.Model):
    """
    Model representing a multimedia element. A multimedia element consists of general information, an embedded video
    and an embedded audio.
    """

    serializer_class = VideoSerializer

    dataset = models.ForeignKey(Dataset, related_name='videos')

    shots_detections = models.ManyToManyField('video_processor.ShotsDetection', through='video_processor.VideoShotsResult')

    full_name = models.CharField(max_length=50, blank=False)
    description = models.TextField(max_length=400, blank=True)
    emotion = enum.EnumField(EmotionType, null=True, default=None)

    # Information fields
    format = models.CharField(max_length=50, blank=True)
    duration = models.FloatField(default=0.)
    bitrate = models.FloatField(default=0.)

    # Time frame annotations
    #time_frame_annotations = ListField(EmbeddedModelField('timeframe_annotator.TimeFrameAnnotation'))

    # Ground truth
    shot_boundaries_ground_truth = JSONField(load_kwargs={'object_pairs_hook': collections.OrderedDict})

    # Monitoring
    preparation_state = enum.EnumField(ComputingStateType, default=ComputingStateType.NO)
    shot_boundaries_detection_state = enum.EnumField(ComputingStateType, default=ComputingStateType.NO)
    feature_extraction_state = enum.EnumField(ComputingStateType, default=ComputingStateType.NO)
    arousal_modeling_state = enum.EnumField(ComputingStateType, default=ComputingStateType.NO)

    available_features = JSONField(default=[])

    # Properties
    def _name(self):
        filename, extension = os.path.splitext(self.full_name)
        return filename
    name = property(_name)

    def _converted_filename(self):
        return self.name + ".mp4"
    converted_filename = property(_converted_filename)

    def _path(self):
        return os.path.join(self.dataset.converted_video_path, self.converted_filename)
    path = property(_path)

    def _original_path(self):
        return os.path.join(self.dataset.get_video_path(self.emotion), self.full_name)
    original_path = property(_original_path)

    def _audio_path(self):
        return os.path.join(self.dataset.audio_path, self.name + ".wav")
    audio_path = property(_audio_path)

    def _nb_frames(self):
        return int(self.duration * float(self.video_part.fps))
    nb_frames = property(_nb_frames)


    # Methods
    def prepare(self, overwrite=False):
        """
        Prepare video:
        - convert video format for web
        - extract audio in .wav
        """
        errors = False
        warnings = False

        logger.info("Prepare video: %s", self.name)

        # For monitoring
        self.preparation_state = ComputingStateType.IN_PROGRESS
        self.save()

        dataset = self.dataset

        # # Read shot boundaries ground truth
        # shot_boundaries_ground_truth = []
        # ground_truth_path = os.path.join(dataset.shot_boundaries_ground_truth_path, self.name + ".csv",)
        # if os.path.isfile(ground_truth_path):
        #     with open(ground_truth_path, "Ur") as f:
        #         for row in csv.reader(f, delimiter=','):
        #             for frame in row:
        #                 shot_boundaries_ground_truth.append(int(frame))
        # else:
        #     logger.debug("No ground truth file found for video %s", self.name)
        #
        # self.shot_boundaries_ground_truth = shot_boundaries_ground_truth
        # self.save()

        # Convert video and store in converted folder
        logger.debug("Converting video (in mp4 and webm): %s", self.full_name)

        if overwrite or not os.path.exists(self.path):
            result_state = convert_video_2_mp4(self.original_path, self.path)
            if result_state == ComputingStateType.FAILED:
                errors = True
            elif result_state == ComputingStateType.WARNING:
                warnings = True

        webm_path = replace_right(self.path, ".mp4", ".webm", 1)
        if overwrite or not os.path.exists(webm_path):
            result_state = convert_video_2_webm(self.original_path, webm_path)
            if result_state == ComputingStateType.FAILED:
                errors = True
            elif result_state == ComputingStateType.WARNING:
                warnings = True

        # Copying converted videos to web folder
        logger.debug("Copying converted videos for %s to web folder.", self.full_name)
        try:
            shutil.copy(self.path, self.dataset.web_video_path)
            shutil.copy(webm_path, self.dataset.web_video_path)
        except:
            errors = True

        # Extract wav and store in audio folder
        logger.debug("Extracting wav from video: %s", self.full_name)

        if overwrite or not os.path.exists(self.audio_path):
            result_state = extract_wav_from_video(self.path, self.audio_path)
            if result_state == ComputingStateType.FAILED:
                errors = True
            elif result_state == ComputingStateType.WARNING:
                warnings = True

        # Get video information
        info = FFMpeg().probe(self.path)

        if info:
            self.format = info.format.format
            self.duration = info.format.duration
            self.bitrate = info.format.bitrate
            self.save()

            self.audio_part.codec = info.audio.codec
            self.audio_part.channels = info.audio.audio_channels
            self.audio_part.samplerate = info.audio.audio_samplerate
            self.audio_part.save()

            self.video_part.codec = info.video.codec
            self.video_part.width = info.video.video_width
            self.video_part.height = info.video.video_height
            self.video_part.fps = info.video.video_fps
            self.video_part.save()
        else:
            errors = True

        # For monitoring
        if errors:
            self.preparation_state = ComputingStateType.FAILED
        elif warnings:
            self.preparation_state = ComputingStateType.WARNING
        else:
            self.preparation_state = ComputingStateType.SUCCESS

        self.save()

        logger.info("Preparation done for video %s\n", self.name)


    def detect_shot_boundaries(self, shots_detection=None):
        """
        Detect shot boundaries for the video, using the given algorithm configuration, or use a default algo
        configuration.
        """
        self.shot_boundaries_detection_state = ComputingStateType.IN_PROGRESS
        self.save()

        if shots_detection is None:
             # Prepare shot detection
            shots_detection = ShotsDetection()
            shots_detection.save()

            # Prepare default algorithm
            algo = ECR()
            algo.shots_detection = shots_detection
            algo.threshold = 0.7
            algo.save()

            logger.debug("Using default configuration: ECR with threshold=%s" % (algo.threshold))

        try:
            if shots_detection.detect(self) > 0:
                self.shot_boundaries_detection_state = ComputingStateType.SUCCESS
            else:
                self.shot_boundaries_detection_state = ComputingStateType.WARNING
        except:
            self.shot_boundaries_detection_state = ComputingStateType.FAILED

        self.save()

    def extract_features(self, feature_types=None, overwrite=False):
        """
        Compute features specified in features_type_list. Overwrite existing features if asked for.
        """
        errors = False
        warnings = False

        self.feature_extraction_state = ComputingStateType.IN_PROGRESS
        self.save()

        logger.info("Computing features for video: %s", self.name)

        if overwrite:
            # Remove all features
            logger.debug("Removing all features for video: %s" % (self.name))
            try:
                self.audio_part.features.all().delete()
                self.video_part.features.all().delete()
            except:
                logger.warning("A problem occured when removing features for video: %s" % (self.name))

        for feature_type in feature_types:
            if feature_type in FeatureType.audio_features:
                multimedia_part = self.audio_part
            elif feature_type in FeatureType.video_features:
                multimedia_part = self.video_part

            if multimedia_part.features.filter(type=feature_type).exists():
                continue
            else:
                logger.debug("Creating %s features for video: %s" % (feature_type, self.name))
                features = Features()
                features.multimedia_part = multimedia_part
                features.type = feature_type
                features.save()

            result_state = features.compute()

            if result_state == ComputingStateType.FAILED:
                errors = True
            elif result_state == ComputingStateType.WARNING:
                warnings = True

        # For monitoring
        if errors:
            self.feature_extraction_state = ComputingStateType.FAILED
        elif warnings:
            self.feature_extraction_state = ComputingStateType.WARNING
        else:
            self.feature_extraction_state = ComputingStateType.SUCCESS

        if not errors:
            if overwrite:
                self.available_features = list(feature_types)
            else:
                self.available_features = list(set(feature_types + self.available_features))

        self.save()

        logger.info("Features computed for video: %s", self.name)


    def model_arousal(self, feature_types, overwrite=False, configuration=None):
        logger.info("Modeling arousal for video: %s", self.full_name)

        if hasattr(self, 'arousal') and not self.arousal is None:
            if overwrite:
                arousal = self.arousal
            else:
                return
        else:
            arousal = Arousal()
            arousal.video = self

        self.arousal_modeling_state = ComputingStateType.IN_PROGRESS
        self.save()

        try:
            arousal.model(feature_types)
            self.arousal_modeling_state = ComputingStateType.SUCCESS
        except:
            self.arousal_modeling_state = ComputingStateType.FAILED

        self.save()

        logger.info("Arousal modelled for video: %s", self.full_name)

    def evaluate_sbd(self):
        video_shots_results = self.video_shots_results
        for video_shots_result in video_shots_results.all():
            shots_detection = video_shots_result.shots_detection
            shots_detection.evaluate(self)


class MultimediaPart(models.Model):
    """
    Abstract class, as parent class for AudioPart and VideoPart.
    """
    pass

class AudioPart(MultimediaPart):
    """
    Model representing the audio part of a multimedia element.
    """
    video = models.OneToOneField(Video, related_name='audio_part')

    # Information fields
    codec = models.CharField(max_length=50, blank=True)
    channels = models.IntegerField(default=0)
    samplerate = models.FloatField(default=0.)

class VideoPart(MultimediaPart):
    """
    Model representing the video part of a multimedia element.
    """
    video = models.OneToOneField(Video, related_name='video_part')

    # Information fields
    codec = models.CharField(max_length=50, blank=True)
    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)
    fps = models.FloatField(default=0.)


#-----------------------------------------------------------------------------------------------------------------------
# Features
#-----------------------------------------------------------------------------------------------------------------------

class Features(models.Model):
    multimedia_part = models.ForeignKey(MultimediaPart, related_name='features')

    type = enum.EnumField(FeatureType, default=FeatureType.ENERGY)

    values = JSONField()
    values_normalized = JSONField()
    values_processed = JSONField()

    def compute_shot_cut_density(self, video_shots_result=None):
        """
        Compute shot cut density using the video shots result passed in argument. If video shots result is not passed,
        last result is used. If no result available, create one with default algorithm parameters.
        :param video_shots_result:
        :return:
        """
        video = self.multimedia_part.video

        if video_shots_result:
            shot_cut_density = video_shots_result.compute_shot_cut_density()
        else:
            if video.video_shots_results.count() == 0:
                video.detect_shot_boundaries()
            # TODO: need to add a selected field on video_shots_results and use it here!
            shot_cut_density = video.video_shots_results.latest('id').compute_shot_cut_density()

        return shot_cut_density

    def compute_brightness(self):
        # Create video capture
        video = self.multimedia_part.video
        capture = cv2.VideoCapture(video.path)

        brightness = list()

        frame_nb = 0
        while True:
            f, crt_frame = capture.read()
            if crt_frame is None:
                # End of video
                break

            cv_size = lambda img: tuple(img.shape[1::-1])
            size = cv_size(crt_frame)
            cv_frame = cv2.cvtColor(crt_frame, cv2.COLOR_BGR2GRAY)

            im = Image.frombytes("L", size, cv_frame.tostring())

            stat = ImageStat.Stat(im)
            frame_brightness = stat.rms[0]

            brightness.append([frame_nb, frame_brightness])

            frame_nb += 1

        return {FeatureFunctionType.VALUE: brightness}


    def compute(self):
        if self.type in FeatureType.audio_features:
            opensmile_extractor = OpensmileExtractor()
            try:
                extracted_features = opensmile_extractor.compute(self)
            except Exception as e:
                logger.error(e.strerror)
                return ComputingStateType.FAILED
        elif self.type in FeatureType.video_features:
            if self.type == FeatureType.SHOT_CUT_DENSITY:
                try:
                    extracted_features = self.compute_shot_cut_density()
                except Exception as e:
                    return ComputingStateType.FAILED
            elif self.type == FeatureType.BRIGHTNESS:
                try:
                    extracted_features = self.compute_brightness()
                except:
                    return ComputingStateType.FAILED

        if len(extracted_features) > 0 :
            self.values = extracted_features
            self.save()
            return ComputingStateType.SUCCESS
        else:
            return ComputingStateType.WARNING

