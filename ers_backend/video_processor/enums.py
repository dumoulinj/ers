from django_enumfield import enum

class ShotBoundariesDetectionAlgorithmType(enum.Enum):
    COLOR_HISTOGRAM = 0
    ECR = 1
    NONE = 2

    labels = {
        COLOR_HISTOGRAM: "color histograms",
        ECR: "edge change ration",
        NONE: "none"
    }

class ShotBoundaryType(enum.Enum):
    NONE = 0
    TRUE_POSITIVE = 1
    FALSE_POSITIVE = 2
    MISS = 3

    labels = {
        NONE: "none",
        TRUE_POSITIVE: "true positive",
        FALSE_POSITIVE: "false positive",
        MISS: "miss"
    }
