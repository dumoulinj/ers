import json
import logging
import cv2, os
from cv2 import cv
from django.conf import settings
from django.db import models
from math import exp
from django_enumfield import enum
from model_utils.managers import InheritanceManager
from PIL import Image, ImageStat

import time

import numpy
from dataset_manager.enums import ComputingStateType, FeatureFunctionType
from video_processor.enums import ShotBoundaryType, ShotBoundariesDetectionAlgorithmType

logger = logging.getLogger(__name__)




#-----------------------------------------------------------------------------------------------------------------------
# Shot detection models
#-----------------------------------------------------------------------------------------------------------------------

class ShotsDetection(models.Model):
    """
    Model representing one particular shots detection execution, with its associated configuration. It contains
    a list of algos that are used, and a list of resulting videos shots.
    """
    date = models.DateTimeField(auto_now=True)

    def _make_decision(self, results):
        """
        TODO
        """
        # TODO
        is_shot = False
        confidence = 0
        threshold = results[0]["threshold"]
        sumConfidence = 0.0
        sumWeight = 0.0

        for result in results:
            # logger.info(result)
            # # Temp: if one is True, so its True
            # if result["result"] == True:
            #     is_shot = True
            confidence = result["confidence"]
            # print(confidence)
            #     break
            sumConfidence = sumConfidence + (result["confidence"] * result["weight"])
            sumWeight = sumWeight + result["weight"]
        # logger.info(is_shot)
        # logger.info(sumConfidence)
        # logger.info(sumWeight)
        # logger.info(threshold)

        is_shot = (sumConfidence / sumWeight) >= threshold
        # if(result["result"] or is_shot):
        #     print(threshold)
        #     print(sumConfidence)
        #     print(result["result"])
        #     print(is_shot)

        return is_shot, sumConfidence


    def detect(self, video):
        """
        Process the video and detect shot boundaries. Store shots and shot boundaries objects in corresponding model
        lists.
        """
        MIN_SHOT_DELAY = 5

        logger.info("Shot detection for %s", video.path)

        # Create and prepare video_shots_results instance
        video_shots_result = VideoShotsResult()
        video_shots_result.shots_detection = self
        video_shots_result.video = video
        video_shots_result.save()
        # Create video capture
        capture = cv2.VideoCapture(video.path)

        # Prepare variables
        previous_frame = None

        shot_nb = 0
        crt_frame_nb = 0
        previous_frame_nb = 0
        last_shot_endframe_nb = -10000
        start_frame_nb = 0

        nb_total_frames = video.nb_frames

        while True:
            f, crt_frame = capture.read()
            if crt_frame is None:
                # End of video
                break

            results = list()

            # Compare last 2 frames
            if not previous_frame is None:
                #crt_frame_timestamp = capture.get(cv.CV_CAP_PROP_POS_MSEC)
                crt_frame_nb = capture.get(cv.CV_CAP_PROP_POS_FRAMES)

                #print crt_frame_nb
                # cv2.imshow('prev', previous_frame)
                # cv2.imshow('crt', crt_frame)
                # cv2.waitKey(100)

                # Two shots need to be separated at least by MIN_SHOT_DELAY frames
                if crt_frame_nb - last_shot_endframe_nb > MIN_SHOT_DELAY:
                    # Apply all algos
                    #for algo in self.algos:
                    for algo in self.algos.all().select_subclasses():
                        result, confidence, diff = algo.is_boundary(previous_frame, crt_frame)
                        results.append({"algo": algo, "result": result, "confidence": confidence, "diff": diff,"weight": algo.weight,"threshold": algo.threshold})

                    # Make a decision by merging algos decisions
                    is_shot, confidence = self._make_decision(results)

                    # If there is a shot, we append the shot and the shot boundary entries to the corresponding lists
                    if is_shot:
                        end_frame_nb = previous_frame_nb

                        # Create shot and shot_boundary, and associate it with shots_detection
                        shot = Shot(video_shots_result=video_shots_result, shot_nb=shot_nb, start_frame=start_frame_nb, end_frame=end_frame_nb)
                        shot.save()

                        shot_boundary = ShotBoundary(video_shots_result=video_shots_result, frame=end_frame_nb)
                        shot_boundary.save()

                        shot_nb += 1
                        start_frame_nb = crt_frame_nb
                        last_shot_endframe_nb = previous_frame_nb

            previous_frame = crt_frame
            previous_frame_nb = crt_frame_nb

            # Show advance
            if settings.DEBUG:
                if crt_frame_nb % 100 == 0:
                    percentage = int(crt_frame_nb * 100. / nb_total_frames)
                print('Shot detection: {}/{} - {}%\r'.format(int(crt_frame_nb), int(nb_total_frames), percentage)),

        print

        # Add last shot
        end_frame_nb = previous_frame_nb - 1
        shot = Shot(video_shots_result=video_shots_result, shot_nb=shot_nb, start_frame=start_frame_nb, end_frame=end_frame_nb)
        shot.save()

        # Save models
        video_shots_result.save()
        self.save()

        # Log info
        logger.info("Number of detected shots: %s", shot_nb)

        return shot_nb

    def evaluate(self, video):
        """
        Evaluate results of shot boundary detection against ground truth. Compute precision and recall and store in
        model. Add also missed shot boundaries, allowing to visualize it later.
        """
        logger.info("Evaluate video: %s", video.path)
        margin = 10

        thruth = video.shot_boundaries_ground_truth if isinstance(video.shot_boundaries_ground_truth,list) else eval(video.shot_boundaries_ground_truth)

        gt_shot_boundaries = thruth
        video_shots_result = self.video_shots_results.get(video=video)
        shot_boundaries_iterator = iter(list(video_shots_result.shot_boundaries.all()))

        nb_true_positives = 0
        nb_false_positives = 0
        nb_misses = 0

        shot_boundary = shot_boundaries_iterator.next()

        shot_boundaries_iterator_end = False

        for gt_frame in gt_shot_boundaries:
            if not shot_boundaries_iterator_end:
                while abs(gt_frame - shot_boundary.frame) > margin and shot_boundary.frame - margin < gt_frame:
                    # False positive
                    shot_boundary.type = ShotBoundaryType.FALSE_POSITIVE
                    #new_shot_boundaries.append(shot_boundary)
                    shot_boundary.save()
                    nb_false_positives += 1

                    try:
                        shot_boundary = shot_boundaries_iterator.next()
                    except StopIteration:
                        shot_boundaries_iterator_end = True
                        break

                if abs(gt_frame - shot_boundary.frame) <= margin and shot_boundary.type != ShotBoundaryType.MISS:
                    # True positive
                    shot_boundary.type = ShotBoundaryType.TRUE_POSITIVE
                    #new_shot_boundaries.append(shot_boundary)
                    shot_boundary.save()
                    nb_true_positives += 1
                    try:
                        shot_boundary = shot_boundaries_iterator.next()
                    except StopIteration:
                        shot_boundaries_iterator_end = True
                else:
                    # Miss
                    miss_shot_boundary = ShotBoundary()
                    miss_shot_boundary.video_shots_result = video_shots_result
                    miss_shot_boundary.frame = gt_frame
                    miss_shot_boundary.type = ShotBoundaryType.MISS
                    miss_shot_boundary.save()
                    #new_shot_boundaries.append(miss_shot_boundary)
                    nb_misses += 1
            else:
                # Miss
                miss_shot_boundary = ShotBoundary()
                miss_shot_boundary.video_shots_result = video_shots_result
                miss_shot_boundary.frame = gt_frame
                miss_shot_boundary.type = ShotBoundaryType.MISS
                miss_shot_boundary.save()
                #new_shot_boundaries.append(miss_shot_boundary)
                nb_misses += 1




        # Precision: TruePos / (TruePos + FalsePos) ; Recall: TruePos / (TruePos + Misses)
        precision = float(nb_true_positives) / float(nb_true_positives + nb_false_positives)
        recall = float(nb_true_positives) / float(nb_true_positives + nb_misses)

        #print "True positives: ", nb_true_positives, "False positives: ", nb_false_positives, "Misses: ", nb_misses
        logger.debug("True positives: %s, False positives: %s, Misses: %s", nb_true_positives, nb_false_positives, nb_misses)
        #print "Precision: ", precision, "Recall: ", recall
        logger.debug("Precision: %s, Recall: %s", precision, recall)

        #video_shots.shot_boundaries = new_shot_boundaries
        video_shots_result.precision = precision
        video_shots_result.recall = recall
        video_shots_result.save()

    def take_thumbnails(self,video):
        # Create video capture
        capture = cv2.VideoCapture(video.path)

        run = True
        # Process the video frame by frame
        while run:
            f, crt_frame = capture.read()
            if crt_frame == None:
                # End of video
                break

            video_shots_result = self.video_shots_results.get(video=video)
            shots = video_shots_result.shots.all()
            for s in shots:
                if s == shots[len(shots)-1]:
                    break
                shot_path_out = os.path.join(video.dataset.converted_video_folder_path,"shots","video_"+str(video.id),'shot_result_'+str(self.id),'shot_'+str(s.id),)
                try:
                    os.makedirs(shot_path_out)
                except:
                    pass
                start = s.start_frame
                mid = s.start_frame+((s.end_frame-s.start_frame)/2)
                end = s.end_frame
                # print('%s %s %s %s ',s.id,start,mid,end)
                if start > mid or start > end or mid > end:
                    print("errror in frame")

                capture.set(cv.CV_CAP_PROP_POS_FRAMES, start)
                t,img = capture.retrieve()
                img = cv2.resize(img,(125,int(video.video_part.height/(float(video.video_part.width)/125))))
                cv2.imwrite(os.path.join(shot_path_out,'start.png'),img)

                capture.set(cv.CV_CAP_PROP_POS_FRAMES, mid)
                t,img = capture.retrieve()
                img = cv2.resize(img,(125,int(video.video_part.height/(float(video.video_part.width)/125))))
                cv2.imwrite(os.path.join(shot_path_out,'mid.png'),img)

                capture.set(cv.CV_CAP_PROP_POS_FRAMES, end)
                t,img = capture.retrieve()
                img = cv2.resize(img,(125,int(video.video_part.height/(float(video.video_part.width)/125))))
                cv2.imwrite(os.path.join(shot_path_out,'end.png'),img)

            run = False
        print

    # def setAlgos(self,algos):
    #     algo = None
    #     # Configure ECR algo
    #     for x in algos:
    #         print(x['value'])
    #         if(x['value'] == ShotAlgoType.ECR):
    #             algo = ECR()
    #         elif (x['value'] == ShotAlgoType.COLORHISTOGRAM):
    #             algo = ColorHistograms()
    #         algo.shots_detection = self
    #         algo.threshold = x['t']
    #         algo.save()


class VideoShotsResult(models.Model):
    """
    Intermediary model to link a multimedia element to its list of shots.
    """
    video = models.ForeignKey('dataset_manager.Video', related_name='video_shots_results')
    shots_detection = models.ForeignKey(ShotsDetection, related_name='video_shots_results')

    precision = models.FloatField(default=-1.)
    recall = models.FloatField(default=-1.)

    comment = models.CharField(max_length=255)

    date = models.DateTimeField(auto_now_add=True,null=True)

    def _configuration_as_string(self):
        configuration_str = ""
        algos = self.shots_detection.algos

        for algo in algos.all():
            name = algo.name
            weight = algo.weight
            threshold = algo.threshold
            algo_string = name + "(threshold=" + str(threshold) + "; weight=" + str(weight) + ")"

            if configuration_str != "":
                configuration_str += ", "

            configuration_str += algo_string

        return configuration_str

    configuration_as_string = property(_configuration_as_string)



    def compute_shot_cut_density(self):
        """
        For a given list of shots, compute the shot cut density, and return a dictionary containing the shot cut density
        for each frame.

        Returned dictionary looks like:
        {'shot_cut_density': [0.28898, 0.2238, ..., 0.123345]}

        Formula: c(k) = exp(1-n(k))/r)
        where n(k) is the number of frames of shot including the k-th video frame
        and r is a constant determining the way the c(k) values are distributed on the scale between 0 and 1. See
        [Hanjalic 2005, Affective video content representation and modeling. IEEE Trans Multimed 7(1):154-154] for r value.
        """
        r = 300.
        shot_cut_density = list()

        for shot in self.shots.all():
            n_k = shot.end_frame - shot.start_frame
            c_k = exp((1-n_k)/r)
            for i in range(shot.start_frame, shot.end_frame+1):
                shot_cut_density.append([i, c_k])

        # if len(shot_cut_density["shot_cut_density"]) > 1:
        #     # Not sure why, but there is one entry too much, so pop!
        #     shot_cut_density["shot_cut_density"].pop()

        return {FeatureFunctionType.VALUE: shot_cut_density}


class Shot(models.Model):
    """
    Model representing a detected shot.
    """
    video_shots_result = models.ForeignKey(VideoShotsResult, related_name='shots')

    shot_nb = models.PositiveIntegerField()
    start_frame = models.PositiveIntegerField()
    end_frame = models.PositiveIntegerField()

    def _frame_number(self):
        return self.end_frame - self.start_frame
    frame_number = property(_frame_number)

    class Meta:
        ordering = ['shot_nb']


class ShotBoundary(models.Model):
    """
    Model representing a shot boundary.
    """
    video_shots_result = models.ForeignKey(VideoShotsResult, related_name='shot_boundaries')

    frame = models.PositiveIntegerField()
    type = enum.EnumField(ShotBoundaryType, default=ShotBoundaryType.NONE)

    class Meta:
        ordering = ['frame']

#-----------------------------------------------------------------------------------------------------------------------
# Shot detection algorithms
#-----------------------------------------------------------------------------------------------------------------------

class ShotDetectionAlgo(models.Model):
    """
    Parent model representing a shot detection algo.
    """
    shots_detection = models.ForeignKey(ShotsDetection, related_name='algos')

    weight = models.FloatField(default=1.)
    threshold = models.FloatField()

    objects = InheritanceManager()

    type = enum.EnumField(ShotBoundariesDetectionAlgorithmType, default=ShotBoundariesDetectionAlgorithmType.NONE)

    def _name(self):
        return ShotBoundariesDetectionAlgorithmType.labels[self.type]
    name = property(_name)

    @staticmethod
    def get_AlgoList():
        list = []
        for k, v in zip(ShotBoundariesDetectionAlgorithmType.labels.viewvalues(),ShotBoundariesDetectionAlgorithmType.labels.keys()):
            d = {}
            d['key'] = k
            d['value'] = v
            list.append(d)
        return list

class ColorHistograms(ShotDetectionAlgo):
    """
    Shot detection algo based on color histograms comparison.
    """
    # def __init__(self):
    #     self.type = ShotBoundariesDetectionAlgorithmType.COLOR_HISTOGRAM

    def _get_hist_comp(self, img1, img2):
        """
        Compute the comparison of img1 and img2 histograms, using the CV_COMP_CORREL method.
        """
        # Convert imgs to HSV
        img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2HSV)
        img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2HSV)

        # cv2.imshow('img1', img1)
        # cv2.imshow('img2', img2)
        # cv2.waitKey(1)

        # Histogram for 1st image
        hist_a1_hs = cv2.calcHist(img1, [0, 1], None, [30, 32], [0, 180, 0, 256])
        cv2.normalize(hist_a1_hs, hist_a1_hs, 0, 255, cv2.NORM_MINMAX)

        # Histogram for 2nd image
        hist_a2_hs = cv2.calcHist(img2, [0, 1], None, [30, 32], [0, 180, 0, 256])
        cv2.normalize(hist_a2_hs, hist_a2_hs, 0, 255, cv2.NORM_MINMAX)

        # Compare
        result = cv2.compareHist(hist_a1_hs, hist_a2_hs, cv.CV_COMP_CORREL)

        return result


    def is_boundary(self, img1, img2):
        """
        Check if there seems to be a boundary between img1 and img2.
        return True or False, confidence, difference with threshold
        """
        confidence = self._get_hist_comp(img1, img2)
        diff = confidence - self.threshold

        if diff >= 0:
            return False, confidence, diff
        else:
            return True, confidence, diff


class ECR(ShotDetectionAlgo):
    """
    Shot detection algo based on the Edge Change Ratio technique, with a small tweak (see my SIGMAP'12 paper).
    """
    def _get_edge_comp(self, img1, img2):
        """

        """
        # Convert to grey
        _img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        _img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

        # Blur
        _img1 = cv2.blur(_img1, (3,3))
        _img2 = cv2.blur(_img2, (3,3))

        # Canny edge detection with aperture=3 for Sobel
        low_threshold = 75
        sobel_aperture = 3
        _img1 = cv2.Canny(_img1, low_threshold, 3*low_threshold, sobel_aperture)
        _img2 = cv2.Canny(_img2, low_threshold, 3*low_threshold, sobel_aperture)

        # Invert image to white background
        i_img1 = numpy.invert(_img1)
        i_img2 = numpy.invert(_img2)

        # Count nb of edge pixels
        s1 = cv2.countNonZero(_img1)
        s2 = cv2.countNonZero(_img2)

        # Dilate
        element = cv2.getStructuringElement(cv2.MORPH_CROSS,(5,5))
        d_img1 = cv2.dilate(_img1, element)
        d_img2 = cv2.dilate(_img2, element)

        # Creating in/out edges pixels images
        im_in = _img2 & numpy.invert(d_img1)
        im_out = _img1 & numpy.invert(d_img2)

        # Compute in/out ECR
        try:
            ecr_in = cv2.countNonZero(im_in) / float(s2)
        except ZeroDivisionError:
            # Image all black!
            ecr_in = cv2.countNonZero(im_in)

        try:
            ecr_out = cv2.countNonZero(im_out) / float(s1)
        except ZeroDivisionError:
            # Image all black!
            ecr_out = cv2.countNonZero(im_out)

        ecr = max(ecr_in, ecr_out)

        return ecr

    def is_boundary(self, img1, img2):
        """

        return True or False, confidence, difference with threshold
        """
        confidence = self._get_edge_comp(img1, img2)
        diff = self.threshold - confidence

        # cv2.imshow('img1', img1)
        # cv2.imshow('img2', img2)
        # cv2.waitKey(50)

        if diff >= 0:
            return False, confidence, diff
        else:
            # cv2.namedWindow('im_in', cv2.CV_WINDOW_AUTOSIZE)
            # cv2.namedWindow('im_out', cv2.CV_WINDOW_AUTOSIZE)
            # False positive detection with transformation
            # Convert to grey
            _img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            _img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
            transformation = cv2.estimateRigidTransform(_img1, _img2, fullAffine=True)

            # cv2.imshow('im_in', _img1)
            # cv2.imshow('im_out', _img2)

            if transformation is None:
                result = (True, 1, (1 - self.threshold))
            else:
                if abs(transformation[0][2]) > 200 or abs(transformation[1][2]) >= 200:
                    result = (True, confidence, diff)
                else:
                    #False positive
                    result = (False, confidence, diff)

            # if result[0]:
            #     print "SHOT"
            #     cv2.waitKey(5000)

            return result

#-----------------------------------------------------------------------------------------------------------------------
# Divers
#-----------------------------------------------------------------------------------------------------------------------

# def prepare_video_shots(name="test_dataset", base_path="/Users/djo3l/Dev/Datasets/TestDataset"):
#     dataset, created = Dataset.objects.get_or_create(name=name, base_path=base_path)
#
#     # Prepare shot detection
#     shots_detection = ShotsDetection()
#     shots_detection.save()
#
#     # Configure ECR algo
#     ecr_algo = ECR()
#     ecr_algo.shots_detection = shots_detection
#     ecr_algo.threshold = 0.61
#     ecr_algo.save()
#
#
#     for video in dataset.videos.all():
#         # Detect shot boundaries
#         shots_detection.detect(video)
#
#
# def evaluate_video_shots(name="test_dataset", base_path="/Users/djo3l/Dev/Datasets/TestDataset"):
#     dataset, created = Dataset.objects.get_or_create(name=name, base_path=base_path)
#
#     shots_detection = ShotsDetection.objects.all().latest('date')
#
#     for video in dataset.videos.all():
#         # Evaluate the result
#         shots_detection.evaluate(video)
#
#
#
# #-----------------------------------------------------------------------------------------------------------------------
# # Frame extraction models
# #-----------------------------------------------------------------------------------------------------------------------
#
# class VideoFrame(models.Model):
#
#     """
#     Model representing frames of a video
#     """
#     video_part = models.ForeignKey(VideoPart, related_name='frames')
#     index = models.IntegerField() #in seconds
#
#     def _path(self):
#         return os.path.join(self.video_part.video.dataset.frame_path, self.video_part.video.name + "_" + str(self.index) + ".png")
#     path = property(_path)
#
#     def evaluate_brightness_for_image(self):
#         #img = cv2.imread(self.path,1)
#         img = Image.open(self.path)
#         #logger.debug("The image is :" + str(img))
#         brightness = 0
#         # for rgbLine in img:
#         #     for rgb in rgbLine:
#         #         brightness += numpy.sqrt(0.299 * rgb[0] * rgb[0] + 0.587 * rgb[1] * rgb[1] + 0.114 * rgb[2] * rgb[2])
#         imageGreyscale = img.convert('L')
#         stat = ImageStat.Stat(imageGreyscale)
#         brightness = stat.rms[0]
#         return brightness
#
#
# #Saving video frames
# def prepare_video_frames(name="test_dataset", base_path="/Users/djo3l/Dev/Datasets/TestDataset"):
#     """
#     Extraction of one frame per second and saving images into a Frames folder for further use
#     """
#     logger.debug("Computing frames...")
#     dataset = Dataset.objects.get(name=name, base_path=base_path)
#     for video in dataset.videos.all():
#         vidcap = cv2.VideoCapture(video.path)
#         total_nb_of_frames = video.nb_frames
#         logger.debug("FPS: " + str(video.video_part.fps))
#         count = 0
#         success = True
#         while success:
#             success, image = vidcap.read()
#             if(success and ((vidcap.get(cv.CV_CAP_PROP_POS_FRAMES) % video.video_part.fps) == 0)):
#                 video_frame = VideoFrame()
#                 video_frame.video_part = video.video_part
#                 video_frame.index = count
#                 the_image = Image.fromarray(image, 'RGB')
#                 the_image.save(dataset.frame_path + "/" + video.name + "_" + str(count) + ".png")
#                 video_frame.save()
#                 count += 1
#             # Show advance
#             if settings.DEBUG:
#                 percentage = int(vidcap.get(cv.CV_CAP_PROP_POS_FRAMES) * 100. / total_nb_of_frames)
#                 print('Frame extraction: {}/{} - {}%\r'.format(int(vidcap.get(cv.CV_CAP_PROP_POS_FRAMES)), int(total_nb_of_frames), percentage)),
#
#         print
#     logger.info("Computing frames done: " + str(count) + "frames in total for video:" + video.name)

#prepare_video_shots("Shaefer2010", "/Users/djo3l/Dev/Datasets/Shaefer2010")
#prepare_video_shots("Manhob-hci", "/Users/djo3l/Dev/Datasets/manhob-hci")
#evaluate_video_shots()

#prepare_video_shots("test", "/Users/chassotce/Dev/ERS/Datasets/test")
#evaluate_video_shots()
#prepare_video_shots()
#evaluate_video_shots()


#prepare_video_shots("test", "/Users/chassotce/Dev/ERS/Datasets/test")
#prepare_video_frames("test", "/Users/chassotce/Dev/ERS/Datasets/test")
# prepare_video_shots("test", "/home/diana/ers/datasets/test")
# prepare_video_frames("test", "/home/diana/ers/datasets/test")
