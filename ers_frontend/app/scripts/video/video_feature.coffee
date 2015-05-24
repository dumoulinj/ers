frame2seconds = (frameNb, fps) ->
	frameNb * 1 / fps

seconds2frame = (seconds, fps) ->
	seconds * fps

angular
	.module 'app.video'

	.controller 'FeaturesCtrl', ($scope, video, $timeout, Restangular, $dragon, featureTypes, featureFunctionTypes) ->
		# Initialize tooltips on buttons
		$timeout(() ->
			$('[data-toggle="tooltip"]').tooltip()
		, 500)

		$scope.getSize = (collection) ->
			_.size(collection)

		$scope.video = video
		$scope.$parent.displayVideo = true
		$scope.featureTypes = featureTypes
		$scope.availableFeatures = []

		$scope.allFeatures = []

		$scope.showFeatures = {}

		$scope.checkAllFeatures = (featuresType) ->
			_.map($scope.showFeatures[featuresType], (val, i, arr) ->
				arr[i] = true
			)

		$scope.uncheckAllFeatures = (featuresType) ->
			_.map($scope.showFeatures[featuresType], (val, i, arr) ->
				arr[i] = false
			)

		$scope.hasFeatures = () ->
			_.size($scope.availableFeatures) > 0

		$('[data-toggle="tooltip"]').tooltip()

		$scope.$watch "video.available_features", ->
			try
				availableFeatures = $.parseJSON($scope.video.available_features)

				$scope.availableFeatures = _.filter(featureTypes, (feature_type) ->
					feature_type.value in availableFeatures
				)
			catch


		$scope.showAddFeatureButton = () ->
			$scope.addFeature.feature != undefined && _.find($scope.allFeatures, {'type': $scope.addFeature.feature}) == undefined

		$scope.getFeatureLabel = (value) ->
			_.result(_.find(featureTypes, { 'value': value }), 'label')

		$scope.getFeatureFunctionLabel = (value) ->
			_.result(_.find(featureFunctionTypes, {'value':value}), 'label')

		$scope.removeFeature = (featureType) ->
			removed = _.remove($scope.allFeatures, (features) ->
				features["type"] == featureType
			)

			delete $scope.hoverLines[featureType]

		$scope.maxValues = 400

		$scope.stride = (values) ->
			result = []
			size = _.size(values)
			if size > $scope.maxValues
				n = Math.floor(size / $scope.maxValues)

				_.forEach(values, (v, i) ->
					if i % n == 0
						result.push(v)
				)
				result
			else
				values

		$scope.addFeature = () ->
			$dragon.callRouter('get_feature', 'video', {video_id: $scope.video.id, feature_type: $scope.addFeature.feature}).then((response) ->
				features = response.data

				$scope.showFeatures[features.type] = {}

				values
				values_normalized
				values_processed

				all_feature_functions = {}
				value = {}

				if _.size(features.values) > 0
					values = features.values

				if _.size(features.values_normalized) > 0
					values_normalized = features.values_normalized

				if _.size(features.values_processed) > 0
					values_processed = features.values_processed

				functionTypes = []

				_.forEach(values, (values, key) ->
					ikey = parseInt(key)
					if ikey == 0
						value = {
							"type": ikey
							"data": [
								{
									"key": "Raw"
									"values": $scope.stride(values)
								}
							]
						}
					else
						functionTypes.push(ikey)
						$scope.showFeatures[features.type][ikey] = true

						all_feature_functions[ikey] = {
							"type": ikey
							"title": $scope.getFeatureFunctionLabel(ikey)
							"data": [
								{
									"key": "Raw"
									"values": $scope.stride(values)
								}
							]
						}
				)

				_.forEach(values_normalized, (values, key) ->
					ikey = parseInt(key)
					value["data"].push({
						"key": "Normalized"
						"values": $scope.stride(values)
					})
				)

				_.forEach(values_processed, (values, key) ->
					ikey = parseInt(key)
					value["data"].push({
						"key": "Processed"
						"values": $scope.stride(values)
					})
				)

				$scope.allFeatures.push({
					"type": features.type
					"title": $scope.getFeatureLabel(features.type)
					"value": value
					"functionFeatures": all_feature_functions
				})

				# Initialize tooltips on buttons
				$timeout(() ->
					$('[data-toggle="tooltip"]').tooltip()
				, 500)

				$timeout(() ->
					$scope.drawHoverLine(features.type, 0)
					_.forEach(functionTypes, (functionType) ->
						$scope.drawHoverLine(features.type, functionType)
					)
				,3000)
			)

		$scope.yAxisTickFormatFunction = () ->
			(d) ->
				d3.round(d, 2)

		$scope.xAxisTickFormatFunction = () ->
			(d) ->
				d3.round(frame2seconds(d, $scope.video.video_part.fps), 0)


		$scope.hoverLines = {}

		updateTimeline = (posX) ->
			_.forEach($scope.hoverLines, (functions) ->
				_.forEach(functions, (hoverLine) ->
					hoverLine.attr("x1", posX).attr("x2", posX)
				)
			)

		$scope.onVideoPlayerReady = (API) ->
			$scope.videoAPI = API
			$scope.arousalChart = d3.select('#arousalCurveId svg g g g.nv-linesWrap')

		$scope.$parent.onUpdateTime = (currentTime, totalTime) ->
			frameNb = seconds2frame(currentTime, $scope.video.video_part.fps)
			pos = getXPosFromValue(frameNb)
			updateTimeline(pos)
			$scope.$parent.crtTime = currentTime

		$scope.$on('elementClick.directive', (angularEvent, event) ->
			seek = frame2seconds(event.point[0], $scope.video.video_part.fps)
			$scope.videoAPI.seekTime(seek)
			pos = getXPosFromValue(event.point[0], $scope.video.video_part.fps)
			updateTimeline(pos)
		)

		graphWidth = 0
		graphHeight = 0
		maxXValue = 0

		getXPosFromValue = (value) ->
			graphWidth * value / maxXValue

		getYPosFromValue = (value) ->
			graphHeight * value / 1


		$scope.drawHoverLine = (featuresType, functionType) ->
			id = '#features_' + featuresType + '_' + functionType
			chart = d3.select(id + ' .nv-linesWrap')

#			arousalCurveChart = d3.select(id + ' .nv-series-0')
			rect = d3.select(id + ' .nv-lineChart g rect')

			# Chart hover lines
			graphWidth = rect.attr("width")
			graphHeight = rect.attr("height")

			if functionType == 0
				featuresData = _.result(_.find($scope.allFeatures, {'type': featuresType}), 'value')
				functionData = featuresData['data'][0]['values']
			else
				featuresData = _.result(_.find($scope.allFeatures, {'type': featuresType}), 'functionFeatures')
				functionData = featuresData[functionType]['data'][0]['values']

			maxXValue = _.last(functionData)[0]

			# Playing line$
			frameNb = seconds2frame($scope.$parent.crtTime, $scope.video.video_part.fps)
			pos = getXPosFromValue(frameNb)

			hoverLine = chart.append("line")
				.attr("x1", pos).attr("x2", pos)
				.attr("y1", 0).attr("y2", graphHeight)
				.attr("stroke-width", 1)
				.style("opacity", 0.9)
				.attr("stroke", "grey")

			if $scope.hoverLines[featuresType] == undefined
				$scope.hoverLines[featuresType] = {}
			$scope.hoverLines[featuresType][functionType] = hoverLine
