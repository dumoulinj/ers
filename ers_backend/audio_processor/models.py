import csv
import logging
import os
from dataset_manager.enums import FeatureType, FeatureFunctionType

logger = logging.getLogger(__name__)

class OpensmileExtractor():
    CONFIG_ENERGY = os.path.join(os.path.dirname(__file__), "configurations/energy.conf")
    CONFIG_EMOTION_FEATURES = os.path.join(os.path.dirname(__file__), "configurations/emotion-features.conf")
    CONFIG_MFCC = os.path.join(os.path.dirname(__file__), "configurations/mfcc.conf")
    CONFIG_PITCH = os.path.join(os.path.dirname(__file__), "configurations/pitch.conf")
    CONFIG_LSP = os.path.join(os.path.dirname(__file__), "configurations/lsp.conf")
    CONFIG_INTENSITY = os.path.join(os.path.dirname(__file__), "configurations/intensity.conf")
    CONFIG_MZCR = os.path.join(os.path.dirname(__file__), "configurations/mzcr.conf")
    CONFIG_SPECTRAL = os.path.join(os.path.dirname(__file__), "configurations/spectral.conf")

    configurations = {
        FeatureType.ENERGY: CONFIG_ENERGY,

        FeatureType.MFCC_1: CONFIG_MFCC,
        FeatureType.MFCC_2: CONFIG_MFCC,
        FeatureType.MFCC_3: CONFIG_MFCC,
        FeatureType.MFCC_4: CONFIG_MFCC,
        FeatureType.MFCC_5: CONFIG_MFCC,
        FeatureType.MFCC_6: CONFIG_MFCC,
        FeatureType.MFCC_7: CONFIG_MFCC,
        FeatureType.MFCC_8: CONFIG_MFCC,
        FeatureType.MFCC_9: CONFIG_MFCC,
        FeatureType.MFCC_10: CONFIG_MFCC,
        FeatureType.MFCC_11: CONFIG_MFCC,
        FeatureType.MFCC_12: CONFIG_MFCC,

        FeatureType.PITCH_VOICE_PROB: CONFIG_PITCH,
        FeatureType.PITCH_F0: CONFIG_PITCH,

        FeatureType.LSP_1: CONFIG_LSP,
        FeatureType.LSP_2: CONFIG_LSP,
        FeatureType.LSP_3: CONFIG_LSP,
        FeatureType.LSP_4: CONFIG_LSP,
        FeatureType.LSP_5: CONFIG_LSP,
        FeatureType.LSP_6: CONFIG_LSP,
        FeatureType.LSP_7: CONFIG_LSP,

        FeatureType.INTENSITY: CONFIG_INTENSITY,
        FeatureType.LOUDNESS: CONFIG_INTENSITY,

        FeatureType.MZCR: CONFIG_MZCR,

        FeatureType.SPECTRAL_1: CONFIG_SPECTRAL,
        FeatureType.SPECTRAL_2: CONFIG_SPECTRAL,
        FeatureType.SPECTRAL_3: CONFIG_SPECTRAL,
        FeatureType.SPECTRAL_4: CONFIG_SPECTRAL,
        FeatureType.SPECTRAL_5: CONFIG_SPECTRAL,

        FeatureType.SPECTRAL_ROLLOFF_1: CONFIG_SPECTRAL,
        FeatureType.SPECTRAL_ROLLOFF_2: CONFIG_SPECTRAL,
        FeatureType.SPECTRAL_ROLLOFF_3: CONFIG_SPECTRAL,
        FeatureType.SPECTRAL_ROLLOFF_4: CONFIG_SPECTRAL,

        FeatureType.SPECTRAL_FLUX: CONFIG_SPECTRAL,
        FeatureType.SPECTRAL_CENTROID: CONFIG_SPECTRAL,
        FeatureType.SPECTRAL_MAX_POS: CONFIG_SPECTRAL,
        FeatureType.SPECTRAL_MIN_POS: CONFIG_SPECTRAL
    }

    def _extract(self, config, params=""):
        """
        Opensmile extraction by calling the command-line extraction command.
        """
        logger.info("OpenSmile extraction with config: %s", config)

        smile_cmd = os.popen("which SMILExtract").read().replace('\n', '')
        cmd = '{} -C "{}" {}'.format(smile_cmd, config, params)
        os.system(cmd)

    # def compute_energy(self, video):
    #     """
    #     Energy extraction for a given video. Returns a list containing the energy rms for each frame.
    #
    #     :param video:
    #     :return:
    #     """
    #
    #     logger.info("Computing sound energy")
    #
    #     audio_path = video.audio_path
    #     output_file = os.path.join(video.dataset.audio_folder_path, "{}.energy.csv".format(video.name))
    #
    #     # Get video frame-rate, and compute framesize (in seconds)
    #     fps = video.video_part.fps
    #     framesize = 1 / fps
    #
    #     # Prepare params (input file, output file, framesize)
    #     params = '-I "{}" -O "{}" -F {}'.format(audio_path, output_file, framesize)
    #
    #     # Do extraction
    #     self._extract(self.CONFIG_ENERGY, params)
    #
    #     energy = list()
    #
    #     # Read the csv and add them to the multimedia element
    #     with open(output_file, 'rb') as csvfile:
    #         csv_reader = csv.DictReader(csvfile, delimiter=';')
    #         for i, row in enumerate(csv_reader):
    #             energy.append([i, float(row['pcm_RMSenergy'])])
    #
    #     # Cleanup
    #     os.remove(output_file)
    #
    #     return energy

    def compute(self, features):
        video = features.multimedia_part.video
        audio_path = video.audio_path
        output_file = os.path.join(video.dataset.audio_path, "{}.output.csv".format(video.name))

        # Get video frame-rate, and compute framesize (in seconds)
        fps = video.video_part.fps
        framesize = 1 / fps

        # Do first time only with mean for each frames, used for arousal
        # Prepare params (input file, output file, framesize)
        params = '-I "{}" -O "{}" -F {}'.format(audio_path, output_file, framesize)

        # Do extraction
        self._extract(self.configurations[features.type], params)

        result = dict()

        function = FeatureFunctionType.VALUE

        # Read the csv and add them to the multimedia element
        crt_nb_frame = 0
        with open(output_file, 'rb') as csvfile:
            csv_reader = csv.DictReader(csvfile, delimiter=';')
            for i, row in enumerate(csv_reader):
                crt_nb_frame += 1

                if not result.has_key(function):
                    result[function] = list()

                function_field = FeatureFunctionType.fields[function]
                if FeatureType.fields.has_key(features.type):
                    field = FeatureType.fields[features.type] + "_" + function_field
                else:
                    field = function_field

                result[function].append([i, float(row[field])])

        os.remove(output_file)

        # Add 0 values to the end as OpenSmile does not process the last second!
        for i in range(crt_nb_frame, video.nb_frames):
            result[function].append([i, 0.])


        # Prepare params (input file, output file, framesize)
        params = '-I "{}" -O "{}" -F {}'.format(audio_path, output_file, framesize)

        # Do extraction
        self._extract(self.configurations[features.type] + '.1s', params)


        # Read the csv and add them to the multimedia element
        crt_nb_frame = 0
        with open(output_file, 'rb') as csvfile:
            csv_reader = csv.DictReader(csvfile, delimiter=';')
            for i, row in enumerate(csv_reader):
                crt_nb_frame += 1
                frame_idx = int(i*fps)
                for function in FeatureType.functions[features.type]:
                    if not result.has_key(function):
                        result[function] = list()

                    function_field = FeatureFunctionType.fields[function]
                    if FeatureType.fields.has_key(features.type):
                        field = FeatureType.fields[features.type] + "_" + function_field
                    else:
                        field = function_field

                    result[function].append([frame_idx, float(row[field])])

        # Cleanup
        os.remove(output_file)

        return result

    # def compute_mfcc_with_functionals(self, video):
    #     """
    #     MFCC features extraction for a given video. Returns a dictionary containing the list of mfcc[1-12] functionals
    #
    #     Returned dictionary looks like:
    #     {   "frameTime": 0.0,
    #         "mfcc_sma[7]_skewness": 0.1635602,
    #         "mfcc_sma[8]_amean": -3.041601,
    #         "mfcc_sma[5]_range": 5.615002, ...
    #     """
    #     logger.info("Computing mfcc")
    #
    #     audio_path = video.audio_path
    #     output_file = os.path.join(video.dataset.audio_folder_path, "{}.mfcc.csv".format(video.name))
    #
    #     # Get video frame-rate, and compute framesize (in seconds)
    #     fps = video.video_part.fps
    #     framesize = 1 / fps
    #
    #     # Prepare params (input file, output file, framesize)
    #     params = '-I "{}" -O "{}" -F {}'.format(audio_path, output_file, framesize)
    #
    #     # Do extraction
    #     self._extract(self.CONFIG_MFCC, params)
    #
    #
    #     mfcc = list()
    #
    #     # Read the csv and add them to the multimedia element
    #     with open(output_file, 'rb') as csvfile:
    #         csv_reader = csv.DictReader(csvfile, delimiter=';')
    #         for i, row in enumerate(csv_reader):
    #             frameFeatures = {}
    #             frameFeatures['frameTime'] = float(row['frameTime'])
    #             for j in range(1,13) :
    #                 frameFeatures['mfcc_sma['+str(j)+']_max'] = float(row['mfcc_sma['+str(j)+']_max'])
    #                 frameFeatures['mfcc_sma['+str(j)+']_min'] = float(row['mfcc_sma['+str(j)+']_min'])
    #                 frameFeatures['mfcc_sma['+str(j)+']_range'] = float(row['mfcc_sma['+str(j)+']_range'])
    #                 frameFeatures['mfcc_sma['+str(j)+']_maxPos'] = float(row['mfcc_sma['+str(j)+']_maxPos'])
    #                 frameFeatures['mfcc_sma['+str(j)+']_minPos'] = float(row['mfcc_sma['+str(j)+']_minPos'])
    #                 frameFeatures['mfcc_sma['+str(j)+']_amean'] = float(row['mfcc_sma['+str(j)+']_amean'])
    #                 frameFeatures['mfcc_sma['+str(j)+']_linregc1'] = float(row['mfcc_sma['+str(j)+']_linregc1'])
    #                 frameFeatures['mfcc_sma['+str(j)+']_linregc2'] = float(row['mfcc_sma['+str(j)+']_linregc2'])
    #                 frameFeatures['mfcc_sma['+str(j)+']_linregerrQ'] = float(row['mfcc_sma['+str(j)+']_linregerrQ'])
    #                 frameFeatures['mfcc_sma['+str(j)+']_skewness'] = float(row['mfcc_sma['+str(j)+']_skewness'])
    #                 frameFeatures['mfcc_sma['+str(j)+']_kurtosis'] = float(row['mfcc_sma['+str(j)+']_kurtosis'])
    #                 frameFeatures['mfcc_sma_de['+str(j)+']_max'] = float(row['mfcc_sma_de['+str(j)+']_max'])
    #                 frameFeatures['mfcc_sma_de['+str(j)+']_min'] = float(row['mfcc_sma_de['+str(j)+']_min'])
    #                 frameFeatures['mfcc_sma_de['+str(j)+']_range'] = float(row['mfcc_sma_de['+str(j)+']_range'])
    #                 frameFeatures['mfcc_sma_de['+str(j)+']_maxPos'] = float(row['mfcc_sma_de['+str(j)+']_maxPos'])
    #                 frameFeatures['mfcc_sma_de['+str(j)+']_minPos'] = float(row['mfcc_sma_de['+str(j)+']_minPos'])
    #                 frameFeatures['mfcc_sma_de['+str(j)+']_amean'] = float(row['mfcc_sma_de['+str(j)+']_amean'])
    #                 frameFeatures['mfcc_sma_de['+str(j)+']_linregc1'] = float(row['mfcc_sma_de['+str(j)+']_linregc1'])
    #                 frameFeatures['mfcc_sma_de['+str(j)+']_linregc2'] = float(row['mfcc_sma_de['+str(j)+']_linregc2'])
    #                 frameFeatures['mfcc_sma_de['+str(j)+']_linregerrQ'] = float(row['mfcc_sma_de['+str(j)+']_linregerrQ'])
    #                 frameFeatures['mfcc_sma_de['+str(j)+']_skewness'] = float(row['mfcc_sma_de['+str(j)+']_skewness'])
    #                 frameFeatures['mfcc_sma_de['+str(j)+']_kurtosis'] = float(row['mfcc_sma_de['+str(j)+']_kurtosis'])
    #             mfcc.append(frameFeatures)
    #     # Cleanup
    #     os.remove(output_file)
    #
    #     return mfcc
    #
    # def compute_mfcc_with_functionals_on_relevant_parts(self, video):
    #     """
    #     MFCC features extraction for a given video. Returns a dictionary containing the list of mfcc[1-12] functionals
    #
    #     Returned dictionary looks like:
    #     {   "frameTime": 0.0,
    #         "mfcc_sma[7]_skewness": 0.1635602,
    #         "mfcc_sma[8]_amean": -3.041601,
    #         "mfcc_sma[5]_range": 5.615002, ...
    #     """
    #     logger.info("Computing mfcc")
    #
    #     audio_path = video.audio_path
    #     output_file = os.path.join(video.dataset.audio_folder_path, "{}.mfcc.csv".format(video.name))
    #
    #     # Get video frame-rate, and compute framesize (in seconds)
    #     fps = video.video_part.fps
    #     framesize = 1 / fps
    #
    #
    #     mfcc = list()
    #
    #     for partition in video.arousal.arousal_partitions:
    #
    #         # Prepare params (input file, output file, framesize)
    #         start_second = partition[0][0] / fps
    #         end_second = partition[1][0] /fps
    #         output_file = os.path.join(video.dataset.audio_folder_path, "{}.mfcc.csv".format(video.name))
    #         params = '-I "{}" -O "{}" -F {} -S {} -E {}'.format(audio_path, output_file, framesize, start_second, end_second)
    #
    #         # Do extraction
    #         self._extract(self.CONFIG_MFCC, params)
    #
    #         # Read the csv and add them to the multimedia element
    #         with open(output_file, 'rb') as csvfile:
    #             csv_reader = csv.DictReader(csvfile, delimiter=';')
    #             for i, row in enumerate(csv_reader):
    #                 frameFeatures = {}
    #                 frameFeatures['frameTime'] = float(row['frameTime']) + int(start_second)
    #                 for j in range(1,13) :
    #                     frameFeatures['mfcc_sma['+str(j)+']_max'] = float(row['mfcc_sma['+str(j)+']_max'])
    #                     frameFeatures['mfcc_sma['+str(j)+']_min'] = float(row['mfcc_sma['+str(j)+']_min'])
    #                     frameFeatures['mfcc_sma['+str(j)+']_range'] = float(row['mfcc_sma['+str(j)+']_range'])
    #                     frameFeatures['mfcc_sma['+str(j)+']_maxPos'] = float(row['mfcc_sma['+str(j)+']_maxPos'])
    #                     frameFeatures['mfcc_sma['+str(j)+']_minPos'] = float(row['mfcc_sma['+str(j)+']_minPos'])
    #                     frameFeatures['mfcc_sma['+str(j)+']_amean'] = float(row['mfcc_sma['+str(j)+']_amean'])
    #                     frameFeatures['mfcc_sma['+str(j)+']_linregc1'] = float(row['mfcc_sma['+str(j)+']_linregc1'])
    #                     frameFeatures['mfcc_sma['+str(j)+']_linregc2'] = float(row['mfcc_sma['+str(j)+']_linregc2'])
    #                     frameFeatures['mfcc_sma['+str(j)+']_linregerrQ'] = float(row['mfcc_sma['+str(j)+']_linregerrQ'])
    #                     frameFeatures['mfcc_sma['+str(j)+']_skewness'] = float(row['mfcc_sma['+str(j)+']_skewness'])
    #                     frameFeatures['mfcc_sma['+str(j)+']_kurtosis'] = float(row['mfcc_sma['+str(j)+']_kurtosis'])
    #                     frameFeatures['mfcc_sma_de['+str(j)+']_max'] = float(row['mfcc_sma_de['+str(j)+']_max'])
    #                     frameFeatures['mfcc_sma_de['+str(j)+']_min'] = float(row['mfcc_sma_de['+str(j)+']_min'])
    #                     frameFeatures['mfcc_sma_de['+str(j)+']_range'] = float(row['mfcc_sma_de['+str(j)+']_range'])
    #                     frameFeatures['mfcc_sma_de['+str(j)+']_maxPos'] = float(row['mfcc_sma_de['+str(j)+']_maxPos'])
    #                     frameFeatures['mfcc_sma_de['+str(j)+']_minPos'] = float(row['mfcc_sma_de['+str(j)+']_minPos'])
    #                     frameFeatures['mfcc_sma_de['+str(j)+']_amean'] = float(row['mfcc_sma_de['+str(j)+']_amean'])
    #                     frameFeatures['mfcc_sma_de['+str(j)+']_linregc1'] = float(row['mfcc_sma_de['+str(j)+']_linregc1'])
    #                     frameFeatures['mfcc_sma_de['+str(j)+']_linregc2'] = float(row['mfcc_sma_de['+str(j)+']_linregc2'])
    #                     frameFeatures['mfcc_sma_de['+str(j)+']_linregerrQ'] = float(row['mfcc_sma_de['+str(j)+']_linregerrQ'])
    #                     frameFeatures['mfcc_sma_de['+str(j)+']_skewness'] = float(row['mfcc_sma_de['+str(j)+']_skewness'])
    #                     frameFeatures['mfcc_sma_de['+str(j)+']_kurtosis'] = float(row['mfcc_sma_de['+str(j)+']_kurtosis'])
    #                 mfcc.append(frameFeatures)
    #         # Cleanup
    #     os.remove(output_file)
    #
    #     return mfcc
    #
    #
    # def compute_pitch_with_functionals(self, video):
    #     """
    #     Pitch feature extraction for a given video. Returns a dictionary containing the list of pitch functionals
    #
    #     Returned dictionary looks like:
    #     {   "frameTime": 0.0,
    #         ""F0_sma_amean": 0.0,
    #         "F0_sma_minPos": 0.0,
    #         "F0_sma_linregc2": 0.0,  ...
    #     """
    #     logger.info("Computing pitch")
    #
    #     audio_path = video.audio_path
    #     output_file = os.path.join(video.dataset.audio_folder_path, "{}.pitch.csv".format(video.name))
    #
    #     # Get video frame-rate, and compute framesize (in seconds)
    #     fps = video.video_part.fps
    #     framesize = 1 / fps
    #
    #     # Prepare params (input file, output file, framesize)
    #     params = '-I "{}" -O "{}" -F {}'.format(audio_path, output_file, framesize)
    #
    #     # Do extraction
    #     self._extract(self.CONFIG_PITCH, params)
    #
    #
    #     pitch = list()
    #
    #     #Read the csv and add them to the multimedia element
    #     with open(output_file, 'rb') as csvfile:
    #         csv_reader = csv.DictReader(csvfile, delimiter=';')
    #         for i, row in enumerate(csv_reader):
    #             frameFeatures = {}
    #             frameFeatures['frameTime'] = float(row['frameTime'])
    #             frameFeatures['voiceProb_sma_max'] = float(row['voiceProb_sma_max'])
    #             frameFeatures['voiceProb_sma_min'] = float(row['voiceProb_sma_min'])
    #             frameFeatures['voiceProb_sma_range'] = float(row['voiceProb_sma_range'])
    #             frameFeatures['voiceProb_sma_maxPos'] = float(row['voiceProb_sma_maxPos'])
    #             frameFeatures['voiceProb_sma_minPos'] = float(row['voiceProb_sma_minPos'])
    #             frameFeatures['voiceProb_sma_amean'] = float(row['voiceProb_sma_amean'])
    #             frameFeatures['voiceProb_sma_linregc1'] = float(row['voiceProb_sma_linregc1'])
    #             frameFeatures['voiceProb_sma_linregc2'] = float(row['voiceProb_sma_linregc2'])
    #             frameFeatures['voiceProb_sma_linregerrQ'] = float(row['voiceProb_sma_linregerrQ'])
    #             frameFeatures['voiceProb_sma_stddev'] = float(row['voiceProb_sma_stddev'])
    #             frameFeatures['voiceProb_sma_skewness'] = float(row['voiceProb_sma_skewness'])
    #             frameFeatures['voiceProb_sma_kurtosis'] = float(row['voiceProb_sma_kurtosis'])
    #             frameFeatures['voiceProb_sma_de_max'] = float(row['voiceProb_sma_de_max'])
    #             frameFeatures['voiceProb_sma_de_min'] = float(row['voiceProb_sma_de_min'])
    #             frameFeatures['voiceProb_sma_de_range'] = float(row['voiceProb_sma_de_range'])
    #             frameFeatures['voiceProb_sma_de_maxPos'] = float(row['voiceProb_sma_de_maxPos'])
    #             frameFeatures['voiceProb_sma_de_minPos'] = float(row['voiceProb_sma_de_minPos'])
    #             frameFeatures['voiceProb_sma_de_amean'] = float(row['voiceProb_sma_de_amean'])
    #             frameFeatures['voiceProb_sma_de_linregc1'] = float(row['voiceProb_sma_de_linregc1'])
    #             frameFeatures['voiceProb_sma_de_linregc2'] = float(row['voiceProb_sma_de_linregc2'])
    #             frameFeatures['voiceProb_sma_de_linregerrQ'] = float(row['voiceProb_sma_de_linregerrQ'])
    #             frameFeatures['voiceProb_sma_de_stddev'] = float(row['voiceProb_sma_de_stddev'])
    #             frameFeatures['voiceProb_sma_de_skewness'] = float(row['voiceProb_sma_de_skewness'])
    #             frameFeatures['voiceProb_sma_de_kurtosis'] = float(row['voiceProb_sma_de_kurtosis'])
    #
    #             frameFeatures['F0_sma_max'] = float(row['F0_sma_max'])
    #             frameFeatures['F0_sma_min'] = float(row['F0_sma_min'])
    #             frameFeatures['F0_sma_range'] = float(row['F0_sma_range'])
    #             frameFeatures['F0_sma_maxPos'] = float(row['F0_sma_maxPos'])
    #             frameFeatures['F0_sma_minPos'] = float(row['F0_sma_minPos'])
    #             frameFeatures['F0_sma_amean'] = float(row['F0_sma_amean'])
    #             frameFeatures['F0_sma_linregc1'] = float(row['F0_sma_linregc1'])
    #             frameFeatures['F0_sma_linregc2'] = float(row['F0_sma_linregc2'])
    #             frameFeatures['F0_sma_linregerrQ'] = float(row['F0_sma_linregerrQ'])
    #             frameFeatures['F0_sma_stddev'] = float(row['F0_sma_stddev'])
    #             frameFeatures['F0_sma_skewness'] = float(row['F0_sma_skewness'])
    #             frameFeatures['F0_sma_kurtosis'] = float(row['F0_sma_kurtosis'])
    #             frameFeatures['F0_sma_de_max'] = float(row['F0_sma_de_max'])
    #             frameFeatures['F0_sma_de_min'] = float(row['F0_sma_de_min'])
    #             frameFeatures['F0_sma_de_range'] = float(row['F0_sma_de_range'])
    #             frameFeatures['F0_sma_de_maxPos'] = float(row['F0_sma_de_maxPos'])
    #             frameFeatures['F0_sma_de_minPos'] = float(row['F0_sma_de_minPos'])
    #             frameFeatures['F0_sma_de_amean'] = float(row['F0_sma_de_amean'])
    #             frameFeatures['F0_sma_de_linregc1'] = float(row['F0_sma_de_linregc1'])
    #             frameFeatures['F0_sma_de_linregc2'] = float(row['F0_sma_de_linregc2'])
    #             frameFeatures['F0_sma_de_linregerrQ'] = float(row['F0_sma_de_linregerrQ'])
    #             frameFeatures['F0_sma_de_stddev'] = float(row['F0_sma_de_stddev'])
    #             frameFeatures['F0_sma_de_skewness'] = float(row['F0_sma_de_skewness'])
    #             frameFeatures['F0_sma_de_kurtosis'] = float(row['F0_sma_de_kurtosis'])
    #             pitch.append(frameFeatures)
    #     #Cleanup
    #     os.remove(output_file)
    #
    #     return pitch
    #
    # def compute_pitch_with_functionals_on_relevant_parts(self, video):
    #     """
    #     Pitch feature extraction for a given video. Returns a dictionary containing the list of pitch functionals
    #
    #     Returned dictionary looks like:
    #     {   "frameTime": 0.0,
    #         ""F0_sma_amean": 0.0,
    #         "F0_sma_minPos": 0.0,
    #         "F0_sma_linregc2": 0.0,  ...
    #     """
    #     logger.info("Computing pitch")
    #
    #     audio_path = video.audio_path
    #     output_file = os.path.join(video.dataset.audio_folder_path, "{}.pitch.csv".format(video.name))
    #
    #     # Get video frame-rate, and compute framesize (in seconds)
    #     fps = video.video_part.fps
    #     framesize = 1 / fps
    #
    #     # Prepare params (input file, output file, framesize)
    #     for partition in video.arousal.arousal_partitions:
    #
    #         # Prepare params (input file, output file, framesize)
    #         start_second = partition[0][0] / fps
    #         end_second = partition[1][0] /fps
    #         output_file = os.path.join(video.dataset.audio_folder_path, "{}.mfcc.csv".format(video.name))
    #         params = '-I "{}" -O "{}" -F {} -S {} -E {}'.format(audio_path, output_file, framesize, start_second, end_second)
    #
    #         # Do extraction
    #         self._extract(self.CONFIG_PITCH, params)
    #
    #
    #         pitch = list()
    #
    #         #Read the csv and add them to the multimedia element
    #         with open(output_file, 'rb') as csvfile:
    #             csv_reader = csv.DictReader(csvfile, delimiter=';')
    #             for i, row in enumerate(csv_reader):
    #                 frameFeatures = {}
    #                 frameFeatures['frameTime'] = float(row['frameTime']) + int(start_second)
    #                 frameFeatures['voiceProb_sma_max'] = float(row['voiceProb_sma_max'])
    #                 frameFeatures['voiceProb_sma_min'] = float(row['voiceProb_sma_min'])
    #                 frameFeatures['voiceProb_sma_range'] = float(row['voiceProb_sma_range'])
    #                 frameFeatures['voiceProb_sma_maxPos'] = float(row['voiceProb_sma_maxPos'])
    #                 frameFeatures['voiceProb_sma_minPos'] = float(row['voiceProb_sma_minPos'])
    #                 frameFeatures['voiceProb_sma_amean'] = float(row['voiceProb_sma_amean'])
    #                 frameFeatures['voiceProb_sma_linregc1'] = float(row['voiceProb_sma_linregc1'])
    #                 frameFeatures['voiceProb_sma_linregc2'] = float(row['voiceProb_sma_linregc2'])
    #                 frameFeatures['voiceProb_sma_linregerrQ'] = float(row['voiceProb_sma_linregerrQ'])
    #                 frameFeatures['voiceProb_sma_stddev'] = float(row['voiceProb_sma_stddev'])
    #                 frameFeatures['voiceProb_sma_skewness'] = float(row['voiceProb_sma_skewness'])
    #                 frameFeatures['voiceProb_sma_kurtosis'] = float(row['voiceProb_sma_kurtosis'])
    #                 frameFeatures['voiceProb_sma_de_max'] = float(row['voiceProb_sma_de_max'])
    #                 frameFeatures['voiceProb_sma_de_min'] = float(row['voiceProb_sma_de_min'])
    #                 frameFeatures['voiceProb_sma_de_range'] = float(row['voiceProb_sma_de_range'])
    #                 frameFeatures['voiceProb_sma_de_maxPos'] = float(row['voiceProb_sma_de_maxPos'])
    #                 frameFeatures['voiceProb_sma_de_minPos'] = float(row['voiceProb_sma_de_minPos'])
    #                 frameFeatures['voiceProb_sma_de_amean'] = float(row['voiceProb_sma_de_amean'])
    #                 frameFeatures['voiceProb_sma_de_linregc1'] = float(row['voiceProb_sma_de_linregc1'])
    #                 frameFeatures['voiceProb_sma_de_linregc2'] = float(row['voiceProb_sma_de_linregc2'])
    #                 frameFeatures['voiceProb_sma_de_linregerrQ'] = float(row['voiceProb_sma_de_linregerrQ'])
    #                 frameFeatures['voiceProb_sma_de_stddev'] = float(row['voiceProb_sma_de_stddev'])
    #                 frameFeatures['voiceProb_sma_de_skewness'] = float(row['voiceProb_sma_de_skewness'])
    #                 frameFeatures['voiceProb_sma_de_kurtosis'] = float(row['voiceProb_sma_de_kurtosis'])
    #
    #                 frameFeatures['F0_sma_max'] = float(row['F0_sma_max'])
    #                 frameFeatures['F0_sma_min'] = float(row['F0_sma_min'])
    #                 frameFeatures['F0_sma_range'] = float(row['F0_sma_range'])
    #                 frameFeatures['F0_sma_maxPos'] = float(row['F0_sma_maxPos'])
    #                 frameFeatures['F0_sma_minPos'] = float(row['F0_sma_minPos'])
    #                 frameFeatures['F0_sma_amean'] = float(row['F0_sma_amean'])
    #                 frameFeatures['F0_sma_linregc1'] = float(row['F0_sma_linregc1'])
    #                 frameFeatures['F0_sma_linregc2'] = float(row['F0_sma_linregc2'])
    #                 frameFeatures['F0_sma_linregerrQ'] = float(row['F0_sma_linregerrQ'])
    #                 frameFeatures['F0_sma_stddev'] = float(row['F0_sma_stddev'])
    #                 frameFeatures['F0_sma_skewness'] = float(row['F0_sma_skewness'])
    #                 frameFeatures['F0_sma_kurtosis'] = float(row['F0_sma_kurtosis'])
    #                 frameFeatures['F0_sma_de_max'] = float(row['F0_sma_de_max'])
    #                 frameFeatures['F0_sma_de_min'] = float(row['F0_sma_de_min'])
    #                 frameFeatures['F0_sma_de_range'] = float(row['F0_sma_de_range'])
    #                 frameFeatures['F0_sma_de_maxPos'] = float(row['F0_sma_de_maxPos'])
    #                 frameFeatures['F0_sma_de_minPos'] = float(row['F0_sma_de_minPos'])
    #                 frameFeatures['F0_sma_de_amean'] = float(row['F0_sma_de_amean'])
    #                 frameFeatures['F0_sma_de_linregc1'] = float(row['F0_sma_de_linregc1'])
    #                 frameFeatures['F0_sma_de_linregc2'] = float(row['F0_sma_de_linregc2'])
    #                 frameFeatures['F0_sma_de_linregerrQ'] = float(row['F0_sma_de_linregerrQ'])
    #                 frameFeatures['F0_sma_de_stddev'] = float(row['F0_sma_de_stddev'])
    #                 frameFeatures['F0_sma_de_skewness'] = float(row['F0_sma_de_skewness'])
    #                 frameFeatures['F0_sma_de_kurtosis'] = float(row['F0_sma_de_kurtosis'])
    #                 pitch.append(frameFeatures)
    #         #Cleanup
    #     os.remove(output_file)
    #
    #     return pitch
    #
    #
    # def compute_lsp_with_functionals(self, video):
    #     """
    #     Line spectral pair frequencies feature extraction for a given video. Returns a dictionary containing the list of LSP functionals
    #
    #     Returned dictionary looks like:
    #     {   "frameTime": 0.0,
    #          "lspFreq_sma[1]_max": 0.5344351,
    #             "lspFreq_sma_de[1]_skewness": -1.086014,
    #             "lspFreq_sma_de[1]_min": -0.01659869,  ...
    #     """
    #     logger.info("Computing LSP")
    #
    #     audio_path = video.audio_path
    #     output_file = os.path.join(video.dataset.audio_folder_path, "{}.lsp.csv".format(video.name))
    #
    #     # Get video frame-rate, and compute framesize (in seconds)
    #     fps = video.video_part.fps
    #     framesize = 1 / fps
    #
    #     # Prepare params (input file, output file, framesize)
    #     params = '-I "{}" -O "{}" -F {}'.format(audio_path, output_file, framesize)
    #
    #     # Do extraction
    #     self._extract(self.CONFIG_LSP, params)
    #
    #
    #     lsp = list()
    #
    #     #Read the csv and add them to the multimedia element
    #     with open(output_file, 'rb') as csvfile:
    #         csv_reader = csv.DictReader(csvfile, delimiter=';')
    #         for i, row in enumerate(csv_reader):
    #             frameFeatures = {}
    #             frameFeatures['frameTime'] = float(row['frameTime'])
    #             for j in range(1,8) :
    #                 frameFeatures['lspFreq_sma['+str(j)+']_max'] = float(row['lspFreq_sma['+str(j)+']_max'])
    #                 frameFeatures['lspFreq_sma['+str(j)+']_min'] = float(row['lspFreq_sma['+str(j)+']_min'])
    #                 frameFeatures['lspFreq_sma['+str(j)+']_range'] = float(row['lspFreq_sma['+str(j)+']_range'])
    #                 frameFeatures['lspFreq_sma['+str(j)+']_maxPos'] = float(row['lspFreq_sma['+str(j)+']_maxPos'])
    #                 frameFeatures['lspFreq_sma['+str(j)+']_minPos'] = float(row['lspFreq_sma['+str(j)+']_minPos'])
    #                 frameFeatures['lspFreq_sma['+str(j)+']_amean'] = float(row['lspFreq_sma['+str(j)+']_amean'])
    #                 frameFeatures['lspFreq_sma['+str(j)+']_linregc1'] = float(row['lspFreq_sma['+str(j)+']_linregc1'])
    #                 frameFeatures['lspFreq_sma['+str(j)+']_linregc2'] = float(row['lspFreq_sma['+str(j)+']_linregc2'])
    #                 frameFeatures['lspFreq_sma['+str(j)+']_linregerrQ'] = float(row['lspFreq_sma['+str(j)+']_linregerrQ'])
    #                 frameFeatures['lspFreq_sma['+str(j)+']_skewness'] = float(row['lspFreq_sma['+str(j)+']_skewness'])
    #                 frameFeatures['lspFreq_sma['+str(j)+']_kurtosis'] = float(row['lspFreq_sma['+str(j)+']_kurtosis'])
    #                 frameFeatures['lspFreq_sma_de['+str(j)+']_max'] = float(row['lspFreq_sma_de['+str(j)+']_max'])
    #                 frameFeatures['lspFreq_sma_de['+str(j)+']_min'] = float(row['lspFreq_sma_de['+str(j)+']_min'])
    #                 frameFeatures['lspFreq_sma_de['+str(j)+']_range'] = float(row['lspFreq_sma_de['+str(j)+']_range'])
    #                 frameFeatures['lspFreq_sma_de['+str(j)+']_maxPos'] = float(row['lspFreq_sma_de['+str(j)+']_maxPos'])
    #                 frameFeatures['lspFreq_sma_de['+str(j)+']_minPos'] = float(row['lspFreq_sma_de['+str(j)+']_minPos'])
    #                 frameFeatures['lspFreq_sma_de['+str(j)+']_amean'] = float(row['lspFreq_sma_de['+str(j)+']_amean'])
    #                 frameFeatures['lspFreq_sma_de['+str(j)+']_linregc1'] = float(row['lspFreq_sma_de['+str(j)+']_linregc1'])
    #                 frameFeatures['lspFreq_sma_de['+str(j)+']_linregc2'] = float(row['lspFreq_sma_de['+str(j)+']_linregc2'])
    #                 frameFeatures['lspFreq_sma_de['+str(j)+']_linregerrQ'] = float(row['lspFreq_sma_de['+str(j)+']_linregerrQ'])
    #                 frameFeatures['lspFreq_sma_de['+str(j)+']_skewness'] = float(row['lspFreq_sma_de['+str(j)+']_skewness'])
    #                 frameFeatures['lspFreq_sma_de['+str(j)+']_kurtosis'] = float(row['lspFreq_sma_de['+str(j)+']_kurtosis'])
    #
    #             lsp.append(frameFeatures)
    #     #Cleanup
    #     os.remove(output_file)
    #
    #     return lsp
    #
    # def compute_lsp_with_functionals_on_relevant_parts(self, video):
    #     """
    #     Line spectral pair frequencies feature extraction for a given video. Returns a dictionary containing the list of LSP functionals
    #
    #     Returned dictionary looks like:
    #     {   "frameTime": 0.0,
    #          "lspFreq_sma[1]_max": 0.5344351,
    #             "lspFreq_sma_de[1]_skewness": -1.086014,
    #             "lspFreq_sma_de[1]_min": -0.01659869,  ...
    #     """
    #     logger.info("Computing LSP")
    #
    #     audio_path = video.audio_path
    #     output_file = os.path.join(video.dataset.audio_folder_path, "{}.lsp.csv".format(video.name))
    #
    #     # Get video frame-rate, and compute framesize (in seconds)
    #     fps = video.video_part.fps
    #     framesize = 1 / fps
    #
    #     # Prepare params (input file, output file, framesize)
    #     for partition in video.arousal.arousal_partitions:
    #
    #         # Prepare params (input file, output file, framesize)
    #         start_second = partition[0][0] / fps
    #         end_second = partition[1][0] /fps
    #         output_file = os.path.join(video.dataset.audio_folder_path, "{}.mfcc.csv".format(video.name))
    #         params = '-I "{}" -O "{}" -F {} -S {} -E {}'.format(audio_path, output_file, framesize, start_second, end_second)
    #
    #         # Do extraction
    #         self._extract(self.CONFIG_LSP, params)
    #
    #
    #         lsp = list()
    #
    #         #Read the csv and add them to the multimedia element
    #         with open(output_file, 'rb') as csvfile:
    #             csv_reader = csv.DictReader(csvfile, delimiter=';')
    #             for i, row in enumerate(csv_reader):
    #                 frameFeatures = {}
    #                 frameFeatures['frameTime'] = float(row['frameTime']) + int(start_second)
    #                 for j in range(1,8) :
    #                     frameFeatures['lspFreq_sma['+str(j)+']_max'] = float(row['lspFreq_sma['+str(j)+']_max'])
    #                     frameFeatures['lspFreq_sma['+str(j)+']_min'] = float(row['lspFreq_sma['+str(j)+']_min'])
    #                     frameFeatures['lspFreq_sma['+str(j)+']_range'] = float(row['lspFreq_sma['+str(j)+']_range'])
    #                     frameFeatures['lspFreq_sma['+str(j)+']_maxPos'] = float(row['lspFreq_sma['+str(j)+']_maxPos'])
    #                     frameFeatures['lspFreq_sma['+str(j)+']_minPos'] = float(row['lspFreq_sma['+str(j)+']_minPos'])
    #                     frameFeatures['lspFreq_sma['+str(j)+']_amean'] = float(row['lspFreq_sma['+str(j)+']_amean'])
    #                     frameFeatures['lspFreq_sma['+str(j)+']_linregc1'] = float(row['lspFreq_sma['+str(j)+']_linregc1'])
    #                     frameFeatures['lspFreq_sma['+str(j)+']_linregc2'] = float(row['lspFreq_sma['+str(j)+']_linregc2'])
    #                     frameFeatures['lspFreq_sma['+str(j)+']_linregerrQ'] = float(row['lspFreq_sma['+str(j)+']_linregerrQ'])
    #                     frameFeatures['lspFreq_sma['+str(j)+']_skewness'] = float(row['lspFreq_sma['+str(j)+']_skewness'])
    #                     frameFeatures['lspFreq_sma['+str(j)+']_kurtosis'] = float(row['lspFreq_sma['+str(j)+']_kurtosis'])
    #                     frameFeatures['lspFreq_sma_de['+str(j)+']_max'] = float(row['lspFreq_sma_de['+str(j)+']_max'])
    #                     frameFeatures['lspFreq_sma_de['+str(j)+']_min'] = float(row['lspFreq_sma_de['+str(j)+']_min'])
    #                     frameFeatures['lspFreq_sma_de['+str(j)+']_range'] = float(row['lspFreq_sma_de['+str(j)+']_range'])
    #                     frameFeatures['lspFreq_sma_de['+str(j)+']_maxPos'] = float(row['lspFreq_sma_de['+str(j)+']_maxPos'])
    #                     frameFeatures['lspFreq_sma_de['+str(j)+']_minPos'] = float(row['lspFreq_sma_de['+str(j)+']_minPos'])
    #                     frameFeatures['lspFreq_sma_de['+str(j)+']_amean'] = float(row['lspFreq_sma_de['+str(j)+']_amean'])
    #                     frameFeatures['lspFreq_sma_de['+str(j)+']_linregc1'] = float(row['lspFreq_sma_de['+str(j)+']_linregc1'])
    #                     frameFeatures['lspFreq_sma_de['+str(j)+']_linregc2'] = float(row['lspFreq_sma_de['+str(j)+']_linregc2'])
    #                     frameFeatures['lspFreq_sma_de['+str(j)+']_linregerrQ'] = float(row['lspFreq_sma_de['+str(j)+']_linregerrQ'])
    #                     frameFeatures['lspFreq_sma_de['+str(j)+']_skewness'] = float(row['lspFreq_sma_de['+str(j)+']_skewness'])
    #                     frameFeatures['lspFreq_sma_de['+str(j)+']_kurtosis'] = float(row['lspFreq_sma_de['+str(j)+']_kurtosis'])
    #
    #                 lsp.append(frameFeatures)
    #     #Cleanup
    #     os.remove(output_file)
    #
    #     return lsp
    #
    #
    # def compute_intensity_with_functionals(self, video):
    #     """
    #     Intensity and loudness feature extraction for a given video. Returns a dictionary containing the list of intensity functionals
    #
    #     Returned dictionary looks like:
    #     {   "frameTime": 0.0,
    #         pcm_loudness_sma_de_minPos": 9.0,
    #             "pcm_loudness_sma_de_min": -0.004015894,
    #             "pcm_loudness_sma_stddev": 0.006899435,   ...
    #     """
    #     logger.info("Computing pitch")
    #
    #     audio_path = video.audio_path
    #     output_file = os.path.join(video.dataset.audio_folder_path, "{}.intesity.csv".format(video.name))
    #
    #     # Get video frame-rate, and compute framesize (in seconds)
    #     fps = video.video_part.fps
    #     framesize = 1 / fps
    #
    #     # Prepare params (input file, output file, framesize)
    #     params = '-I "{}" -O "{}" -F {}'.format(audio_path, output_file, framesize)
    #
    #     # Do extraction
    #     self._extract(self.CONFIG_INTENSITY, params)
    #
    #
    #     intensity = list()
    #
    #     #Read the csv and add them to the multimedia element
    #     with open(output_file, 'rb') as csvfile:
    #         csv_reader = csv.DictReader(csvfile, delimiter=';')
    #         for i, row in enumerate(csv_reader):
    #             frameFeatures = {}
    #             frameFeatures['frameTime'] = float(row['frameTime'])
    #             frameFeatures['pcm_intensity_sma_max'] = float(row['pcm_intensity_sma_max'])
    #             frameFeatures['pcm_intensity_sma_min'] = float(row['pcm_intensity_sma_min'])
    #             frameFeatures['pcm_intensity_sma_range'] = float(row['pcm_intensity_sma_range'])
    #             frameFeatures['pcm_intensity_sma_maxPos'] = float(row['pcm_intensity_sma_maxPos'])
    #             frameFeatures['pcm_intensity_sma_minPos'] = float(row['pcm_intensity_sma_minPos'])
    #             frameFeatures['pcm_intensity_sma_amean'] = float(row['pcm_intensity_sma_amean'])
    #             frameFeatures['pcm_intensity_sma_linregc1'] = float(row['pcm_intensity_sma_linregc1'])
    #             frameFeatures['pcm_intensity_sma_linregc2'] = float(row['pcm_intensity_sma_linregc2'])
    #             frameFeatures['pcm_intensity_sma_linregerrQ'] = float(row['pcm_intensity_sma_linregerrQ'])
    #             frameFeatures['pcm_intensity_sma_stddev'] = float(row['pcm_intensity_sma_stddev'])
    #             frameFeatures['pcm_intensity_sma_skewness'] = float(row['pcm_intensity_sma_skewness'])
    #             frameFeatures['pcm_intensity_sma_kurtosis'] = float(row['pcm_intensity_sma_kurtosis'])
    #             frameFeatures['pcm_intensity_sma_de_max'] = float(row['pcm_intensity_sma_de_max'])
    #             frameFeatures['pcm_intensity_sma_de_min'] = float(row['pcm_intensity_sma_de_min'])
    #             frameFeatures['pcm_intensity_sma_de_range'] = float(row['pcm_intensity_sma_de_range'])
    #             frameFeatures['pcm_intensity_sma_de_maxPos'] = float(row['pcm_intensity_sma_de_maxPos'])
    #             frameFeatures['pcm_intensity_sma_de_minPos'] = float(row['pcm_intensity_sma_de_minPos'])
    #             frameFeatures['pcm_intensity_sma_de_amean'] = float(row['pcm_intensity_sma_de_amean'])
    #             frameFeatures['pcm_intensity_sma_de_linregc1'] = float(row['pcm_intensity_sma_de_linregc1'])
    #             frameFeatures['pcm_intensity_sma_de_linregc2'] = float(row['pcm_intensity_sma_de_linregc2'])
    #             frameFeatures['pcm_intensity_sma_de_linregerrQ'] = float(row['pcm_intensity_sma_de_linregerrQ'])
    #             frameFeatures['pcm_intensity_sma_de_stddev'] = float(row['pcm_intensity_sma_de_stddev'])
    #             frameFeatures['pcm_intensity_sma_de_skewness'] = float(row['pcm_intensity_sma_de_skewness'])
    #             frameFeatures['pcm_intensity_sma_de_kurtosis'] = float(row['pcm_intensity_sma_de_kurtosis'])
    #
    #             frameFeatures['pcm_loudness_sma_max'] = float(row['pcm_loudness_sma_max'])
    #             frameFeatures['pcm_loudness_sma_min'] = float(row['pcm_loudness_sma_min'])
    #             frameFeatures['pcm_loudness_sma_range'] = float(row['pcm_loudness_sma_range'])
    #             frameFeatures['pcm_loudness_sma_maxPos'] = float(row['pcm_loudness_sma_maxPos'])
    #             frameFeatures['pcm_loudness_sma_minPos'] = float(row['pcm_loudness_sma_minPos'])
    #             frameFeatures['pcm_loudness_sma_amean'] = float(row['pcm_loudness_sma_amean'])
    #             frameFeatures['pcm_loudness_sma_linregc1'] = float(row['pcm_loudness_sma_linregc1'])
    #             frameFeatures['pcm_loudness_sma_linregc2'] = float(row['pcm_loudness_sma_linregc2'])
    #             frameFeatures['pcm_loudness_sma_linregerrQ'] = float(row['pcm_loudness_sma_linregerrQ'])
    #             frameFeatures['pcm_loudness_sma_stddev'] = float(row['pcm_loudness_sma_stddev'])
    #             frameFeatures['pcm_loudness_sma_skewness'] = float(row['pcm_loudness_sma_skewness'])
    #             frameFeatures['pcm_loudness_sma_kurtosis'] = float(row['pcm_loudness_sma_kurtosis'])
    #             frameFeatures['pcm_loudness_sma_de_max'] = float(row['pcm_loudness_sma_de_max'])
    #             frameFeatures['pcm_loudness_sma_de_min'] = float(row['pcm_loudness_sma_de_min'])
    #             frameFeatures['pcm_loudness_sma_de_range'] = float(row['pcm_loudness_sma_de_range'])
    #             frameFeatures['pcm_loudness_sma_de_maxPos'] = float(row['pcm_loudness_sma_de_maxPos'])
    #             frameFeatures['pcm_loudness_sma_de_minPos'] = float(row['pcm_loudness_sma_de_minPos'])
    #             frameFeatures['pcm_loudness_sma_de_amean'] = float(row['pcm_loudness_sma_de_amean'])
    #             frameFeatures['pcm_loudness_sma_de_linregc1'] = float(row['pcm_loudness_sma_de_linregc1'])
    #             frameFeatures['pcm_loudness_sma_de_linregc2'] = float(row['pcm_loudness_sma_de_linregc2'])
    #             frameFeatures['pcm_loudness_sma_de_linregerrQ'] = float(row['pcm_loudness_sma_de_linregerrQ'])
    #             frameFeatures['pcm_loudness_sma_de_stddev'] = float(row['pcm_loudness_sma_de_stddev'])
    #             frameFeatures['pcm_loudness_sma_de_skewness'] = float(row['pcm_loudness_sma_de_skewness'])
    #             frameFeatures['pcm_loudness_sma_de_kurtosis'] = float(row['pcm_loudness_sma_de_kurtosis'])
    #
    #             intensity.append(frameFeatures)
    #     #Cleanup
    #     os.remove(output_file)
    #
    #     return intensity
    #
    # def compute_intensity_with_functionals_on_relevant_parts(self, video):
    #     """
    #     Intensity and loudness feature extraction for a given video. Returns a dictionary containing the list of intensity functionals
    #
    #     Returned dictionary looks like:
    #     {   "frameTime": 0.0,
    #         pcm_loudness_sma_de_minPos": 9.0,
    #             "pcm_loudness_sma_de_min": -0.004015894,
    #             "pcm_loudness_sma_stddev": 0.006899435,   ...
    #     """
    #     logger.info("Computing pitch")
    #
    #     audio_path = video.audio_path
    #     output_file = os.path.join(video.dataset.audio_folder_path, "{}.intesity.csv".format(video.name))
    #
    #     # Get video frame-rate, and compute framesize (in seconds)
    #     fps = video.video_part.fps
    #     framesize = 1 / fps
    #
    #     # Prepare params (input file, output file, framesize)
    #     for partition in video.arousal.arousal_partitions:
    #
    #         # Prepare params (input file, output file, framesize)
    #         start_second = partition[0][0] / fps
    #         end_second = partition[1][0] /fps
    #         output_file = os.path.join(video.dataset.audio_folder_path, "{}.mfcc.csv".format(video.name))
    #         params = '-I "{}" -O "{}" -F {} -S {} -E {}'.format(audio_path, output_file, framesize, start_second, end_second)
    #
    #         # Do extraction
    #         self._extract(self.CONFIG_INTENSITY, params)
    #
    #
    #         intensity = list()
    #
    #         #Read the csv and add them to the multimedia element
    #         with open(output_file, 'rb') as csvfile:
    #             csv_reader = csv.DictReader(csvfile, delimiter=';')
    #             for i, row in enumerate(csv_reader):
    #                 frameFeatures = {}
    #                 frameFeatures['frameTime'] = float(row['frameTime']) + int(start_second)
    #                 frameFeatures['pcm_intensity_sma_max'] = float(row['pcm_intensity_sma_max'])
    #                 frameFeatures['pcm_intensity_sma_min'] = float(row['pcm_intensity_sma_min'])
    #                 frameFeatures['pcm_intensity_sma_range'] = float(row['pcm_intensity_sma_range'])
    #                 frameFeatures['pcm_intensity_sma_maxPos'] = float(row['pcm_intensity_sma_maxPos'])
    #                 frameFeatures['pcm_intensity_sma_minPos'] = float(row['pcm_intensity_sma_minPos'])
    #                 frameFeatures['pcm_intensity_sma_amean'] = float(row['pcm_intensity_sma_amean'])
    #                 frameFeatures['pcm_intensity_sma_linregc1'] = float(row['pcm_intensity_sma_linregc1'])
    #                 frameFeatures['pcm_intensity_sma_linregc2'] = float(row['pcm_intensity_sma_linregc2'])
    #                 frameFeatures['pcm_intensity_sma_linregerrQ'] = float(row['pcm_intensity_sma_linregerrQ'])
    #                 frameFeatures['pcm_intensity_sma_stddev'] = float(row['pcm_intensity_sma_stddev'])
    #                 frameFeatures['pcm_intensity_sma_skewness'] = float(row['pcm_intensity_sma_skewness'])
    #                 frameFeatures['pcm_intensity_sma_kurtosis'] = float(row['pcm_intensity_sma_kurtosis'])
    #                 frameFeatures['pcm_intensity_sma_de_max'] = float(row['pcm_intensity_sma_de_max'])
    #                 frameFeatures['pcm_intensity_sma_de_min'] = float(row['pcm_intensity_sma_de_min'])
    #                 frameFeatures['pcm_intensity_sma_de_range'] = float(row['pcm_intensity_sma_de_range'])
    #                 frameFeatures['pcm_intensity_sma_de_maxPos'] = float(row['pcm_intensity_sma_de_maxPos'])
    #                 frameFeatures['pcm_intensity_sma_de_minPos'] = float(row['pcm_intensity_sma_de_minPos'])
    #                 frameFeatures['pcm_intensity_sma_de_amean'] = float(row['pcm_intensity_sma_de_amean'])
    #                 frameFeatures['pcm_intensity_sma_de_linregc1'] = float(row['pcm_intensity_sma_de_linregc1'])
    #                 frameFeatures['pcm_intensity_sma_de_linregc2'] = float(row['pcm_intensity_sma_de_linregc2'])
    #                 frameFeatures['pcm_intensity_sma_de_linregerrQ'] = float(row['pcm_intensity_sma_de_linregerrQ'])
    #                 frameFeatures['pcm_intensity_sma_de_stddev'] = float(row['pcm_intensity_sma_de_stddev'])
    #                 frameFeatures['pcm_intensity_sma_de_skewness'] = float(row['pcm_intensity_sma_de_skewness'])
    #                 frameFeatures['pcm_intensity_sma_de_kurtosis'] = float(row['pcm_intensity_sma_de_kurtosis'])
    #
    #                 frameFeatures['pcm_loudness_sma_max'] = float(row['pcm_loudness_sma_max'])
    #                 frameFeatures['pcm_loudness_sma_min'] = float(row['pcm_loudness_sma_min'])
    #                 frameFeatures['pcm_loudness_sma_range'] = float(row['pcm_loudness_sma_range'])
    #                 frameFeatures['pcm_loudness_sma_maxPos'] = float(row['pcm_loudness_sma_maxPos'])
    #                 frameFeatures['pcm_loudness_sma_minPos'] = float(row['pcm_loudness_sma_minPos'])
    #                 frameFeatures['pcm_loudness_sma_amean'] = float(row['pcm_loudness_sma_amean'])
    #                 frameFeatures['pcm_loudness_sma_linregc1'] = float(row['pcm_loudness_sma_linregc1'])
    #                 frameFeatures['pcm_loudness_sma_linregc2'] = float(row['pcm_loudness_sma_linregc2'])
    #                 frameFeatures['pcm_loudness_sma_linregerrQ'] = float(row['pcm_loudness_sma_linregerrQ'])
    #                 frameFeatures['pcm_loudness_sma_stddev'] = float(row['pcm_loudness_sma_stddev'])
    #                 frameFeatures['pcm_loudness_sma_skewness'] = float(row['pcm_loudness_sma_skewness'])
    #                 frameFeatures['pcm_loudness_sma_kurtosis'] = float(row['pcm_loudness_sma_kurtosis'])
    #                 frameFeatures['pcm_loudness_sma_de_max'] = float(row['pcm_loudness_sma_de_max'])
    #                 frameFeatures['pcm_loudness_sma_de_min'] = float(row['pcm_loudness_sma_de_min'])
    #                 frameFeatures['pcm_loudness_sma_de_range'] = float(row['pcm_loudness_sma_de_range'])
    #                 frameFeatures['pcm_loudness_sma_de_maxPos'] = float(row['pcm_loudness_sma_de_maxPos'])
    #                 frameFeatures['pcm_loudness_sma_de_minPos'] = float(row['pcm_loudness_sma_de_minPos'])
    #                 frameFeatures['pcm_loudness_sma_de_amean'] = float(row['pcm_loudness_sma_de_amean'])
    #                 frameFeatures['pcm_loudness_sma_de_linregc1'] = float(row['pcm_loudness_sma_de_linregc1'])
    #                 frameFeatures['pcm_loudness_sma_de_linregc2'] = float(row['pcm_loudness_sma_de_linregc2'])
    #                 frameFeatures['pcm_loudness_sma_de_linregerrQ'] = float(row['pcm_loudness_sma_de_linregerrQ'])
    #                 frameFeatures['pcm_loudness_sma_de_stddev'] = float(row['pcm_loudness_sma_de_stddev'])
    #                 frameFeatures['pcm_loudness_sma_de_skewness'] = float(row['pcm_loudness_sma_de_skewness'])
    #                 frameFeatures['pcm_loudness_sma_de_kurtosis'] = float(row['pcm_loudness_sma_de_kurtosis'])
    #
    #                 intensity.append(frameFeatures)
    #     #Cleanup
    #     os.remove(output_file)
    #
    #     return intensity
    #
    #
    # def compute_energy_with_functionals(self, video):
    #     """
    #     Energy feature extraction for a given video. Returns a dictionary containing the list of energy functionals
    #
    #     Returned dictionary looks like:
    #     {   "frameTime": 0.0,
    #         ""pcm_RMSenergy_sma_amean": 0.0,
    #         "pcm_RMSenergy_sma_minPos": 0.0,
    #         "pcm_RMSenergy_sma_linregc2": 0.0,  ...
    #     """
    #     logger.info("Computing energy with functionals")
    #
    #     audio_path = video.audio_path
    #     output_file = os.path.join(video.dataset.audio_folder_path, "{}.energy-with-func.csv".format(video.name))
    #
    #     # Get video frame-rate, and compute framesize (in seconds)
    #     fps = video.video_part.fps
    #     framesize = 1 / fps
    #
    #     # Prepare params (input file, output file, framesize)
    #     params = '-I "{}" -O "{}" -F {}'.format(audio_path, output_file, framesize)
    #
    #     # Do extraction
    #     self._extract(self.CONFIG_ENERGY_WITH_FUNCTIONALS, params)
    #
    #
    #     energy = list()
    #
    #     #Read the csv and add them to the multimedia element
    #     with open(output_file, 'rb') as csvfile:
    #         csv_reader = csv.DictReader(csvfile, delimiter=';')
    #         for i, row in enumerate(csv_reader):
    #             frameFeatures = {}
    #             frameFeatures['frameTime'] = float(row['frameTime'])
    #             frameFeatures['pcm_RMSenergy_sma_max'] = float(row['pcm_RMSenergy_sma_max'])
    #             frameFeatures['pcm_RMSenergy_sma_min'] = float(row['pcm_RMSenergy_sma_min'])
    #             frameFeatures['pcm_RMSenergy_sma_range'] = float(row['pcm_RMSenergy_sma_range'])
    #             frameFeatures['pcm_RMSenergy_sma_maxPos'] = float(row['pcm_RMSenergy_sma_maxPos'])
    #             frameFeatures['pcm_RMSenergy_sma_minPos'] = float(row['pcm_RMSenergy_sma_minPos'])
    #             frameFeatures['pcm_RMSenergy_sma_amean'] = float(row['pcm_RMSenergy_sma_amean'])
    #             frameFeatures['pcm_RMSenergy_sma_linregc1'] = float(row['pcm_RMSenergy_sma_linregc1'])
    #             frameFeatures['pcm_RMSenergy_sma_linregc2'] = float(row['pcm_RMSenergy_sma_linregc2'])
    #             frameFeatures['pcm_RMSenergy_sma_linregerrQ'] = float(row['pcm_RMSenergy_sma_linregerrQ'])
    #             frameFeatures['pcm_RMSenergy_sma_stddev'] = float(row['pcm_RMSenergy_sma_stddev'])
    #             frameFeatures['pcm_RMSenergy_sma_skewness'] = float(row['pcm_RMSenergy_sma_skewness'])
    #             frameFeatures['pcm_RMSenergy_sma_kurtosis'] = float(row['pcm_RMSenergy_sma_kurtosis'])
    #             frameFeatures['pcm_RMSenergy_sma_de_max'] = float(row['pcm_RMSenergy_sma_de_max'])
    #             frameFeatures['pcm_RMSenergy_sma_de_min'] = float(row['pcm_RMSenergy_sma_de_min'])
    #             frameFeatures['pcm_RMSenergy_sma_de_range'] = float(row['pcm_RMSenergy_sma_de_range'])
    #             frameFeatures['pcm_RMSenergy_sma_de_maxPos'] = float(row['pcm_RMSenergy_sma_de_maxPos'])
    #             frameFeatures['pcm_RMSenergy_sma_de_minPos'] = float(row['pcm_RMSenergy_sma_de_minPos'])
    #             frameFeatures['pcm_RMSenergy_sma_de_amean'] = float(row['pcm_RMSenergy_sma_de_amean'])
    #             frameFeatures['pcm_RMSenergy_sma_de_linregc1'] = float(row['pcm_RMSenergy_sma_de_linregc1'])
    #             frameFeatures['pcm_RMSenergy_sma_de_linregc2'] = float(row['pcm_RMSenergy_sma_de_linregc2'])
    #             frameFeatures['pcm_RMSenergy_sma_de_linregerrQ'] = float(row['pcm_RMSenergy_sma_de_linregerrQ'])
    #             frameFeatures['pcm_RMSenergy_sma_de_stddev'] = float(row['pcm_RMSenergy_sma_de_stddev'])
    #             frameFeatures['pcm_RMSenergy_sma_de_skewness'] = float(row['pcm_RMSenergy_sma_de_skewness'])
    #             frameFeatures['pcm_RMSenergy_sma_de_kurtosis'] = float(row['pcm_RMSenergy_sma_de_kurtosis'])
    #
    #             energy.append(frameFeatures)
    #     #Cleanup
    #     os.remove(output_file)
    #
    #     return energy
    #
    # def compute_energy_with_functionals_on_relevant_parts(self, video):
    #     """
    #     Energy feature extraction for a given video. Returns a dictionary containing the list of energy functionals
    #
    #     Returned dictionary looks like:
    #     {   "frameTime": 0.0,
    #         ""pcm_RMSenergy_sma_amean": 0.0,
    #         "pcm_RMSenergy_sma_minPos": 0.0,
    #         "pcm_RMSenergy_sma_linregc2": 0.0,  ...
    #     """
    #     logger.info("Computing energy with functionals")
    #
    #     audio_path = video.audio_path
    #     output_file = os.path.join(video.dataset.audio_folder_path, "{}.energy-with-func.csv".format(video.name))
    #
    #     # Get video frame-rate, and compute framesize (in seconds)
    #     fps = video.video_part.fps
    #     framesize = 1 / fps
    #
    #     # Prepare params (input file, output file, framesize)
    #     for partition in video.arousal.arousal_partitions:
    #
    #         # Prepare params (input file, output file, framesize)
    #         start_second = partition[0][0] / fps
    #         end_second = partition[1][0] /fps
    #         output_file = os.path.join(video.dataset.audio_folder_path, "{}.mfcc.csv".format(video.name))
    #         params = '-I "{}" -O "{}" -F {} -S {} -E {}'.format(audio_path, output_file, framesize, start_second, end_second)
    #
    #         # Do extraction
    #         self._extract(self.CONFIG_ENERGY_WITH_FUNCTIONALS, params)
    #
    #
    #         energy = list()
    #
    #         #Read the csv and add them to the multimedia element
    #         with open(output_file, 'rb') as csvfile:
    #             csv_reader = csv.DictReader(csvfile, delimiter=';')
    #             for i, row in enumerate(csv_reader):
    #                 frameFeatures = {}
    #                 frameFeatures['frameTime'] = float(row['frameTime']) + int(start_second)
    #                 frameFeatures['pcm_RMSenergy_sma_max'] = float(row['pcm_RMSenergy_sma_max'])
    #                 frameFeatures['pcm_RMSenergy_sma_min'] = float(row['pcm_RMSenergy_sma_min'])
    #                 frameFeatures['pcm_RMSenergy_sma_range'] = float(row['pcm_RMSenergy_sma_range'])
    #                 frameFeatures['pcm_RMSenergy_sma_maxPos'] = float(row['pcm_RMSenergy_sma_maxPos'])
    #                 frameFeatures['pcm_RMSenergy_sma_minPos'] = float(row['pcm_RMSenergy_sma_minPos'])
    #                 frameFeatures['pcm_RMSenergy_sma_amean'] = float(row['pcm_RMSenergy_sma_amean'])
    #                 frameFeatures['pcm_RMSenergy_sma_linregc1'] = float(row['pcm_RMSenergy_sma_linregc1'])
    #                 frameFeatures['pcm_RMSenergy_sma_linregc2'] = float(row['pcm_RMSenergy_sma_linregc2'])
    #                 frameFeatures['pcm_RMSenergy_sma_linregerrQ'] = float(row['pcm_RMSenergy_sma_linregerrQ'])
    #                 frameFeatures['pcm_RMSenergy_sma_stddev'] = float(row['pcm_RMSenergy_sma_stddev'])
    #                 frameFeatures['pcm_RMSenergy_sma_skewness'] = float(row['pcm_RMSenergy_sma_skewness'])
    #                 frameFeatures['pcm_RMSenergy_sma_kurtosis'] = float(row['pcm_RMSenergy_sma_kurtosis'])
    #                 frameFeatures['pcm_RMSenergy_sma_de_max'] = float(row['pcm_RMSenergy_sma_de_max'])
    #                 frameFeatures['pcm_RMSenergy_sma_de_min'] = float(row['pcm_RMSenergy_sma_de_min'])
    #                 frameFeatures['pcm_RMSenergy_sma_de_range'] = float(row['pcm_RMSenergy_sma_de_range'])
    #                 frameFeatures['pcm_RMSenergy_sma_de_maxPos'] = float(row['pcm_RMSenergy_sma_de_maxPos'])
    #                 frameFeatures['pcm_RMSenergy_sma_de_minPos'] = float(row['pcm_RMSenergy_sma_de_minPos'])
    #                 frameFeatures['pcm_RMSenergy_sma_de_amean'] = float(row['pcm_RMSenergy_sma_de_amean'])
    #                 frameFeatures['pcm_RMSenergy_sma_de_linregc1'] = float(row['pcm_RMSenergy_sma_de_linregc1'])
    #                 frameFeatures['pcm_RMSenergy_sma_de_linregc2'] = float(row['pcm_RMSenergy_sma_de_linregc2'])
    #                 frameFeatures['pcm_RMSenergy_sma_de_linregerrQ'] = float(row['pcm_RMSenergy_sma_de_linregerrQ'])
    #                 frameFeatures['pcm_RMSenergy_sma_de_stddev'] = float(row['pcm_RMSenergy_sma_de_stddev'])
    #                 frameFeatures['pcm_RMSenergy_sma_de_skewness'] = float(row['pcm_RMSenergy_sma_de_skewness'])
    #                 frameFeatures['pcm_RMSenergy_sma_de_kurtosis'] = float(row['pcm_RMSenergy_sma_de_kurtosis'])
    #
    #                 energy.append(frameFeatures)
    #     #Cleanup
    #     os.remove(output_file)
    #
    #     return energy
    #
    #
    # def compute_mzcr_with_functionals(self, video):
    #     """
    #     Zero crossings feature extraction for a given video. Returns a dictionary containing the list of zero crossings functionals
    #
    #     Returned dictionary looks like:
    #     {   "frameTime": 0.0,
    #         "pcm_zcr_sma_de_linregerrQ": 4.132327e-05,
    #             "pcm_zcr_sma_linregerrQ": 0.000783579,
    #             "pcm_zcr_sma_range": 0.1157986,   ...
    #     """
    #     logger.info("Computing zero crossings")
    #
    #     audio_path = video.audio_path
    #     output_file = os.path.join(video.dataset.audio_folder_path, "{}.mzcr.csv".format(video.name))
    #
    #     # Get video frame-rate, and compute framesize (in seconds)
    #     fps = video.video_part.fps
    #     framesize = 1 / fps
    #
    #     # Prepare params (input file, output file, framesize)
    #     params = '-I "{}" -O "{}" -F {}'.format(audio_path, output_file, framesize)
    #
    #     # Do extraction
    #     self._extract(self.CONFIG_MZCR, params)
    #
    #
    #     mzcr = list()
    #
    #     #Read the csv and add them to the multimedia element
    #     with open(output_file, 'rb') as csvfile:
    #         csv_reader = csv.DictReader(csvfile, delimiter=';')
    #         for i, row in enumerate(csv_reader):
    #             frameFeatures = {}
    #             frameFeatures['frameTime'] = float(row['frameTime'])
    #             frameFeatures['pcm_zcr_sma_max'] = float(row['pcm_zcr_sma_max'])
    #             frameFeatures['pcm_zcr_sma_min'] = float(row['pcm_zcr_sma_min'])
    #             frameFeatures['pcm_zcr_sma_range'] = float(row['pcm_zcr_sma_range'])
    #             frameFeatures['pcm_zcr_sma_maxPos'] = float(row['pcm_zcr_sma_maxPos'])
    #             frameFeatures['pcm_zcr_sma_minPos'] = float(row['pcm_zcr_sma_minPos'])
    #             frameFeatures['pcm_zcr_sma_amean'] = float(row['pcm_zcr_sma_amean'])
    #             frameFeatures['pcm_zcr_sma_linregc1'] = float(row['pcm_zcr_sma_linregc1'])
    #             frameFeatures['pcm_zcr_sma_linregc2'] = float(row['pcm_zcr_sma_linregc2'])
    #             frameFeatures['pcm_zcr_sma_linregerrQ'] = float(row['pcm_zcr_sma_linregerrQ'])
    #             frameFeatures['pcm_zcr_sma_stddev'] = float(row['pcm_zcr_sma_stddev'])
    #             frameFeatures['pcm_zcr_sma_skewness'] = float(row['pcm_zcr_sma_skewness'])
    #             frameFeatures['pcm_zcr_sma_kurtosis'] = float(row['pcm_zcr_sma_kurtosis'])
    #             frameFeatures['pcm_zcr_sma_de_max'] = float(row['pcm_zcr_sma_de_max'])
    #             frameFeatures['pcm_zcr_sma_de_min'] = float(row['pcm_zcr_sma_de_min'])
    #             frameFeatures['pcm_zcr_sma_de_range'] = float(row['pcm_zcr_sma_de_range'])
    #             frameFeatures['pcm_zcr_sma_de_maxPos'] = float(row['pcm_zcr_sma_de_maxPos'])
    #             frameFeatures['pcm_zcr_sma_de_minPos'] = float(row['pcm_zcr_sma_de_minPos'])
    #             frameFeatures['pcm_zcr_sma_de_amean'] = float(row['pcm_zcr_sma_de_amean'])
    #             frameFeatures['pcm_zcr_sma_de_linregc1'] = float(row['pcm_zcr_sma_de_linregc1'])
    #             frameFeatures['pcm_zcr_sma_de_linregc2'] = float(row['pcm_zcr_sma_de_linregc2'])
    #             frameFeatures['pcm_zcr_sma_de_linregerrQ'] = float(row['pcm_zcr_sma_de_linregerrQ'])
    #             frameFeatures['pcm_zcr_sma_de_stddev'] = float(row['pcm_zcr_sma_de_stddev'])
    #             frameFeatures['pcm_zcr_sma_de_skewness'] = float(row['pcm_zcr_sma_de_skewness'])
    #             frameFeatures['pcm_zcr_sma_de_kurtosis'] = float(row['pcm_zcr_sma_de_kurtosis'])
    #
    #             mzcr.append(frameFeatures)
    #     #Cleanup
    #     os.remove(output_file)
    #
    #     return mzcr
    #
    # def compute_mzcr_with_functionals_on_relevant_parts(self, video):
    #     """
    #     Zero crossings feature extraction for a given video. Returns a dictionary containing the list of zero crossings functionals
    #
    #     Returned dictionary looks like:
    #     {   "frameTime": 0.0,
    #         "pcm_zcr_sma_de_linregerrQ": 4.132327e-05,
    #             "pcm_zcr_sma_linregerrQ": 0.000783579,
    #             "pcm_zcr_sma_range": 0.1157986,   ...
    #     """
    #     logger.info("Computing zero crossings")
    #
    #     audio_path = video.audio_path
    #     output_file = os.path.join(video.dataset.audio_folder_path, "{}.mzcr.csv".format(video.name))
    #
    #     # Get video frame-rate, and compute framesize (in seconds)
    #     fps = video.video_part.fps
    #     framesize = 1 / fps
    #
    #     # Prepare params (input file, output file, framesize)
    #     for partition in video.arousal.arousal_partitions:
    #
    #         # Prepare params (input file, output file, framesize)
    #         start_second = partition[0][0] / fps
    #         end_second = partition[1][0] /fps
    #         output_file = os.path.join(video.dataset.audio_folder_path, "{}.mfcc.csv".format(video.name))
    #         params = '-I "{}" -O "{}" -F {} -S {} -E {}'.format(audio_path, output_file, framesize, start_second, end_second)
    #
    #         # Do extraction
    #         self._extract(self.CONFIG_MZCR, params)
    #
    #
    #         mzcr = list()
    #
    #         #Read the csv and add them to the multimedia element
    #         with open(output_file, 'rb') as csvfile:
    #             csv_reader = csv.DictReader(csvfile, delimiter=';')
    #             for i, row in enumerate(csv_reader):
    #                 frameFeatures = {}
    #                 frameFeatures['frameTime'] = float(row['frameTime']) + int(start_second)
    #                 frameFeatures['pcm_zcr_sma_max'] = float(row['pcm_zcr_sma_max'])
    #                 frameFeatures['pcm_zcr_sma_min'] = float(row['pcm_zcr_sma_min'])
    #                 frameFeatures['pcm_zcr_sma_range'] = float(row['pcm_zcr_sma_range'])
    #                 frameFeatures['pcm_zcr_sma_maxPos'] = float(row['pcm_zcr_sma_maxPos'])
    #                 frameFeatures['pcm_zcr_sma_minPos'] = float(row['pcm_zcr_sma_minPos'])
    #                 frameFeatures['pcm_zcr_sma_amean'] = float(row['pcm_zcr_sma_amean'])
    #                 frameFeatures['pcm_zcr_sma_linregc1'] = float(row['pcm_zcr_sma_linregc1'])
    #                 frameFeatures['pcm_zcr_sma_linregc2'] = float(row['pcm_zcr_sma_linregc2'])
    #                 frameFeatures['pcm_zcr_sma_linregerrQ'] = float(row['pcm_zcr_sma_linregerrQ'])
    #                 frameFeatures['pcm_zcr_sma_stddev'] = float(row['pcm_zcr_sma_stddev'])
    #                 frameFeatures['pcm_zcr_sma_skewness'] = float(row['pcm_zcr_sma_skewness'])
    #                 frameFeatures['pcm_zcr_sma_kurtosis'] = float(row['pcm_zcr_sma_kurtosis'])
    #                 frameFeatures['pcm_zcr_sma_de_max'] = float(row['pcm_zcr_sma_de_max'])
    #                 frameFeatures['pcm_zcr_sma_de_min'] = float(row['pcm_zcr_sma_de_min'])
    #                 frameFeatures['pcm_zcr_sma_de_range'] = float(row['pcm_zcr_sma_de_range'])
    #                 frameFeatures['pcm_zcr_sma_de_maxPos'] = float(row['pcm_zcr_sma_de_maxPos'])
    #                 frameFeatures['pcm_zcr_sma_de_minPos'] = float(row['pcm_zcr_sma_de_minPos'])
    #                 frameFeatures['pcm_zcr_sma_de_amean'] = float(row['pcm_zcr_sma_de_amean'])
    #                 frameFeatures['pcm_zcr_sma_de_linregc1'] = float(row['pcm_zcr_sma_de_linregc1'])
    #                 frameFeatures['pcm_zcr_sma_de_linregc2'] = float(row['pcm_zcr_sma_de_linregc2'])
    #                 frameFeatures['pcm_zcr_sma_de_linregerrQ'] = float(row['pcm_zcr_sma_de_linregerrQ'])
    #                 frameFeatures['pcm_zcr_sma_de_stddev'] = float(row['pcm_zcr_sma_de_stddev'])
    #                 frameFeatures['pcm_zcr_sma_de_skewness'] = float(row['pcm_zcr_sma_de_skewness'])
    #                 frameFeatures['pcm_zcr_sma_de_kurtosis'] = float(row['pcm_zcr_sma_de_kurtosis'])
    #
    #                 mzcr.append(frameFeatures)
    #     #Cleanup
    #     os.remove(output_file)
    #
    #     return mzcr
    #
    #
    # def compute_spectral_with_functionals(self, video):
    #     """
    #     Spectral feature extraction for a given video. Returns a dictionary containing the list of spectral features functionals
    #
    #     Returned dictionary looks like:
    #     {   "frameTime": 0.0,
    #         "pcm_Mag_fband0-650_sma_skewness": 0.09087647,
    #             "pcm_Mag_fband1000-4000_sma_range": 7.615095e-06,
    #             "pcm_Mag_fband0-250_sma_de_maxPos": 2.0,
    #             "pcm_Mag_spectralRollOff50.0_sma_linregc2": 3617.764,   ...
    #     """
    #     logger.info("Computing spectral features")
    #
    #     audio_path = video.audio_path
    #     output_file = os.path.join(video.dataset.audio_folder_path, "{}.spectral.csv".format(video.name))
    #
    #     # Get video frame-rate, and compute framesize (in seconds)
    #     fps = video.video_part.fps
    #     framesize = 1 / fps
    #
    #     # Prepare params (input file, output file, framesize)
    #     params = '-I "{}" -O "{}" -F {}'.format(audio_path, output_file, framesize)
    #
    #     # Do extraction
    #     self._extract(self.CONFIG_SPECTRAL, params)
    #
    #
    #     spectral = list()
    #
    #     #Read the csv and add them to the multimedia element
    #     with open(output_file, 'rb') as csvfile:
    #         csv_reader = csv.DictReader(csvfile, delimiter=';')
    #         for i, row in enumerate(csv_reader):
    #             frameFeatures = {}
    #             frameFeatures['frameTime'] = float(row['frameTime'])
    #
    #             for range in ['0-250','0-650','250-650','1000-4000','3010-9123']:
    #                 frameFeatures['pcm_Mag_fband'+range+'_sma_max'] = float(row['pcm_Mag_fband'+range+'_sma_max'])
    #                 frameFeatures['pcm_Mag_fband'+range+'_sma_min'] = float(row['pcm_Mag_fband'+range+'_sma_min'])
    #                 frameFeatures['pcm_Mag_fband'+range+'_sma_range'] = float(row['pcm_Mag_fband'+range+'_sma_range'])
    #                 frameFeatures['pcm_Mag_fband'+range+'_sma_maxPos'] = float(row['pcm_Mag_fband'+range+'_sma_maxPos'])
    #                 frameFeatures['pcm_Mag_fband'+range+'_sma_minPos'] = float(row['pcm_Mag_fband'+range+'_sma_minPos'])
    #                 frameFeatures['pcm_Mag_fband'+range+'_sma_amean'] = float(row['pcm_Mag_fband'+range+'_sma_amean'])
    #                 frameFeatures['pcm_Mag_fband'+range+'_sma_linregc1'] = float(row['pcm_Mag_fband'+range+'_sma_linregc1'])
    #                 frameFeatures['pcm_Mag_fband'+range+'_sma_linregc2'] = float(row['pcm_Mag_fband'+range+'_sma_linregc2'])
    #                 frameFeatures['pcm_Mag_fband'+range+'_sma_linregerrQ'] = float(row['pcm_Mag_fband'+range+'_sma_linregerrQ'])
    #                 frameFeatures['pcm_Mag_fband'+range+'_sma_stddev'] = float(row['pcm_Mag_fband'+range+'_sma_stddev'])
    #                 frameFeatures['pcm_Mag_fband'+range+'_sma_skewness'] = float(row['pcm_Mag_fband'+range+'_sma_skewness'])
    #                 frameFeatures['pcm_Mag_fband'+range+'_sma_kurtosis'] = float(row['pcm_Mag_fband'+range+'_sma_kurtosis'])
    #                 frameFeatures['pcm_Mag_fband'+range+'_sma_de_max'] = float(row['pcm_Mag_fband'+range+'_sma_de_max'])
    #                 frameFeatures['pcm_Mag_fband'+range+'_sma_de_min'] = float(row['pcm_Mag_fband'+range+'_sma_de_min'])
    #                 frameFeatures['pcm_Mag_fband'+range+'_sma_de_range'] = float(row['pcm_Mag_fband'+range+'_sma_de_range'])
    #                 frameFeatures['pcm_Mag_fband'+range+'_sma_de_maxPos'] = float(row['pcm_Mag_fband'+range+'_sma_de_maxPos'])
    #                 frameFeatures['pcm_Mag_fband'+range+'_sma_de_minPos'] = float(row['pcm_Mag_fband'+range+'_sma_de_minPos'])
    #                 frameFeatures['pcm_Mag_fband'+range+'_sma_de_amean'] = float(row['pcm_Mag_fband'+range+'_sma_de_amean'])
    #                 frameFeatures['pcm_Mag_fband'+range+'_sma_de_linregc1'] = float(row['pcm_Mag_fband'+range+'_sma_de_linregc1'])
    #                 frameFeatures['pcm_Mag_fband'+range+'_sma_de_linregc2'] = float(row['pcm_Mag_fband'+range+'_sma_de_linregc2'])
    #                 frameFeatures['pcm_Mag_fband'+range+'_sma_de_linregerrQ'] = float(row['pcm_Mag_fband'+range+'_sma_de_linregerrQ'])
    #                 frameFeatures['pcm_Mag_fband'+range+'_sma_de_stddev'] = float(row['pcm_Mag_fband'+range+'_sma_de_stddev'])
    #                 frameFeatures['pcm_Mag_fband'+range+'_sma_de_skewness'] = float(row['pcm_Mag_fband'+range+'_sma_de_skewness'])
    #                 frameFeatures['pcm_Mag_fband'+range+'_sma_de_kurtosis'] = float(row['pcm_Mag_fband'+range+'_sma_de_kurtosis'])
    #
    #             for range in ['25.0','50.0','75.0','90.0']:
    #                 frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_max'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_max'])
    #                 frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_min'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_min'])
    #                 frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_range'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_range'])
    #                 frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_maxPos'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_maxPos'])
    #                 frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_minPos'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_minPos'])
    #                 frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_amean'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_amean'])
    #                 frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_linregc1'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_linregc1'])
    #                 frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_linregc2'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_linregc2'])
    #                 frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_linregerrQ'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_linregerrQ'])
    #                 frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_stddev'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_stddev'])
    #                 frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_skewness'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_skewness'])
    #                 frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_kurtosis'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_kurtosis'])
    #                 frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_de_max'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_de_max'])
    #                 frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_de_min'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_de_min'])
    #                 frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_de_range'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_de_range'])
    #                 frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_de_maxPos'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_de_maxPos'])
    #                 frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_de_minPos'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_de_minPos'])
    #                 frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_de_amean'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_de_amean'])
    #                 frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_de_linregc1'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_de_linregc1'])
    #                 frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_de_linregc2'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_de_linregc2'])
    #                 frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_de_linregerrQ'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_de_linregerrQ'])
    #                 frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_de_stddev'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_de_stddev'])
    #                 frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_de_skewness'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_de_skewness'])
    #                 frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_de_kurtosis'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_de_kurtosis'])
    #
    #             for feature in ['spectralFlux','spectralCentroid','spectralMaxPos','spectralMinPos']:
    #                 frameFeatures['pcm_Mag_'+feature+'_sma_max'] = float(row['pcm_Mag_'+feature+'_sma_max'])
    #                 frameFeatures['pcm_Mag_'+feature+'_sma_min'] = float(row['pcm_Mag_'+feature+'_sma_min'])
    #                 frameFeatures['pcm_Mag_'+feature+'_sma_range'] = float(row['pcm_Mag_'+feature+'_sma_range'])
    #                 frameFeatures['pcm_Mag_'+feature+'_sma_maxPos'] = float(row['pcm_Mag_'+feature+'_sma_maxPos'])
    #                 frameFeatures['pcm_Mag_'+feature+'_sma_minPos'] = float(row['pcm_Mag_'+feature+'_sma_minPos'])
    #                 frameFeatures['pcm_Mag_'+feature+'_sma_amean'] = float(row['pcm_Mag_'+feature+'_sma_amean'])
    #                 frameFeatures['pcm_Mag_'+feature+'_sma_linregc1'] = float(row['pcm_Mag_'+feature+'_sma_linregc1'])
    #                 frameFeatures['pcm_Mag_'+feature+'_sma_linregc2'] = float(row['pcm_Mag_'+feature+'_sma_linregc2'])
    #                 frameFeatures['pcm_Mag_'+feature+'_sma_linregerrQ'] = float(row['pcm_Mag_'+feature+'_sma_linregerrQ'])
    #                 frameFeatures['pcm_Mag_'+feature+'_sma_stddev'] = float(row['pcm_Mag_'+feature+'_sma_stddev'])
    #                 frameFeatures['pcm_Mag_'+feature+'_sma_skewness'] = float(row['pcm_Mag_'+feature+'_sma_skewness'])
    #                 frameFeatures['pcm_Mag_'+feature+'_sma_kurtosis'] = float(row['pcm_Mag_'+feature+'_sma_kurtosis'])
    #                 frameFeatures['pcm_Mag_'+feature+'_sma_de_max'] = float(row['pcm_Mag_'+feature+'_sma_de_max'])
    #                 frameFeatures['pcm_Mag_'+feature+'_sma_de_min'] = float(row['pcm_Mag_'+feature+'_sma_de_min'])
    #                 frameFeatures['pcm_Mag_'+feature+'_sma_de_range'] = float(row['pcm_Mag_'+feature+'_sma_de_range'])
    #                 frameFeatures['pcm_Mag_'+feature+'_sma_de_maxPos'] = float(row['pcm_Mag_'+feature+'_sma_de_maxPos'])
    #                 frameFeatures['pcm_Mag_'+feature+'_sma_de_minPos'] = float(row['pcm_Mag_'+feature+'_sma_de_minPos'])
    #                 frameFeatures['pcm_Mag_'+feature+'_sma_de_amean'] = float(row['pcm_Mag_'+feature+'_sma_de_amean'])
    #                 frameFeatures['pcm_Mag_'+feature+'_sma_de_linregc1'] = float(row['pcm_Mag_'+feature+'_sma_de_linregc1'])
    #                 frameFeatures['pcm_Mag_'+feature+'_sma_de_linregc2'] = float(row['pcm_Mag_'+feature+'_sma_de_linregc2'])
    #                 frameFeatures['pcm_Mag_'+feature+'_sma_de_linregerrQ'] = float(row['pcm_Mag_'+feature+'_sma_de_linregerrQ'])
    #                 frameFeatures['pcm_Mag_'+feature+'_sma_de_stddev'] = float(row['pcm_Mag_'+feature+'_sma_de_stddev'])
    #                 frameFeatures['pcm_Mag_'+feature+'_sma_de_skewness'] = float(row['pcm_Mag_'+feature+'_sma_de_skewness'])
    #                 frameFeatures['pcm_Mag_'+feature+'_sma_de_kurtosis'] = float(row['pcm_Mag_'+feature+'_sma_de_kurtosis'])
    #
    #             spectral.append(frameFeatures)
    #     #Cleanup
    #     os.remove(output_file)
    #
    #     return spectral
    #
    # def compute_spectral_with_functionals_on_relevant_parts(self, video):
    #     """
    #     Spectral feature extraction for a given video. Returns a dictionary containing the list of spectral features functionals
    #
    #     Returned dictionary looks like:
    #     {   "frameTime": 0.0,
    #         "pcm_Mag_fband0-650_sma_skewness": 0.09087647,
    #             "pcm_Mag_fband1000-4000_sma_range": 7.615095e-06,
    #             "pcm_Mag_fband0-250_sma_de_maxPos": 2.0,
    #             "pcm_Mag_spectralRollOff50.0_sma_linregc2": 3617.764,   ...
    #     """
    #     logger.info("Computing spectral features")
    #
    #     audio_path = video.audio_path
    #     output_file = os.path.join(video.dataset.audio_folder_path, "{}.spectral.csv".format(video.name))
    #
    #     # Get video frame-rate, and compute framesize (in seconds)
    #     fps = video.video_part.fps
    #     framesize = 1 / fps
    #
    #     # Prepare params (input file, output file, framesize)
    #     for partition in video.arousal.arousal_partitions:
    #
    #         # Prepare params (input file, output file, framesize)
    #         start_second = partition[0][0] / fps
    #         end_second = partition[1][0] /fps
    #         output_file = os.path.join(video.dataset.audio_folder_path, "{}.mfcc.csv".format(video.name))
    #         params = '-I "{}" -O "{}" -F {} -S {} -E {}'.format(audio_path, output_file, framesize, start_second, end_second)
    #
    #         # Do extraction
    #         self._extract(self.CONFIG_SPECTRAL, params)
    #
    #
    #         spectral = list()
    #
    #         #Read the csv and add them to the multimedia element
    #         with open(output_file, 'rb') as csvfile:
    #             csv_reader = csv.DictReader(csvfile, delimiter=';')
    #             for i, row in enumerate(csv_reader):
    #                 frameFeatures = {}
    #                 frameFeatures['frameTime'] = float(row['frameTime']) + int(start_second)
    #
    #                 for range in ['0-250','0-650','250-650','1000-4000','3010-9123']:
    #                     frameFeatures['pcm_Mag_fband'+range+'_sma_max'] = float(row['pcm_Mag_fband'+range+'_sma_max'])
    #                     frameFeatures['pcm_Mag_fband'+range+'_sma_min'] = float(row['pcm_Mag_fband'+range+'_sma_min'])
    #                     frameFeatures['pcm_Mag_fband'+range+'_sma_range'] = float(row['pcm_Mag_fband'+range+'_sma_range'])
    #                     frameFeatures['pcm_Mag_fband'+range+'_sma_maxPos'] = float(row['pcm_Mag_fband'+range+'_sma_maxPos'])
    #                     frameFeatures['pcm_Mag_fband'+range+'_sma_minPos'] = float(row['pcm_Mag_fband'+range+'_sma_minPos'])
    #                     frameFeatures['pcm_Mag_fband'+range+'_sma_amean'] = float(row['pcm_Mag_fband'+range+'_sma_amean'])
    #                     frameFeatures['pcm_Mag_fband'+range+'_sma_linregc1'] = float(row['pcm_Mag_fband'+range+'_sma_linregc1'])
    #                     frameFeatures['pcm_Mag_fband'+range+'_sma_linregc2'] = float(row['pcm_Mag_fband'+range+'_sma_linregc2'])
    #                     frameFeatures['pcm_Mag_fband'+range+'_sma_linregerrQ'] = float(row['pcm_Mag_fband'+range+'_sma_linregerrQ'])
    #                     frameFeatures['pcm_Mag_fband'+range+'_sma_stddev'] = float(row['pcm_Mag_fband'+range+'_sma_stddev'])
    #                     frameFeatures['pcm_Mag_fband'+range+'_sma_skewness'] = float(row['pcm_Mag_fband'+range+'_sma_skewness'])
    #                     frameFeatures['pcm_Mag_fband'+range+'_sma_kurtosis'] = float(row['pcm_Mag_fband'+range+'_sma_kurtosis'])
    #                     frameFeatures['pcm_Mag_fband'+range+'_sma_de_max'] = float(row['pcm_Mag_fband'+range+'_sma_de_max'])
    #                     frameFeatures['pcm_Mag_fband'+range+'_sma_de_min'] = float(row['pcm_Mag_fband'+range+'_sma_de_min'])
    #                     frameFeatures['pcm_Mag_fband'+range+'_sma_de_range'] = float(row['pcm_Mag_fband'+range+'_sma_de_range'])
    #                     frameFeatures['pcm_Mag_fband'+range+'_sma_de_maxPos'] = float(row['pcm_Mag_fband'+range+'_sma_de_maxPos'])
    #                     frameFeatures['pcm_Mag_fband'+range+'_sma_de_minPos'] = float(row['pcm_Mag_fband'+range+'_sma_de_minPos'])
    #                     frameFeatures['pcm_Mag_fband'+range+'_sma_de_amean'] = float(row['pcm_Mag_fband'+range+'_sma_de_amean'])
    #                     frameFeatures['pcm_Mag_fband'+range+'_sma_de_linregc1'] = float(row['pcm_Mag_fband'+range+'_sma_de_linregc1'])
    #                     frameFeatures['pcm_Mag_fband'+range+'_sma_de_linregc2'] = float(row['pcm_Mag_fband'+range+'_sma_de_linregc2'])
    #                     frameFeatures['pcm_Mag_fband'+range+'_sma_de_linregerrQ'] = float(row['pcm_Mag_fband'+range+'_sma_de_linregerrQ'])
    #                     frameFeatures['pcm_Mag_fband'+range+'_sma_de_stddev'] = float(row['pcm_Mag_fband'+range+'_sma_de_stddev'])
    #                     frameFeatures['pcm_Mag_fband'+range+'_sma_de_skewness'] = float(row['pcm_Mag_fband'+range+'_sma_de_skewness'])
    #                     frameFeatures['pcm_Mag_fband'+range+'_sma_de_kurtosis'] = float(row['pcm_Mag_fband'+range+'_sma_de_kurtosis'])
    #
    #                 for range in ['25.0','50.0','75.0','90.0']:
    #                     frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_max'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_max'])
    #                     frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_min'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_min'])
    #                     frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_range'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_range'])
    #                     frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_maxPos'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_maxPos'])
    #                     frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_minPos'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_minPos'])
    #                     frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_amean'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_amean'])
    #                     frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_linregc1'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_linregc1'])
    #                     frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_linregc2'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_linregc2'])
    #                     frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_linregerrQ'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_linregerrQ'])
    #                     frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_stddev'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_stddev'])
    #                     frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_skewness'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_skewness'])
    #                     frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_kurtosis'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_kurtosis'])
    #                     frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_de_max'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_de_max'])
    #                     frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_de_min'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_de_min'])
    #                     frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_de_range'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_de_range'])
    #                     frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_de_maxPos'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_de_maxPos'])
    #                     frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_de_minPos'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_de_minPos'])
    #                     frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_de_amean'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_de_amean'])
    #                     frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_de_linregc1'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_de_linregc1'])
    #                     frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_de_linregc2'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_de_linregc2'])
    #                     frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_de_linregerrQ'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_de_linregerrQ'])
    #                     frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_de_stddev'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_de_stddev'])
    #                     frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_de_skewness'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_de_skewness'])
    #                     frameFeatures['pcm_Mag_spectralRollOff'+range+'_sma_de_kurtosis'] = float(row['pcm_Mag_spectralRollOff'+range+'_sma_de_kurtosis'])
    #
    #                 for feature in ['spectralFlux','spectralCentroid','spectralMaxPos','spectralMinPos']:
    #                     frameFeatures['pcm_Mag_'+feature+'_sma_max'] = float(row['pcm_Mag_'+feature+'_sma_max'])
    #                     frameFeatures['pcm_Mag_'+feature+'_sma_min'] = float(row['pcm_Mag_'+feature+'_sma_min'])
    #                     frameFeatures['pcm_Mag_'+feature+'_sma_range'] = float(row['pcm_Mag_'+feature+'_sma_range'])
    #                     frameFeatures['pcm_Mag_'+feature+'_sma_maxPos'] = float(row['pcm_Mag_'+feature+'_sma_maxPos'])
    #                     frameFeatures['pcm_Mag_'+feature+'_sma_minPos'] = float(row['pcm_Mag_'+feature+'_sma_minPos'])
    #                     frameFeatures['pcm_Mag_'+feature+'_sma_amean'] = float(row['pcm_Mag_'+feature+'_sma_amean'])
    #                     frameFeatures['pcm_Mag_'+feature+'_sma_linregc1'] = float(row['pcm_Mag_'+feature+'_sma_linregc1'])
    #                     frameFeatures['pcm_Mag_'+feature+'_sma_linregc2'] = float(row['pcm_Mag_'+feature+'_sma_linregc2'])
    #                     frameFeatures['pcm_Mag_'+feature+'_sma_linregerrQ'] = float(row['pcm_Mag_'+feature+'_sma_linregerrQ'])
    #                     frameFeatures['pcm_Mag_'+feature+'_sma_stddev'] = float(row['pcm_Mag_'+feature+'_sma_stddev'])
    #                     frameFeatures['pcm_Mag_'+feature+'_sma_skewness'] = float(row['pcm_Mag_'+feature+'_sma_skewness'])
    #                     frameFeatures['pcm_Mag_'+feature+'_sma_kurtosis'] = float(row['pcm_Mag_'+feature+'_sma_kurtosis'])
    #                     frameFeatures['pcm_Mag_'+feature+'_sma_de_max'] = float(row['pcm_Mag_'+feature+'_sma_de_max'])
    #                     frameFeatures['pcm_Mag_'+feature+'_sma_de_min'] = float(row['pcm_Mag_'+feature+'_sma_de_min'])
    #                     frameFeatures['pcm_Mag_'+feature+'_sma_de_range'] = float(row['pcm_Mag_'+feature+'_sma_de_range'])
    #                     frameFeatures['pcm_Mag_'+feature+'_sma_de_maxPos'] = float(row['pcm_Mag_'+feature+'_sma_de_maxPos'])
    #                     frameFeatures['pcm_Mag_'+feature+'_sma_de_minPos'] = float(row['pcm_Mag_'+feature+'_sma_de_minPos'])
    #                     frameFeatures['pcm_Mag_'+feature+'_sma_de_amean'] = float(row['pcm_Mag_'+feature+'_sma_de_amean'])
    #                     frameFeatures['pcm_Mag_'+feature+'_sma_de_linregc1'] = float(row['pcm_Mag_'+feature+'_sma_de_linregc1'])
    #                     frameFeatures['pcm_Mag_'+feature+'_sma_de_linregc2'] = float(row['pcm_Mag_'+feature+'_sma_de_linregc2'])
    #                     frameFeatures['pcm_Mag_'+feature+'_sma_de_linregerrQ'] = float(row['pcm_Mag_'+feature+'_sma_de_linregerrQ'])
    #                     frameFeatures['pcm_Mag_'+feature+'_sma_de_stddev'] = float(row['pcm_Mag_'+feature+'_sma_de_stddev'])
    #                     frameFeatures['pcm_Mag_'+feature+'_sma_de_skewness'] = float(row['pcm_Mag_'+feature+'_sma_de_skewness'])
    #                     frameFeatures['pcm_Mag_'+feature+'_sma_de_kurtosis'] = float(row['pcm_Mag_'+feature+'_sma_de_kurtosis'])
    #
    #                 spectral.append(frameFeatures)
    #     #Cleanup
    #     os.remove(output_file)
    #
    #     return spectral
    #
    #
    # def compute_emotion_features(self, video):
    #     """
    #     Energy extraction for a given video. Returns a dictionary containing the list of energy rms and
    #     log values for each frame.
    #
    #     Returned dictionary looks like:
    #     {'energy_log': [-1.590190e+01, -4.580110e+02, ..., -4.580110e+02],
    #      'energy_rms': [3.523272e-04, 1.528272e-02, ..., 1.528272e-02]}
    #     """
    #     logger.info("Computing emotion features")
    #
    #     audio_path = video.audio_path
    #     output_file = os.path.join(video.dataset.audio_folder_path, "{}.emotion_features.csv".format(video.name))
    #
    #     # Get video frame-rate, and compute framesize (in seconds)
    #     fps = video.video_part.fps
    #     framesize = 1 / fps
    #
    #     # Prepare params (input file, output file, framesize)
    #     params = '-I "{}" -O "{}" -F {}'.format(audio_path, output_file, framesize)
    #
    #     # Do extraction
    #     self._extract(self.CONFIG_EMOTION_FEATURES, params)
    #     #
    #     #
    #     # energy = list()
    #     # # energy["energy_log"] = list()
    #     # # energy["energy_rms"] = list()
    #     #
    #     # # Read the csv and add them to the multimedia element
    #     # with open(output_file, 'rb') as csvfile:
    #     #     csv_reader = csv.DictReader(csvfile, delimiter=';')
    #     #     for i, row in enumerate(csv_reader):
    #     #         # energy["energy_log"].append(float(row['pcm_LOGenergy']))
    #     #         # energy["energy_rms"].append(float(row['pcm_RMSenergy']))
    #     #         energy.append([i, float(row['pcm_RMSenergy'])])
    #     #
    #     # # Cleanup
    #     # os.remove(output_file)
    #     #
    #     # return energy