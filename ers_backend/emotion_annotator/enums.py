from django_enumfield import enum

class EmotionType(enum.Enum):
    ANGER = 0
    DISGUST = 1
    FEAR = 2
    SURPRISE = 3
    HAPPINESS = 4
    SADNESS = 5
    NEUTRAL = 6

    labels = {
        ANGER: 'Anger',
        DISGUST: 'Disgust',
        FEAR: 'Fear',
        SURPRISE: 'Surprise',
        HAPPINESS: 'Happiness',
        SADNESS: 'Sadness',
        NEUTRAL: 'Neutral'
    }
