import os
import shutil
from django.db.models.signals import post_save, post_delete
from django.dispatch.dispatcher import receiver
from dataset_manager.models import Dataset, Video


@receiver(post_save, sender=Dataset)
def dataset_post_save(sender, **kwargs):
    """
    Used to prepare directories after a dataset is newly created.
    """
    created = kwargs['created']
    instance = kwargs['instance']

    if created:
        instance.prepare()

@receiver(post_delete, sender=Dataset)
def dataset_post_delete(sender, instance, **kwargs):
    path = instance.base_path

    try:
        shutil.rmtree(path)
    except:
        pass


@receiver(post_delete, sender=Video)
def video_post_delete(sender, instance, **kwargs):
    paths = [instance.path, instance.original_path, instance.audio_path]
    for path in paths:
        try:
            os.remove(path)
        except:
            pass