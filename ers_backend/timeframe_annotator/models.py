from django.db import models
from django_enumfield import enum
from dataset_manager.models import Video
from timeframe_annotator.enums import TimeframeAnnotationType


class TimeframeAnnotation(models.Model):
    """
    Model representing a time frame annotation.
    """
    video = models.ForeignKey(Video, related_name='timeframe_annotations')

    start_frame = models.PositiveIntegerField(default=0)
    end_frame = models.PositiveIntegerField(default=0)
    annotation = enum.EnumField(TimeframeAnnotationType, default=TimeframeAnnotationType.NONE)