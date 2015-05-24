from django_enumfield import enum

class TimeframeAnnotationType(enum.Enum):
    NONE = 0
    POSITIVE = 1
    NEGATIVE = 2

    labels = {
        NONE: "None",
        POSITIVE: "Positive",
        NEGATIVE: "Negative"
    }
