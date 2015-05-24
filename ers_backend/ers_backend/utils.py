import logging
import os
from converter import Converter
from converter.ffmpeg import FFMpeg, FFMpegConvertError
from django.conf import settings

#ffmpeg_cmd = "/opt/local/bin/ffmpeg"
from dataset_manager.enums import EmotionType, ComputingStateType

logger = logging.getLogger(__name__)

def mkdir_if_not_exists(path):
    """
    Create a directory if it does not already exists.
    :param path: Directory path
    :return: Return True if the folder exists or has been correctly created, False if there is a problem.
    """
    try:
        if not os.path.exists(path):
            os.makedirs(path)

        return True
    except:
        pass

    return False


def is_emotion_dir(path):
    """
    Check if the given path is an emotion class folder
    :param path: The path to check
    :return: True if the folder is an emotion class
    """
    return os.path.isdir(path) and EmotionType.is_an_enum(os.path.basename(path))


def is_video(path):
    """
    Check if the given filepath is a video, regarding a list of valid extensions.
    """
    if not os.path.isdir(path) and path.endswith(settings.VIDEO_EXTENSIONS):
        return True
    else:
        return False

def convert_video_2_mp4(filepath_in, filepath_out):
    """
    Convert a video in mp4 format, with aac sound.
    (need to install ffmpeg this way: 'sudo port install ffmpeg +nonfree' in order to libfaac to work)
    """

    # cmd = '{} -i "{}" -filter:v scale=640:360,setsar=1/1 -pix_fmt yuv420p -c:v libx264 -preset:v \
    #     slow -profile:v baseline -x264opts level=3.0:ref=1 -b:v 700k -r:v 25/1 -force_fps -movflags +faststart -c:a \
    #     libfaac -b:a 80k "{}"'.format(ffmpeg_cmd filepath_in, filepath_out)
    # os.system(cmd)

    conv = Converter().convert(filepath_in, filepath_out, {
        'format': 'mp4',
        'audio': {'codec': 'aac'},
        'video': {'codec': 'h264'}
    }, timeout=None)

    try:
        for timecode in conv:
            print ".",

        return ComputingStateType.SUCCESS
    except FFMpegConvertError:
        logger.warning("Control that video %s has correctly been converted.", filepath_out)
        return ComputingStateType.WARNING
    except:
        logger.warning("Problem when converting video: %s", filepath_out)
        return ComputingStateType.FAILED



def convert_video_2_webm(filepath_in, filepath_out):
    """
    Convert a video to webm format.
    """

    # cmd = '{} {} -i "{}" -filter:v scale=640:360,setsar=1/1 -pix_fmt yuv420p -vpre libvpx-720p -b:v 500k -r:v 25/1 -force_fps -c:a libvorbis -b:a 80k "{}"'.format(ffmpeg_cmd, auto_overwrite, filepath_in, filepath_out)
    # os.system(cmd)

    conv = Converter().convert(filepath_in, filepath_out, {
        'format': 'webm',
        'audio': {'codec': 'vorbis'},
        'video': {'codec': 'vp8'}
    }, timeout=None)

    try:
        for timecode in conv:
            print ".",
        return ComputingStateType.SUCCESS
    except FFMpegConvertError:
        logger.warning("Control that video %s has correctly been converted.", filepath_out)
        return ComputingStateType.WARNING
    except:
        logger.warning("Problem when converting video: %s", filepath_out)
        return ComputingStateType.FAILED

    #shutil.move(filepath_temp,filepath_out)

def extract_wav_from_video(filepath_in, filepath_out):
    """
    Extract wav from video to allow processing with OpenCV/OpenSmile.
    """
    warning = False

    filepath_out_temp = "{}.temp.wav".format(filepath_out)

    # Extract wav with ffmpeg
    # cmd = '{} -i "{}" "{}"'.format(ffmpeg_cmd, filepath_in, filepath_out_temp)
    # os.system(cmd)

    conv = FFMpeg().convert(filepath_in, filepath_out_temp, [], timeout=None)

    try:
        for timecode in conv:
            print ".",
    except FFMpegConvertError:
        logger.warning("Control that audio %s has correctly been extracted.", filepath_out)
        warning = True
    except:
        logger.warning("Problem when extracting audio: %s", filepath_out)
        return ComputingStateType.FAILED

    try:
        # Convert wav file to be readable from OpenSmile
        #sox_cmd = "/opt/local/bin/sox"
        sox_cmd = os.popen("which sox").read().split('\n')[0]
        cmd = '{} "{}" -c 1 -b 16 -e signed-integer "{}"'.format(sox_cmd, filepath_out_temp, filepath_out)
        os.system(cmd)
    except:
        return ComputingStateType.FAILED

    try:
        # Remove temp file
        os.remove(filepath_out_temp)
    except:
        warning = True

    if warning:
        return ComputingStateType.WARNING
    else:
        return ComputingStateType.SUCCESS


def replace_right(source, target, replacement, replacements=1):
    """
    Replace the last occurence of a string.
    :param source:
    :param target:
    :param replacement:
    :param replacements:
    :return:
    """
    return replacement.join(source.rsplit(target, replacements))
