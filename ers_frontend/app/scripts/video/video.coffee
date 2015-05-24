frame2seconds = (frameNb, fps) ->
	frameNb * 1 / fps

seconds2frame = (seconds, fps) ->
	seconds * fps

angular
	.module 'app.video', []
	.config ($stateProvider) ->
		$stateProvider
			.state 'video', {
				url: '/video/{videoId:[0-9]+}',
				templateUrl: '/partials/video.html',
				controller: 'VideoCtrl',
				resolve: {
					video: ($stateParams, VideosResource) ->
						VideosResource.one($stateParams.videoId).get()

					dataset: (video, Restangular) ->
						Restangular.oneUrl('dataset', video.dataset).get()

					videoSources: (video, dataset) ->
						if(!!window.chrome)
							[
								{src: "datasets/" + dataset.id + "/videos/" + video.name + ".webm", type: "video/webm"},
							]
						else
							[
								{src: "datasets/" + dataset.id + "/videos/" + video.name + ".mp4", type: "video/mp4"},
								{src: "datasets/" + dataset.id + "/videos/" + video.name + ".webm", type: "video/webm"},
							]

					videoPart: (video, Restangular) ->
						Restangular.oneUrl('videoPart', video.video_part).get()

					audioPart: (video, Restangular) ->
						Restangular.oneUrl('audioPart', video.audio_part).get()

					emotions: (Restangular) ->
						Restangular.one('dataset_manager/emotions').get().then((emotions) ->
							emotions.plain()
						)
				}
			}
			.state 'video.info', {
				url: '/info',
				templateUrl: '/partials/video.info.html',
				controller: 'InfoCtrl'
			}
			.state 'video.sbd', {
				url: '/sbd',
				templateUrl: '/partials/video.sbd.html',
				controller: 'SbdCtrl',
				resolve: {
					sbdResults: (video, Restangular) ->
						sbdResults = []

						_.forEach(video.shots_detections, (shotsUrl)->
							sbdResult = Restangular.oneUrl('video_shots_results', shotsUrl).get().then((sbdResult)->
								sbdResults.push(sbdResult)
							)
						)
						sbdResults
				}
			}
			.state 'video.sbd.detail', {
				url: '/{sbdResultId:-1|[0-9]+}?removed',
				templateUrl: '/partials/video.sbd-detail.html',
				controller: 'SbdDetailCtrl',
				resolve:{
					sbdResult:(Restangular, $stateParams)->
						Restangular.one('video_processor/video_shots_results', $stateParams.sbdResultId).get()

#					thumbnails:(Restangular,shot,video, dataset)->
#						thumbnails = []
#						shotD = Restangular.oneUrl('shots_detections',shot.shots_detection).get().then((shotD)->
#							shot.shots.forEach((shot_s) ->
#								z = "datasets/" + dataset.id + "/videos/shots/video_" + video.id + "/shot_result_" + shotD.id+ "/shot_" + shot_s.id
#								thumbnails.push({"src": "datasets/" + dataset.id + "/videos/shots/video_" + video.id + "/shot_result_"+ shotD.id + "/shot_" + shot_s.id})
#							)
#							thumbnails
#						)
				}
			}
			.state 'video.features', {
				url: '/features',
				templateUrl: '/partials/video.features.html',
				controller: 'FeaturesCtrl',
				resolve:{
					featureTypes: (Restangular) ->
						Restangular.one('dataset_manager/feature_types').get().then((emotions) ->
							emotions.plain()
						)

					featureFunctionTypes: (Restangular) ->
						Restangular.one('dataset_manager/feature_function_types').get().then((feature_function_types) ->
							feature_function_types.plain()
						)
				}
			}
			.state 'video.arousalcurve', {
				url: '/arousalcurve',
				templateUrl: '/partials/video.arousalcurve.html',
				controller: 'ArousalCtrl',
				resolve: {
					arousal: (video, Restangular) ->
						Restangular.oneUrl('arousal_modeler', video.arousal).get()

					featureTypes: (Restangular) ->
						Restangular.one('dataset_manager/feature_types').get().then((emotions) ->
							emotions.plain()
						)

					featureFunctionTypes: (Restangular) ->
						Restangular.one('dataset_manager/feature_function_types').get().then((feature_function_types) ->
							feature_function_types.plain()
						)
				}
			}

	.controller 'InfoCtrl', ($scope) ->
		$scope.$parent.displayVideo = true

	.controller 'VideoCtrl', ($scope, $timeout, video, dataset, videoPart, audioPart, videoSources, emotions) ->
		# Initialize tooltips on buttons
		$timeout(() ->
			$('[data-toggle="tooltip"]').tooltip()
		, 500)

		$scope.video = video
		$scope.dataset = dataset
		$scope.videoSources = videoSources

		$scope.video.video_part = videoPart
		$scope.video.audio_part = audioPart
		$scope.displayVideo = false
		$scope.crtTime = 0

		# Emotions
		$scope.emotions = emotions

		$scope.getters = {
			emotion: (value) ->
				_.result(_.find(emotions, {'value': value}), 'label')
		}

		$scope.API = null

		$scope.onVideoPlayerReady = (API) ->
			$scope.videoAPI = API

		$scope.onUpdateTime = (currentTime, totalTime) ->
			$scope.crtTime = currentTime
			$scope.totalTime = totalTime

		$scope.videoConfig = {
			autoHide: true,
			autoHideTime: 1000,
			autoPlay: false,
			responsive: true,
			stretch: "fill"
		}

