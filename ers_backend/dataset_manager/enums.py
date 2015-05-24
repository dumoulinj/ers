from django_enumfield import enum

class BetterEnum(enum.Enum):
    def is_an_enum(label):
        return label in EmotionType.labels.values()
    is_an_enum = staticmethod(is_an_enum)

    def get_enum_from_label(label):
        if not EmotionType.is_an_enum(label):
            return -1
        return EmotionType.labels.keys()[EmotionType.labels.values().index(label)]
    get_enum_from_label = staticmethod(get_enum_from_label)


class FeatureFunctionType(BetterEnum):
    VALUE = 0
    PCM_RMS = 1
    MAX = 2
    MIN = 3
    RANGE = 4
    MAX_POS = 5
    MIN_POS = 6
    MEAN = 7
    SKEWNESS = 8
    KURTOSIS = 9

    labels = {
        VALUE: "value",
        PCM_RMS: "pcm rms",
        MAX: "max",
        MIN: "min",
        RANGE: "range",
        MAX_POS: "max pos",
        MEAN: "mean",
        SKEWNESS: "skewness",
        KURTOSIS: "kurtosis"
    }

    fields = {
        VALUE: "amean",
        PCM_RMS: "pcm_RMSenergy",
        MAX: "max",
        MIN: "min",
        RANGE: "range",
        MAX_POS: "maxPos",
        MIN_POS: "minPos",
        MEAN: "amean",
        SKEWNESS: "skewness",
        KURTOSIS: "kurtosis"
    }

    standard_audio_functions = (MEAN, MAX, MIN, RANGE, MAX_POS, MIN_POS, SKEWNESS, KURTOSIS, )

class FeatureType(BetterEnum):
    SHOT_CUT_DENSITY = 0
    BRIGHTNESS = 1

    ENERGY = 2

    MFCC_1 = 3
    MFCC_2 = 4
    MFCC_3 = 5
    MFCC_4 = 6
    MFCC_5 = 7
    MFCC_6 = 8
    MFCC_7 = 9
    MFCC_8 = 10
    MFCC_9 = 11
    MFCC_10 = 12
    MFCC_11 = 13
    MFCC_12 = 14

    PITCH_VOICE_PROB = 15
    PITCH_F0 = 16

    LSP_1 = 17
    LSP_2 = 18
    LSP_3 = 19
    LSP_4 = 20
    LSP_5 = 21
    LSP_6 = 22
    LSP_7 = 23

    INTENSITY = 24
    LOUDNESS = 25

    MZCR = 26

    SPECTRAL_1 = 27
    SPECTRAL_2 = 28
    SPECTRAL_3 = 29
    SPECTRAL_4 = 30
    SPECTRAL_5 = 31

    SPECTRAL_ROLLOFF_1 = 32
    SPECTRAL_ROLLOFF_2 = 33
    SPECTRAL_ROLLOFF_3 = 34
    SPECTRAL_ROLLOFF_4 = 35

    SPECTRAL_FLUX = 36
    SPECTRAL_CENTROID = 37
    SPECTRAL_MAX_POS = 38
    SPECTRAL_MIN_POS = 39



    labels = {
        SHOT_CUT_DENSITY: 'shot cut density',

        BRIGHTNESS: 'brightness',

        ENERGY: 'energy',

        MFCC_1: 'MFCC [1]',
        MFCC_2: 'MFCC [2]',
        MFCC_3: 'MFCC [3]',
        MFCC_4: 'MFCC [4]',
        MFCC_5: 'MFCC [5]',
        MFCC_6: 'MFCC [6]',
        MFCC_7: 'MFCC [7]',
        MFCC_8: 'MFCC [8]',
        MFCC_9: 'MFCC [9]',
        MFCC_10: 'MFCC [10]',
        MFCC_11: 'MFCC [11]',
        MFCC_12: 'MFCC [12]',

        PITCH_VOICE_PROB: 'Pitch [Voice prob]',
        PITCH_F0: 'Pitch [F0]',

        LSP_1: 'LSP [1]',
        LSP_2: 'LSP [2]',
        LSP_3: 'LSP [3]',
        LSP_4: 'LSP [4]',
        LSP_5: 'LSP [5]',
        LSP_6: 'LSP [6]',
        LSP_7: 'LSP [7]',

        INTENSITY: 'intensity',
        LOUDNESS: 'loudness',

        MZCR: 'zero crossings',

        SPECTRAL_1: 'spectral [0-250]',
        SPECTRAL_2: 'spectral [0-600]',
        SPECTRAL_3: 'spectral [250-650]',
        SPECTRAL_4: 'spectral [1000-4000]',
        SPECTRAL_5: 'spectral [3010-9123]',

        SPECTRAL_ROLLOFF_1: 'spectral rollof [25.0]',
        SPECTRAL_ROLLOFF_2: 'spectral rollof [50.0]',
        SPECTRAL_ROLLOFF_3: 'spectral rollof [75.0]',
        SPECTRAL_ROLLOFF_4: 'spectral rollof [90.0]',

        SPECTRAL_FLUX: 'spectral flux',
        SPECTRAL_CENTROID: 'spectral centroid',
        SPECTRAL_MAX_POS: 'spectral max pos',
        SPECTRAL_MIN_POS: 'spectral min pos'
    }

    video_features = (SHOT_CUT_DENSITY, BRIGHTNESS, )
    audio_features = (ENERGY, MFCC_1, MFCC_2, MFCC_3, MFCC_4, MFCC_5, MFCC_6, MFCC_7, MFCC_8, MFCC_9, MFCC_10, MFCC_11, MFCC_12, PITCH_VOICE_PROB, PITCH_F0, LSP_1, LSP_2, LSP_3, LSP_4, LSP_5, LSP_6, LSP_7, INTENSITY, LOUDNESS, MZCR, SPECTRAL_1, SPECTRAL_2, SPECTRAL_3, SPECTRAL_4, SPECTRAL_5, SPECTRAL_ROLLOFF_1, SPECTRAL_ROLLOFF_2, SPECTRAL_ROLLOFF_3, SPECTRAL_ROLLOFF_4, SPECTRAL_FLUX, SPECTRAL_CENTROID, SPECTRAL_MAX_POS, SPECTRAL_MIN_POS, )

    functions = {
        SHOT_CUT_DENSITY: (FeatureFunctionType.VALUE, ),

        BRIGHTNESS: (FeatureFunctionType.VALUE, ),

        ENERGY: FeatureFunctionType.standard_audio_functions,

        MFCC_1: FeatureFunctionType.standard_audio_functions,
        MFCC_2: FeatureFunctionType.standard_audio_functions,
        MFCC_3: FeatureFunctionType.standard_audio_functions,
        MFCC_4: FeatureFunctionType.standard_audio_functions,
        MFCC_5: FeatureFunctionType.standard_audio_functions,
        MFCC_6: FeatureFunctionType.standard_audio_functions,
        MFCC_7: FeatureFunctionType.standard_audio_functions,
        MFCC_8: FeatureFunctionType.standard_audio_functions,
        MFCC_9: FeatureFunctionType.standard_audio_functions,
        MFCC_10: FeatureFunctionType.standard_audio_functions,
        MFCC_11: FeatureFunctionType.standard_audio_functions,
        MFCC_12: FeatureFunctionType.standard_audio_functions,

        PITCH_VOICE_PROB: FeatureFunctionType.standard_audio_functions,
        PITCH_F0: FeatureFunctionType.standard_audio_functions,

        LSP_1: FeatureFunctionType.standard_audio_functions,
        LSP_2: FeatureFunctionType.standard_audio_functions,
        LSP_3: FeatureFunctionType.standard_audio_functions,
        LSP_4: FeatureFunctionType.standard_audio_functions,
        LSP_5: FeatureFunctionType.standard_audio_functions,
        LSP_6: FeatureFunctionType.standard_audio_functions,
        LSP_7: FeatureFunctionType.standard_audio_functions,

        INTENSITY: FeatureFunctionType.standard_audio_functions,
        LOUDNESS: FeatureFunctionType.standard_audio_functions,

        MZCR: FeatureFunctionType.standard_audio_functions,

        SPECTRAL_1: FeatureFunctionType.standard_audio_functions,
        SPECTRAL_2: FeatureFunctionType.standard_audio_functions,
        SPECTRAL_3: FeatureFunctionType.standard_audio_functions,
        SPECTRAL_4: FeatureFunctionType.standard_audio_functions,
        SPECTRAL_5: FeatureFunctionType.standard_audio_functions,

        SPECTRAL_ROLLOFF_1: FeatureFunctionType.standard_audio_functions,
        SPECTRAL_ROLLOFF_2: FeatureFunctionType.standard_audio_functions,
        SPECTRAL_ROLLOFF_3: FeatureFunctionType.standard_audio_functions,
        SPECTRAL_ROLLOFF_4: FeatureFunctionType.standard_audio_functions,

        SPECTRAL_FLUX: FeatureFunctionType.standard_audio_functions,
        SPECTRAL_CENTROID: FeatureFunctionType.standard_audio_functions,
        SPECTRAL_MAX_POS: FeatureFunctionType.standard_audio_functions,
        SPECTRAL_MIN_POS: FeatureFunctionType.standard_audio_functions
    }

    fields = {
        ENERGY: 'pcm_RMSenergy_sma',

        MFCC_1: 'mfcc_sma[1]',
        MFCC_2: 'mfcc_sma[2]',
        MFCC_3: 'mfcc_sma[3]',
        MFCC_4: 'mfcc_sma[4]',
        MFCC_5: 'mfcc_sma[5]',
        MFCC_6: 'mfcc_sma[6]',
        MFCC_7: 'mfcc_sma[7]',
        MFCC_8: 'mfcc_sma[8]',
        MFCC_9: 'mfcc_sma[9]',
        MFCC_10: 'mfcc_sma[10]',
        MFCC_11: 'mfcc_sma[11]',
        MFCC_12: 'mfcc_sma[12]',

        PITCH_VOICE_PROB: 'voiceProb_sma',
        PITCH_F0: 'F0_sma',

        LSP_1: 'lspFreq_sma[1]',
        LSP_2: 'lspFreq_sma[2]',
        LSP_3: 'lspFreq_sma[3]',
        LSP_4: 'lspFreq_sma[4]',
        LSP_5: 'lspFreq_sma[5]',
        LSP_6: 'lspFreq_sma[6]',
        LSP_7: 'lspFreq_sma[7]',

        INTENSITY: 'pcm_intensity_sma',
        LOUDNESS: 'pcm_loudness_sma',

        MZCR: 'pcm_zcr_sma',

        SPECTRAL_1: 'pcm_Mag_fband0-250_sma',
        SPECTRAL_2: 'pcm_Mag_fband0-650_sma',
        SPECTRAL_3: 'pcm_Mag_fband250-650_sma',
        SPECTRAL_4: 'pcm_Mag_fband1000-4000_sma',
        SPECTRAL_5: 'pcm_Mag_fband3010-9123_sma',

        SPECTRAL_ROLLOFF_1: 'pcm_Mag_spectralRollOff25.0_sma',
        SPECTRAL_ROLLOFF_2: 'pcm_Mag_spectralRollOff50.0_sma',
        SPECTRAL_ROLLOFF_3: 'pcm_Mag_spectralRollOff75.0_sma',
        SPECTRAL_ROLLOFF_4: 'pcm_Mag_spectralRollOff90.0_sma',

        SPECTRAL_FLUX: 'pcm_Mag_spectralFlux_sma',
        SPECTRAL_CENTROID: 'pcm_Mag_spectralCentroid_sma',
        SPECTRAL_MAX_POS: 'pcm_Mag_spectralMaxPos_sma',
        SPECTRAL_MIN_POS: 'pcm_Mag_spectralMinPos_sma',
    }


class ComputingStateType(BetterEnum):
    NO = 0
    IN_PROGRESS = 1
    SUCCESS = 2
    FAILED = 3
    WARNING = 4

    labels = {
        NO: 'no',
        IN_PROGRESS: 'in progress',
        SUCCESS: 'success',
        FAILED: 'failed',
        WARNING: 'warning'
    }

class EmotionType(BetterEnum):
    NEUTRAL = 0
    ANGER = 1
    DISGUST = 2
    FEAR = 3
    HAPPINESS = 4
    SADNESS = 5
    SURPRISE = 6
    TENDERNESS = 7
    AMUSEMENT = 8

    labels = {
        NEUTRAL: 'neutral',
        ANGER: 'anger',
        DISGUST: 'disgust',
        FEAR: 'fear',
        HAPPINESS: 'happiness',
        SADNESS: 'sadness',
        SURPRISE: 'surprise',
        TENDERNESS: 'tenderness',
        AMUSEMENT: 'amusement'
    }

    ekman_emotions = (NEUTRAL, ANGER, DISGUST, FEAR, HAPPINESS, SADNESS, SURPRISE, )
    schaefer_emotions = (AMUSEMENT, TENDERNESS, )

    basic_emotions = {
        "ekman": ekman_emotions,
        "schaefer": schaefer_emotions
    }