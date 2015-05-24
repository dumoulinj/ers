# import logging
#
# from socketio.namespace import BaseNamespace
# from socketio.mixins import RoomsMixin, BroadcastMixin
# from socketio.sdjango import namespace
# import time
# from models import Dataset,Video
# from multiprocessing import Pool
# from threading import Thread
# from enums import Compute_state
# from video_processor.models import ShotsDetection,ECR,VideoShotsResult,VideoFrame
#
# def evaluate(self,shotDetection,video):
#     for x in shotDetection:
#         x.evaluate(video)
#     self.broadcast_event('endEval')
#
# # Prepare videos
# def pre_vids(self,videos,dataset,update,overwrite,overwrite_audio,algos):
#         nbstep = len(videos)
#         nbdone = 0
#         print(self)
#         self.broadcast_event('progress bar',{"nbstep":nbstep,"nbdone":nbdone})
#         for video in videos:
#             video.prepare_state = Compute_state.IN_PROGRESS
#             video.save()
#             self.broadcast_event('refresh',{"id":video.id})
#             dataset.prepare_video(video,update=update, overwrite_converted=overwrite, overwrite_audio=overwrite_audio)
#             self.broadcast_event('refresh',{"id":video.id})
#             nbdone+=1
#             self.broadcast_event('progress bar',{"nbstep":nbstep,"nbdone":nbdone})
#         self.broadcast_event('end')
#
# # Shot videos, evaluate and take thumbnails
# def shot_vids(self,videos,dataset,update,overwrite,overwrite_audio,algos):
#         shots_detection = ShotsDetection()
#         shots_detection.save()
#         shots_detection.setAlgos(algos)
#
#         nbstep = len(videos)
#         nbdone = 0
#         print(self)
#         self.broadcast_event('progress bar',{"nbstep":nbstep,"nbdone":nbdone})
#         for video in videos:
#             video.shot_state = Compute_state.IN_PROGRESS
#             video.save()
#             self.broadcast_event('refresh',{"id":video.id})
#
#             shots_detection.detect(video)
#             nbdone+=1
#
#             if(video.shot_boundaries_ground_truth != []):
#                 shots_detection.evaluate(video)
#             shots_detection.take_thumbnails(video)
#             self.broadcast_event('refresh',{"id":video.id})
#             self.broadcast_event('progress bar',{"nbstep":nbstep,"nbdone":nbdone})
#         self.broadcast_event('end')
#
# # Create the features
# def feature_vids(self,videos,dataset,update,overwrite,overwrite_audio,algos):
#     nbstep = len(videos)
#     nbdone = 0
#     print(self)
#     self.broadcast_event('progress bar',{"nbstep":nbstep,"nbdone":nbdone})
#     for video in videos:
#         video.features_state = Compute_state.IN_PROGRESS
#         video.save()
#         self.broadcast_event('refresh',{"id":video.id})
#         dataset.compute_features(video,overwrite)
#         self.broadcast_event('refresh',{"id":video.id})
#         nbdone+=1
#         self.broadcast_event('progress bar',{"nbstep":nbstep,"nbdone":nbdone})
#     self.broadcast_event('end')
#
# # Create the arousal
# def arousal_vids(self,videos,dataset,update,overwrite,overwrite_audio,algos,window_len=1000,wsize=10,wstep=3,crest_intensity_threshold=0.1,beta=8):
#     nbstep = len(videos)
#     nbdone = 0
#     # print(self)
#     self.broadcast_event('progress bar',{"nbstep":nbstep,"nbdone":nbdone})
#     for video in videos:
#         video.arousal_state = Compute_state.IN_PROGRESS
#         video.save()
#         self.broadcast_event('refresh',{"id":video.id})
#         dataset.model_arousal(video,overwrite,window_len,wsize,wstep,crest_intensity_threshold,beta)
#         self.broadcast_event('refresh',{"id":video.id})
#         nbdone+=1
#         self.broadcast_event('progress bar',{"nbstep":nbstep,"nbdone":nbdone})
#         self.broadcast_event('update arousal',{})
#     self.broadcast_event('end')
#
# # Prepare, shot, features and arousal the video
# def all_vids(self,videos,dataset,update,overwrite,overwrite_audio,algos):
#     # Prepare shot detection
#     shots_detection = ShotsDetection()
#     shots_detection.save()
#     shots_detection.setAlgos(algos)
#
#     dataset.prepare()
#     nbvid = len(videos)
#     nbstep = nbvid*4
#     nbdone = 0
#     print(self)
#     self.broadcast_event('progress bar',{"nbstep":nbstep,"nbdone":nbdone})
#     for video in videos:
#         video.prepare_state = Compute_state.IN_PROGRESS
#         video.save()
#         self.broadcast_event('refresh',{"id":video.id})
#
#         dataset.prepare_video(video,update=update, overwrite_converted=overwrite, overwrite_audio=overwrite_audio)
#         self.broadcast_event('refresh',{"id":video.id})
#         nbdone+=1
#         self.broadcast_event('progress bar',{"nbstep":nbstep,"nbdone":nbdone})
#         video.shot_state = Compute_state.IN_PROGRESS
#         video.save()
#         shots_detection.detect(video)
#         if(video.shot_boundaries_ground_truth != []):
#                 shots_detection.evaluate(video)
#         shots_detection.take_thumbnails(video)
#         nbdone+=1
#         self.broadcast_event('progress bar',{"nbstep":nbstep,"nbdone":nbdone})
#         self.broadcast_event('refresh',{"id":video.id})
#         video.features_state = Compute_state.IN_PROGRESS
#         video.save()
#
#         dataset.compute_features(video,overwrite)
#         nbdone+=1
#         self.broadcast_event('progress bar',{"nbstep":nbstep,"nbdone":nbdone})
#         self.broadcast_event('refresh',{"id":video.id})
#         video.arousal_state = Compute_state.IN_PROGRESS
#         video.save()
#
#         dataset.model_arousal(video,overwrite)
#         nbdone+=1
#         self.broadcast_event('progress bar',{"nbstep":nbstep,"nbdone":nbdone})
#         self.broadcast_event('refresh',{"id":video.id})
#     self.broadcast_event('end')
#
# @namespace('/videoprocessorsocket')
# class VideoProcessorSocketNamespace(BaseNamespace, RoomsMixin, BroadcastMixin):
#     def initialize(self):
#         self.logger = logging.getLogger("videoprocessorsocket")
#         self.log("Socketio session on videoprocessorsocket started")
#
#     def log(self, message):
#         self.logger.info("[{0}] {1}".format(self.socket.sessid, message))
#
#     # def on_shot_dataset(self,params):
#     #
#     #     algos = params['algos']
#     #     name = params['name']
#     #     base_path = params['base_path']
#     #     videos = []
#     #
#     #     dataset = Dataset.objects.get(name=name, base_path=base_path)
#     #     for video in dataset.videos.all():
#     #         videos.append(video)
#     #     t = Thread(target=shot_vids,args=(self,videos,dataset,algos))
#     #     t.start()
#     #     self.log(params)
#     #     return True
#     #
#     #
#     # def on_shot_video(self,params):
#     #     self.log(params)
#     #     algos = params['algos']
#     #
#     #     for x in algos:
#     #         self.log(x['key'])
#     #         self.log(x['value'])
#     #     videos = []
#     #     video = Video.objects.get(id=params['id'])
#     #     name = params['name']
#     #     base_path = params['base_path']
#     #     dataset = Dataset.objects.get(name=name, base_path=base_path)
#     #     videos.append(video)
#     #     t = Thread(target=shot_vids,args=(self,videos,dataset,algos))
#     #     t.start()
#     #     self.log(params)
#     #     return True
#     #
#     def on_evaluate_video(self,params):
#         video = params['video']
#         video = Video.objects.get(id=video['id'])
#         res = VideoShotsResult.objects.filter(video=video)
#         shots = []
#         for x in res:
#             shots.append(x.shots_detection)
#         t = Thread(target=evaluate ,args=(self,shots,video))
#         t.start()
#         return True
#
# @namespace('/datasetsocket')
# class DatasetNamespace(BaseNamespace, RoomsMixin, BroadcastMixin):
#     def initialize(self):
#         self.logger = logging.getLogger("datasetsocket")
#         self.log("Socketio session on datasetsocket started")
#
#     def log(self, message):
#         self.logger.info("[{0}] {1}".format(self.socket.sessid, message))
#
#     # def on_prepare_dataset(self,params):
#     #     self.log("prepare_dataset")
#     #     self.log("Nom {0} Path: {1}".format(params['name'],params['base_path']))
#     #     name = params['name']
#     #     base_path = params['base_path']
#     #     overwrite = params['overwrite']
#     #     overwrite_audio = params['overwrite_audio']
#     #     update = params['update']
#     #     dataset, created = Dataset.objects.get_or_create(name=name, base_path=base_path)
#     #     self.log(dataset.base_path)
#     #     self.log(dataset.audio_path)
#     #     self.log(dataset.video_path)
#     #     videos = dataset.prepare()
#     #     self.log("videos number {0}".format(len(videos)))
#     #     videos = []
#     #     for vid in dataset.videos.all():
#     #         videos.append(vid)
#     #     t = Thread(target=pre_vids,args=(self,videos,dataset,update,overwrite,overwrite_audio))
#     #     t.start()
#     #     self.log("Videos name's")
#     #     self.log(dataset.videos_name_in_folder)
#     #     self.log(params)
#     #     return True
#
#     def on_get_videos_in_dataset(self,params):
#         name = params['name']
#         dataset = Dataset.objects.get(name=name)
#         videos = dataset.video_list
#         for vid in videos:
#             dataset.create_video(vid)
#         self.broadcast_event('list videos',{})
#         return True
#
#     # def on_prepare_video(self,params):
#     #     self.log(params)
#     #     videos = []
#     #     video = Video.objects.get(id=params['id'])
#     #     name = params['name']
#     #     base_path = params['base_path']
#     #     overwrite = params['overwrite']
#     #     overwrite_audio = params['overwrite_audio']
#     #     update = params['update']
#     #     dataset = Dataset.objects.get(name=name, base_path=base_path)
#     #     videos.append(video)
#     #     t = Thread(target=pre_vids,args=(self,videos,dataset,update,overwrite,overwrite_audio))
#     #     t.start()
#     #     self.log(params)
#     #     return True
#
#     # def on_feature_video(self,params):
#     #     self.log(params)
#     #     videos = []
#     #     video = Video.objects.get(id=params['id'])
#     #     name = params['name']
#     #     base_path = params['base_path']
#     #     overwrite = params['overwrite']
#     #     dataset = Dataset.objects.get(name=name, base_path=base_path)
#     #     videos.append(video)
#     #     t = Thread(target=feature_vids,args=(self,videos,dataset,overwrite))
#     #     t.start()
#     #     self.log(params)
#     #     return True
#     #
#     # def on_feature_dataset(self,params):
#     #     name = params['name']
#     #     base_path = params['base_path']
#     #     overwrite = params['overwrite']
#     #     videos = []
#     #
#     #     dataset = Dataset.objects.get(name=name, base_path=base_path)
#     #
#     #     for video in dataset.videos.all():
#     #         videos.append(video)
#     #
#     #     t = Thread(target=feature_vids,args=(self,videos,dataset,overwrite))
#     #     t.start()
#     #     self.log(params)
#     #     return True
#
#     def on_arousal_video(self,params):
#         self.log(params)
#         videos = []
#         video = Video.objects.get(id=params['id'])
#         name = params['name']
#         base_path = params['base_path']
#         overwrite = params['overwrite']
#         algos = ""
#         overwrite_audio = ""
#         update = ""
#         dataset = Dataset.objects.get(name=name, base_path=base_path)
#         videos.append(video)
#         try:
#             window_len = int(params['windowlen'])
#             wsize = int(params['wsize'])
#             wstep = int(params['wstep'])
#             crest_intensity_threshold = float(params['crest_intensity_threshold'])
#             beta = int(params['beta'])
#             t = Thread(target=arousal_vids,args=(self,videos,dataset,update,overwrite,overwrite_audio,algos,window_len,wsize,wstep,crest_intensity_threshold,beta))
#         except:
#             t = Thread(target=arousal_vids,args=(self,videos,dataset,update,overwrite,overwrite_audio,algos))
#
#         t.start()
#         self.log(params)
#         return True
#     #
#     # def on_arousal_dataset(self,params):
#     #     name = params['name']
#     #     base_path = params['base_path']
#     #     videos = []
#     #     overwrite = params['overwrite']
#     #     dataset = Dataset.objects.get(name=name, base_path=base_path)
#     #
#     #
#     #     for video in dataset.videos.all():
#     #         videos.append(video)
#     #
#     #     t = Thread(target=arousal_vids,args=(self,videos,dataset,overwrite))
#     #     t.start()
#     #     # self.log(params)
#     #     return True
#
#     #
#     # def on_all_video(self,params):
#     #     self.log(params)
#     #     videos = []
#     #     video = Video.objects.get(id=params['id'])
#     #     algos = params['algos']
#     #     name = params['name']
#     #     base_path = params['base_path']
#     #     overwrite = params['overwrite']
#     #     overwrite_audio = params['overwrite_audio']
#     #     update = params['update']
#     #     dataset = Dataset.objects.get(name=name, base_path=base_path)
#     #     videos.append(video)
#     #     t = Thread(target=all_vids,args=(self,videos,dataset,update,overwrite,overwrite_audio,algos))
#     #     t.start()
#     #     return True
#     #
#     # def on_all_dataset(self,params):
#     #     name = params['name']
#     #     base_path = params['base_path']
#     #     videos = []
#     #     overwrite = params['overwrite']
#     #     overwrite_audio = params['overwrite_audio']
#     #     update = params['update']
#     #     algos = params['algos']
#     #     dataset = Dataset.objects.get(name=name, base_path=base_path)
#     #
#     #
#     #
#     #     for video in dataset.videos.all():
#     #         videos.append(video)
#     #
#     #     t = Thread(target=all_vids,args=(self,videos,dataset,update,overwrite,overwrite_audio,algos))
#     #     t.start()
#     #     self.log(params)
#     #     return True
#
#     def on_do_this(self,params):
#         self.log(params)
#         videos = []
#
#         algos = params['algos']
#         name = params['name']
#         base_path = params['base_path']
#         overwrite = params['overwrite']
#         overwrite_audio = params['overwrite_audio']
#         update = params['update']
#         dataset = Dataset.objects.get(name=name, base_path=base_path)
#         if(params['id'] == -1):
#             for video in dataset.videos.all():
#                 videos.append(video)
#         else:
#             video = Video.objects.get(id=params['id'])
#             videos.append(video)
#         t = Thread(target=eval(params['function']),args=(self,videos,dataset,update,overwrite,overwrite_audio,algos))
#         t.start()
#         return True