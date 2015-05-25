'use strict'

# app.datasets Module
#
# @abstract Datasets controllers

angular
	.module 'app.datasets', []
	.config ($stateProvider, $urlRouterProvider) ->
		$stateProvider
			.state 'datasets', {
				url: '/datasets',
				templateUrl: '/partials/dataset.html'
			}
			.state 'datasets.list', {
				url: '/list?removed',
				templateUrl: '/partials/dataset.list.html',
				controller: 'DatasetsCtrl',
			}
			.state 'datasets.detail', {
				url: '/{datasetId:-1|[0-9]+}?created',
				templateUrl: '/partials/dataset.detail.html',
				controller: 'DatasetCtrl',
				resolve:{
					algorithms: (Restangular) ->
						Restangular.one('video_processor/sbd_algorithms').get().then((algorithms) ->
							algorithms.plain()
						)

					emotions: (Restangular) ->
						Restangular.one('dataset_manager/emotions').get().then((emotions) ->
							emotions.plain()
						)

					featureTypes: (Restangular) ->
						Restangular.one('dataset_manager/feature_types').get().then((feature_types) ->
							feature_types.plain()
						)

				}
			}
	.controller 'DatasetsCtrl', ['$scope', '$dragon', 'DatasetsResource', '$state', '$stateParams', '$alert', '$timeout', ($scope, $dragon, DatasetsResource, $state, $stateParams, $alert, $timeout) ->

		# Retrieve datasets list
#		$scope.datasets = DatasetsResource.getList().$object
		$dragon.onReady(() ->
			$dragon.getList('dataset').then((response) ->
				$scope.datasets = response.data
			)
		)

		# Initialize tooltips on buttons
		$timeout(() ->
			$('[data-toggle="tooltip"]').tooltip()
		, 500)

		# Growl if removed
		if $stateParams.removed
			$alert({
				title: 'Confirmation',
				content: 'Dataset successfully removed!',
				placement: 'top-right',
				type: 'success',
				duration: 4,
				show: true
			})	
	]
	.controller 'DatasetCtrl', ['$scope', '$dragon', 'DatasetsResource', 'Restangular','$state', '$stateParams', '$modal', '$alert', '$timeout', '$filter', 'algorithms', 'emotions', 'featureTypes', '$cookieStore', 'FileUploader', 'ComputingStateType', ($scope, $dragon, DatasetsResource, Restangular, $state, $stateParams, $modal, $alert, $timeout, $filter, algorithms, emotions, featureTypes, $cookieStore, FileUploader, ComputingStateType) ->
		# Initialize tooltips on buttons
		$timeout(() ->
			$('[data-toggle="tooltip"]').tooltip()
		, 1000)

		$scope.backTo = "datasets.list"
		$scope.additionalPathsActivePanels = []
		$scope.featuresSelectionActivePanels = [0, 1]
		$scope.arousalFeaturesSelectionActivePanels = [0, 1]

		# Dataset
		$scope.dataset = {}
		$scope.datasetId = $stateParams.datasetId
		$scope.dataset.name = ""
		$scope.dataset.description = ""
		$scope.dataset.nb_videos = 0
		$scope.tempDataset = {}

		# Videos
		$scope.videos = []

		# Emotions
		$scope.emotions = emotions

		# Features
		$scope.featureTypes = featureTypes
		$scope.audioFeatureTypes = _.filter(featureTypes, (feature_type) -> feature_type.type == 'audio')
		$scope.videoFeatureTypes = _.filter(featureTypes, (feature_type) -> feature_type.type == 'video')

		$scope.arousalAudioFeatureTypes = []
		$scope.arousalVideoFeatureTypes = []

		$scope.selectedFeatures = {
			audio: [],
			video: []
		}

		$scope.arousalSelectedFeatures = {
			audio: [],
			video: []
		}

		$scope.checkAllFeatures = (type, tab) ->
			if type == 'audio'
				if tab == 'features'
					$scope.selectedFeatures.audio = $scope.audioFeatureTypes.map((item) -> item.value)
				else if tab == 'arousal'
					temp = _.filter($scope.audioFeatureTypes, (item) ->
						item.value in $scope.dataset.available_features
					)
					$scope.arousalSelectedFeatures.audio = temp.map((item) ->
						item.value
					)
			else if type == 'video'
				if tab == 'features'
					$scope.selectedFeatures.video = $scope.videoFeatureTypes.map((item) -> item.value)
				else if tab == 'arousal'
					temp = _.filter($scope.videoFeatureTypes, (item) ->
						item.value in $scope.dataset.available_features
					)
					$scope.arousalSelectedFeatures.video = temp.map((item) ->
						item.value
					)

		$scope.uncheckAllFeatures = (type, tab) ->
			if type == 'audio'
				if tab == 'features'
					$scope.selectedFeatures.audio = []
				else if tab == 'arousal'
					$scope.arousalSelectedFeatures.audio = []
			else if type == 'video'
				if tab == 'features'
					$scope.selectedFeatures.video = []
				else if tab == 'arousal'
					$scope.arousalSelectedFeatures.video = []

		# Mode
		$scope.createMode = false
		$scope.editMode = false

		# Management
		$scope.manageTabs = {}
		$scope.manageTabs.activeTab = 0

		# Shot boundaries detection : Algos configuration
		$scope.sbd = {}
		$scope.sbd.algorithms = algorithms
		$scope.sbd.algorithm = {}
		$scope.sbd.algorithm.value
		$scope.sbd.algorithm.label
		$scope.sbd.weight = 1
		$scope.sbd.configuration = (if $cookieStore.get('sbd.configuration') then $cookieStore.get('sbd.configuration') else [{"value": 0, "label": "edge change ratio", "threshold": 0.7, "weight": 1}] )
		$scope.sbd.globalThreshold = (if $cookieStore.get('sbd.globalThreshold') then $cookieStore.get('sbd.globalThreshold') else 0.7 )

		# Monitoring
		$scope.nb_videos = $scope.dataset.nb_videos

		# TODO: rename
		$scope.currentval = 0
		$scope.maxval = 0
		$scope.isDefault = true

		$scope.indexColumn = -1

		# Ready for tasks
		$scope.readyForVideosPreparation = true
		$scope.readyForShotBoundariesDetection = false
		$scope.readyForFeatureExtraction = false
		$scope.readyForArousalModeling = false


		# Return true if the dataset has 1 or more videos
		$scope.hasVideos = () ->
			$scope.dataset.nb_videos > 0

		$scope.getters = {
			emotion: (value) ->
				_.result(_.find(emotions, {'value': value}), 'label')
		}

		# Clear filters for the video table
		$scope.clearFilters = () ->
			if $scope.filterBy != undefined
				$scope.filterBy.name = ""
				$scope.filterBy.emotion = undefined

		## Swampdragon
		$scope.datasetChannel = 'datasetChannel'
		$scope.videosChannel = 'videosChannel'

		$scope.getDataset = () ->
			$dragon.getSingle('dataset', {id:$scope.datasetId}).then((response) ->
				$scope.dataset = response.data
				$scope.getVideos()
			)

		$scope.getVideos = () ->
			$dragon.getList('video', {dataset_id:$scope.datasetId}).then((response) ->
				$scope.videos = response.data
				if _.size($scope.videos) > 0
					$scope.displayedVideos = [].concat($scope.videos)
			)

		$dragon.onReady(() ->
			$dragon.subscribe('dataset', $scope.datasetChannel, {id: $scope.datasetId}).then((response) ->
				$scope.datasetDataMapper = new DataMapper(response.data)
			)

			$dragon.subscribe('video', $scope.videosChannel, {dataset__id: $scope.datasetId}).then((response) ->
				$scope.videosDataMapper = new DataMapper(response.data)
			)

			if $scope.datasetId != "-1"
				$scope.getDataset()
		)

		$dragon.onChannelMessage((channels, message) ->
			if (indexOf.call(channels, $scope.datasetChannel) > -1)
				if $scope.datasetDataMapper != undefined
					$scope.$apply(() ->
						$scope.datasetDataMapper.mapData($scope.dataset, message)

						$scope.showTaskConfirmation(message)
					)

			if (indexOf.call(channels, $scope.videosChannel) > -1)
				if $scope.videosDataMapper != undefined
					$scope.$apply(() ->
						$scope.videosDataMapper.mapData($scope.videos, message)
						if _.size($scope.videos > 0)
							$scope.displayedVideos = [].concat($scope.videos)
					)
		)


		# If dataset created, show confirmation
		if $stateParams.created
			$alert({
				title: 'Confirmation',
				content: 'Dataset successfully created!',
				placement: 'top-right',
				type: 'success',
				duration: 4,
				show: true
			})

		# Edit dataset
		$scope.edit = () ->
			$scope.tempDataset.name = $scope.dataset.name
			$scope.tempDataset.description = $scope.dataset.description
#			$scope.tempDataset.base_path = $scope.dataset.base_path
			$scope.editMode = true

		# Cancel edition
		$scope.cancel = () ->
			if $scope.editMode
				$scope.editMode = false

			if $scope.createMode
				$scope.createMode = false

			# Reset original values
			$scope.dataset.name = $scope.tempDataset.name
			$scope.dataset.description = $scope.tempDataset.description


		# Submit new dataset values
		$scope.submitDatasetForm = (isValid) ->
			if isValid
				if $scope.createMode
					$dragon.create('dataset', $scope.dataset).then((response) ->
						if response.data.error or response.data.id == undefined
							$alert({
								title: 'Error',
								content: response.data.error.message,
								placement: 'top-right',
								type: 'danger',
								show: true
							})
						else
							dataset = response.data
							$state.go('datasets.detail' ,{ datasetId: dataset.id, created: true },{ })
					)

				else if $scope.editMode
					newDescription = $scope.dataset.description
					$dragon.update('dataset', $scope.dataset).then((response) ->
						if response.data.description == newDescription
							$alert({
								title: 'Confirmation',
								content: 'Dataset successfully updated!',
								placement: 'top-right',
								type: 'success',
								duration: 4,
								show: true
							})
						else
							$alert({
								title: 'Error',
								content: 'Problem during dataset update!',
								placement: 'top-right',
								type: 'danger',
								show: true
							})
						$scope.editMode = false
					)
				return
			return

		# Remove dataset
		removeModalScope = $scope.$new(true)
		removeModalScope.title = "Confirmation"
		removeModalScope.content = "Are your sure you want to remove this dataset?"
		removeModalScope.buttons = [
			{
				text: "Remove",
				class: "btn-danger",
				callback: () -> $scope.remove()
			}
		]

		removeModal = $modal({
			scope: removeModalScope,
			template: "/partials/modal.tpl.html",
			show: false
		})

		$scope.showRemoveModal = () ->
			removeModal.$promise.then(removeModal.show)

		$scope.remove = () ->
			$dragon.delete('dataset', {id:$scope.datasetId}).then((response) ->
				$state.go('datasets.list', { removed: true }, { })
			)


		# Remove video
		removeVideoModalScope = $scope.$new(true)
		removeVideoModalScope.title = "Confirmation"
		removeVideoModalScope.content = "Are your sure you want to remove this video?"
		removeVideoModalScope.buttons = [{
			text: "Remove",
			class: "btn-danger",
			callback: () -> $scope.removeVideo()
		}]

		removeVideoModal = $modal({
			scope: removeVideoModalScope,
			template: "/partials/modal.tpl.html",
			show: false
		})

		$scope.showRemoveVideoModal = (videoId) ->
			$scope.videoToDeleteId = videoId
			removeVideoModal.$promise.then(removeVideoModal.show)

		$scope.removeVideo = () ->
			$dragon.delete('video', {id:$scope.videoToDeleteId}).then((response) ->
				$scope.videoToDeleteId = null
				$alert({
					title: 'Confirmation',
					content: 'Video successfully removed!',
					placement: 'top-right',
					type: 'success',
					duration: 4,
					show: true
				})
			)

		# Prepare dataset
		$scope.prepareDataset = () ->
			$dragon.callRouter('prepare_dataset', 'dataset', {dataset_id:$scope.datasetId})

		# Scan video folder
		$scope.scanVideoFolder = () ->
			$scope.scanningVideoFolder = true
			$dragon.callRouter('scan_video_folder', 'dataset', {dataset_id:$scope.datasetId})

		# Prepare videos
		$scope.prepareVideos = (overwrite) ->
			#$scope.nb_videos_done.videos_preparation = 0
			$scope.preparingVideos = true
			$dragon.callRouter('prepare_videos', 'dataset', {dataset_id:$scope.datasetId, overwrite:overwrite})

		# Detect shot boundaries
		$scope.detectShotBoundaries = () ->
			#$scope.nb_videos_done.shot_boundaries_detection = 0
			$scope.detectingShotBoundaries = true
			$dragon.callRouter('detect_shot_boundaries', 'dataset', {dataset_id:$scope.datasetId, configuration:$scope.sbd.configuration})

		# Extract features
		$scope.extractFeatures = () ->
			#$scope.nb_videos_done.feature_extraction = 0
			$scope.extractingFeatures = true
			selected_feature_types = $scope.selectedFeatures.audio.concat($scope.selectedFeatures.video)
			$dragon.callRouter('extract_features', 'dataset', {dataset_id:$scope.datasetId, feature_types:selected_feature_types, overwrite:$scope.extractFeatures.overwrite})

		# Model arousal
		$scope.modelArousal = () ->
			#$scope.nb_videos_done.arousal_modeling = 0
			$scope.modelingArousal = true
			selected_feature_types = $scope.arousalSelectedFeatures.audio.concat($scope.arousalSelectedFeatures.video)
			$dragon.callRouter('model_arousal', 'dataset', {dataset_id:$scope.datasetId, feature_types:selected_feature_types, overwrite:$scope.modelArousal.overwrite})


		## Watches
		# Change manage button text
		$scope.$watch "manageMode", ->
			$scope.toggleText = (if $scope.manageMode then "Exit manage" else "Manage")
			sessionStorage.manageMode = JSON.stringify($scope.manageMode)

		# Reload dataset after video folder scan
		$scope.$watch "dataset.scan_state", ->
			if $scope.dataset.scan_state == ComputingStateType.IN_PROGRESS
				$scope.scanningVideoFolder = true

				$scope.readyForShotBoundariesDetection = false
				$scope.readyForFeatureExtraction = false
				$scope.readyForArousalModeling = false
			else
				if $scope.scanningVideoFolder
					$scope.getDataset()

				$scope.scanningVideoFolder = false

				$scope.readyForShotBoundariesDetection = $scope.dataset.videos_preparation_state in [ComputingStateType.WARNING, ComputingStateType.SUCCESS]
				$scope.readyForFeatureExtraction = $scope.readyForShotBoundariesDetection && $scope.dataset.shot_boundaries_detection_state in [ComputingStateType.WARNING, ComputingStateType.SUCCESS]
				$scope.readyForArousalModeling = $scope.readyForFeatureExtraction && $scope.dataset.feature_extraction_state in [ComputingStateType.WARNING, ComputingStateType.SUCCESS]


		$scope.$watch "dataset.videos_preparation_state", ->
			$scope.readyForShotBoundariesDetection = $scope.dataset.videos_preparation_state in [ComputingStateType.WARNING, ComputingStateType.SUCCESS]

			if $scope.dataset.videos_preparation_state == ComputingStateType.IN_PROGRESS
				$scope.preparingVideos = true

				$scope.readyForShotBoundariesDetection = false
				$scope.readyForFeatureExtraction = false
				$scope.readyForArousalModeling = false
			else
				if $scope.preparingVideos
					$scope.getVideos()

				$scope.preparingVideos = false

				$scope.readyForShotBoundariesDetection = $scope.dataset.videos_preparation_state in [ComputingStateType.WARNING, ComputingStateType.SUCCESS]
				$scope.readyForFeatureExtraction = $scope.readyForShotBoundariesDetection && $scope.dataset.shot_boundaries_detection_state in [ComputingStateType.WARNING, ComputingStateType.SUCCESS]
				$scope.readyForArousalModeling = $scope.readyForFeatureExtraction && $scope.dataset.feature_extraction_state in [ComputingStateType.WARNING, ComputingStateType.SUCCESS]


		$scope.$watch "dataset.shot_boundaries_detection_state", ->
			$scope.readyForFeatureExtraction = $scope.readyForShotBoundariesDetection && $scope.dataset.shot_boundaries_detection_state in [ComputingStateType.WARNING, ComputingStateType.SUCCESS]

			if $scope.dataset.shot_boundaries_detection_state == ComputingStateType.IN_PROGRESS
				$scope.detectingShotBoundaries = true

				$scope.readyForVideosPreparation = false
				$scope.readyForFeatureExtraction = false
				$scope.readyForArousalModeling = false
			else
				if $scope.detectingShotBoundaries
					$scope.getVideos()

				$scope.detectingShotBoundaries = false

				$scope.readyForVideosPreparation = true
				$scope.readyForFeatureExtraction = $scope.readyForShotBoundariesDetection && $scope.dataset.shot_boundaries_detection_state in [ComputingStateType.WARNING, ComputingStateType.SUCCESS]
				$scope.readyForArousalModeling = $scope.readyForFeatureExtraction && $scope.dataset.feature_extraction_state in [ComputingStateType.WARNING, ComputingStateType.SUCCESS]

		$scope.$watch "dataset.feature_extraction_state", ->
			$scope.readyForArousalModeling = $scope.readyForFeatureExtraction && $scope.dataset.feature_extraction_state in [ComputingStateType.WARNING, ComputingStateType.SUCCESS]

			if $scope.dataset.feature_extraction_state == ComputingStateType.IN_PROGRESS
				$scope.extractingFeatures = true

				$scope.readyForVideosPreparation = false
				$scope.readyForShotBoundariesDetection = false
				$scope.readyForArousalModeling = false
			else
				if $scope.extractingFeatures
					$scope.getVideos()

				$scope.extractingFeatures = false

				$scope.readyForVideosPreparation = true
				$scope.readyForShotBoundariesDetection = $scope.dataset.videos_preparation_state in [ComputingStateType.WARNING, ComputingStateType.SUCCESS]
				$scope.readyForArousalModeling = $scope.readyForFeatureExtraction && $scope.dataset.feature_extraction_state in [ComputingStateType.WARNING, ComputingStateType.SUCCESS]


		$scope.$watch "dataset.arousal_modeling_state", ->
			if $scope.dataset.arousal_modeling_state == ComputingStateType.IN_PROGRESS
				$scope.modelingArousal = true

				$scope.readyForVideosPreparation = false
				$scope.readyForShotBoundariesDetection = false
				$scope.readyForFeatureExtraction = false
			else
				if $scope.modelingArousal
					$scope.getVideos()

				$scope.modelingArousal = false

				$scope.readyForVideosPreparation = true
				$scope.readyForShotBoundariesDetection = $scope.dataset.videos_preparation_state in [ComputingStateType.WARNING, ComputingStateType.SUCCESS]
				$scope.readyForFeatureExtraction = $scope.readyForShotBoundariesDetection && $scope.dataset.shot_boundaries_detection_state in [ComputingStateType.WARNING, ComputingStateType.SUCCESS]


		# Global threshold for algos configuration
		# TODO: why cookie???
		$scope.$watch "sbd.globalThreshold", ->
			$cookieStore.put('sbd.globalThreshold', $scope.sbd.globalThreshold)
			$scope.sbd.configuration.forEach((algorithm)->
				algorithm.threshold = $scope.sbd.globalThreshold
			)

		$scope.$watch "dataset.available_features", ->
			try
				$scope.arousalAudioFeatureTypes = _.filter(featureTypes, (feature_type) -> feature_type.type == 'audio' && feature_type.value in $scope.dataset.available_features)
				$scope.arousalVideoFeatureTypes = _.filter(featureTypes, (feature_type) -> feature_type.type == 'video' && feature_type.value in $scope.dataset.available_features)

				$scope.selectedFeatures.audio = $scope.arousalAudioFeatureTypes.map((item) -> item.value)
				$scope.selectedFeatures.video = $scope.arousalVideoFeatureTypes.map((item) -> item.value)
			catch



		# Show confirmation messages after tasks
		$scope.showTaskConfirmation = (message) ->
			if message.action = "updated"
				type = undefined
				if message.data.hasOwnProperty('preparation_state')
					if message.data['preparation_state'] == ComputingStateType.ERROR
						type = "danger"
						text = "dataset preparation"
					else if message.data['preparation_state'] == ComputingStateType.WARNING
						type = "warning"
						text = "dataset preparation"
					else if message.data['preparation_state'] == ComputingStateType.SUCCESS
						type = "success"
						text = "Dataset prepared"

				else if message.data.hasOwnProperty('scan_state')
					if message.data['scan_state'] == ComputingStateType.ERROR
						type = "danger"
						text = "dataset video folder scan"
					else if message.data['scan_state'] == ComputingStateType.WARNING
						type = "warning"
						text = "dataset video folder scan"
					else if message.data['scan_state'] == ComputingStateType.SUCCESS
						type = "success"
						text = "Dataset video folder scanned"

				else if message.data.hasOwnProperty('videos_preparation_state')
					if message.data['videos_preparation_state'] == ComputingStateType.ERROR
						type = "danger"
						text = "videos preparation"
					else if message.data['videos_preparation_state'] == ComputingStateType.WARNING
						type = "warning"
						text = "videos preparation"
					else if message.data['videos_preparation_state'] == ComputingStateType.SUCCESS
						type = "success"
						text = "Videos prepared"

				else if message.data.hasOwnProperty('shot_boundaries_detection_state')
					if message.data['shot_boundaries_detection_state'] == ComputingStateType.ERROR
						type = "danger"
						text = "shot boundaries detection"
					else if message.data['shot_boundaries_detection_state'] == ComputingStateType.WARNING
						type = "warning"
						text = "shot boundaries detection"
					else if message.data['shot_boundaries_detection_state'] == ComputingStateType.SUCCESS
						type = "success"
						text = "Shot boundaries detected"

				else if message.data.hasOwnProperty('feature_extraction_state')
					if message.data['feature_extraction_state'] == ComputingStateType.ERROR
						type = "danger"
						text = "features extraction"
					else if message.data['feature_extraction_state'] == ComputingStateType.WARNING
						type = "warning"
						text = "features extraction"
					else if message.data['feature_extraction_state'] == ComputingStateType.SUCCESS
						type = "success"
						text = "Features extracted"

				else if message.data.hasOwnProperty('arousal_modeling_state')
					if message.data['arousal_modeling_state'] == ComputingStateType.ERROR
						type = "danger"
						text = "arousal modeling"
					else if message.data['arousal_modeling_state'] == ComputingStateType.WARNING
						type = "warning"
						text = "arousal modeling"
					else if message.data['arousal_modeling_state'] == ComputingStateType.SUCCESS
						type = "success"
						text = "Arousal modeled"

				if type
					if type == "danger"
						title = "Error"
						content = "A problem occurred during " + text + "."
						duration = false
					else if type == "warning"
						title = "Warning"
						content = "Please control that the " + text + " has worked."
						duration = false
					else if type == "success"
						title = "Confirmation"
						content = text + " successfully!"
						duration = 4

					$alert({
						title: title,
						content: content,
						placement: 'top-right',
						type: type,
						duration: duration,
						show: true
					})

		# Change mode
		if $stateParams.datasetId == "-1" or $stateParams.datasetId == -1
			# Create new dataset mode
			$scope.createMode = true
			$scope.dataset = {}
			$scope.dataset.name = ""
			$scope.dataset.description = ""


		## Algorithms
		# Add algorithm to dataset
		$scope.addSBDAlgo = () ->
			ok = true
			$scope.sbd.configuration.forEach((algorithm)->
				if(algorithm.value == $scope.sbd.algorithm.value)
					alert('Already exist, delete before add the same algo')
					ok = false
			)
			if ok
				algorithm = {}
				algorithm.value = $scope.sbd.algorithm.value
				algorithm.label = $scope.sbd.algorithms[$scope.sbd.algorithm.value].label
				algorithm.weight = $scope.sbd.weight
				algorithm.threshold = $scope.sbd.globalThreshold
				$scope.sbd.configuration.push(algorithm)
				$scope.sbd.addAlgorithm = false
			$cookieStore.put('sbd.configuration', $scope.sbd.configuration)


		# Delete algorithm in list
		$scope.removeSBDAlgo = (algorithmToRemove) ->
			$scope.sbd.configuration.forEach((algorithm)->
				if(algorithmToRemove.value == algorithm.value)
					index = $scope.sbd.configuration.indexOf(algorithm)
					$scope.sbd.configuration.splice(index,1)
			)
			$cookieStore.put('sbd.configuration', $scope.sbd.configuration)

		# Show button
		$scope.buttonShow = (data) ->
			if(data['state'] == 'None')
				return true
			vid = $filter('getByProperty')('id',data['videoId'],$scope.videos)
			return vid[data['state']] == data['value']


		$scope.clickFunction = (data) ->
			$scope.$eval(data['function'])(data)



		## File uploader
		$scope.uploader = new FileUploader(url: "/upload")
		$scope.$watch "addVideo", ->
			if $scope.addVideo
				$scope.uploader.emotion = 0


		$scope.$watch "dataset.video_path", ->
			try
				folder = ""
				if $scope.uploader.emotion != undefined
					emotion = _.result(_.find($scope.emotions, {'value': $scope.uploader.emotion}), 'label')
					folder = "/" + emotion

				$scope.uploader.formData = [{'path': $scope.dataset.video_path + folder}]
			catch
			# No values for the moment

		$scope.$watch "uploader.emotion", ->
			try
				folder = ""
				if $scope.uploader.emotion != undefined
					emotion = _.result(_.find($scope.emotions, {'value': $scope.uploader.emotion}), 'label')
					folder = "/" + emotion
					
				$scope.uploader.formData = [{'path': $scope.dataset.video_path + folder}]
			catch
				# No values for the moment

		# Filters
		$scope.uploader.filters.push
			name: "customFilter"
			fn: (item, options) ->
				@queue.length < 10

		# Callbacks
#		uploader.onWhenAddingFileFailed = (item, filter, options) -> #{File|FileLikeObject}
#			console.info "onWhenAddingFileFailed", item, filter, options
#
#		uploader.onAfterAddingFile = (fileItem) ->
#			console.info "onAfterAddingFile", fileItem
#
#		uploader.onAfterAddingAll = (addedFileItems) ->
#			console.info "onAfterAddingAll", addedFileItems
#
#		uploader.onBeforeUploadItem = (item) ->
#			console.info "onBeforeUploadItem", item
#
#		uploader.onProgressItem = (fileItem, progress) ->
#			console.info "onProgressItem", fileItem, progress
#
#		uploader.onProgressAll = (progress) ->
#			console.info "onProgressAll", progress
#
#		uploader.onSuccessItem = (fileItem, response, status, headers) ->
#			console.info "onSuccessItem", fileItem, response, status, headers
#
#		uploader.onErrorItem = (fileItem, response, status, headers) ->
#			console.info "onErrorItem", fileItem, response, status, headers
#
#		uploader.onCancelItem = (fileItem, response, status, headers) ->
#			console.info "onCancelItem", fileItem, response, status, headers

		$scope.uploader.onCompleteItem = (fileItem, response, status, headers) ->
			$scope.uploader.removeFromQueue(fileItem)

		$scope.uploader.onCompleteAll = ->
#			$state.transitionTo($state.current, { datasetId: $scope.dataset.id }, {
#				reload: true
#			})
			$scope.scanVideoFolder()
	]
