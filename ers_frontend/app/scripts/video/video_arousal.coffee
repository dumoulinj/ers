angular
	.module 'app.video'
	.controller 'ArousalCtrl', ($scope, $timeout, video, arousal, featureTypes, featureFunctionTypes) ->
		# Initialize tooltips on buttons
		$timeout(() ->
			$('[data-toggle="tooltip"]').tooltip()
		, 500)

		$scope.video = video
		$scope.arousal = arousal
		$scope.$parent.displayVideo = true

		$scope.hasArousal = () ->
			_.size($scope.arousal.arousal_curve) > 0

		$scope.getFeatureLabel = (value) ->
			_.result(_.find(featureTypes, { 'value': value }), 'label')

		$scope.getFeatureFunctionLabel = (value) ->
			_.result(_.find(featureFunctionTypes, {'value':value}), 'label')

		$scope.API = null
		hoverLine = null


		updateTimeline = (posX) ->
			hoverLine.attr("x1", posX).attr("x2", posX)

		$scope.onVideoPlayerReady = (API) ->
			$scope.videoAPI = API
			$scope.arousalChart = d3.select('#arousalCurveId svg g g g.nv-linesWrap')

		$scope.$parent.onUpdateTime = (currentTime, totalTime) ->
			frameNb = seconds2frame(currentTime, $scope.video.video_part.fps)
			pos = getXPosFromValue(frameNb)
			updateTimeline(pos)
			$scope.$parent.crtTime = currentTime


		$scope.videoConfig = {
			autoHide: true,
			autoHideTime: 1000,
			autoPlay: false,
			responsive: true,
			stretch: "fill"			
		}


		graphWidth = 0
		graphHeight = 0
		maxXValue = 0

		getXPosFromValue = (value) ->
			graphWidth * value / maxXValue

		getYPosFromValue = (value) ->
			graphHeight * value / 1


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


		$scope.yAxisTickFormatFunction = () ->
			(d) ->
				d3.round(d, 2)

		$scope.xAxisTickFormatFunction = () ->
			(d) ->
				d3.round(frame2seconds(d, $scope.video.video_part.fps), 0)


		$scope.$watch "arousal", ->
			if $scope.arousal.arousal_curve
				values = $scope.stride($scope.arousal.arousal_curve)


				arousal_curve = [
					{
						"key": "Arousal curve"
						"values": values
					}
				]


				_.forEach($scope.arousal.used_features, (features, featureType) ->
					iFeatureType = parseInt(featureType)
					_.forEach(features, (functionValues, functionType) ->
						iFunctionType = parseInt(functionType)
						function_label = $scope.getFeatureFunctionLabel(iFunctionType)
						if function_label != "none" and function_label != "value"
							name = $scope.getFeatureLabel(iFeatureType) + " (" + function_label + ")"
						else
							name = $scope.getFeatureLabel(iFeatureType)

						values = $scope.stride(functionValues)

						functionSerie = {
							"key": _.capitalize(name)
							"values": values
						}
						arousal_curve.push(functionSerie)
					)
				)

				$scope.arousal_curve = arousal_curve

		# Chart Events
		$scope.$on('elementClick.directive', (angularEvent, event) ->
			seek = frame2seconds(event.point[0], $scope.video.video_part.fps)
			$scope.videoAPI.seekTime(seek)
			pos = getXPosFromValue(event.point[0], $scope.video.video_part.fps)
			updateTimeline(pos)
		)

		$scope.drawHoverLine = () ->
			$scope.chart = d3.select('#arousalCurveId .nv-linesWrap')
			$scope.arousalCurveChart = d3.select('#arousalCurveId .nv-series-0')
			rect = d3.select('#arousalCurveId .nv-lineChart g rect')

			# Chart hover lines
			graphWidth = rect.attr("width")
			graphHeight = rect.attr("height")
			maxXValue = $scope.arousal.arousal_curve[$scope.arousal.arousal_curve.length-1][0]

			# Playing line$
			frameNb = seconds2frame($scope.$parent.crtTime, $scope.video.video_part.fps)
			pos = getXPosFromValue(frameNb)
			if !hoverLine
				hoverLine = $scope.chart.append("line")
					.attr("x1", pos).attr("x2", pos)
					.attr("y1", 0).attr("y2", graphHeight)
					.attr("stroke-width", 1)
					.style("opacity", 0.9)
					.attr("stroke", "grey")

		$scope.drawCrests = () ->
			$scope.chart = d3.select('#arousalCurveId .nv-linesWrap')

			# Crests
			crestsGroup = $scope.chart.append("g")

			for crest in $scope.arousal.arousal_crests
				crestX = crest[0]
				crestY = crest[1]
				crestPosX = getXPosFromValue(crestX)
				crestPosY = getYPosFromValue(crestY)
				crestsGroup.append("line")
					.attr("x1", crestPosX).attr("x2", crestPosX)
					.attr("y1", graphHeight-crestPosY).attr("y2", graphHeight)
					.attr("stroke-width", 1)
					.attr("stroke", "red")
					.style("opacity", 1)
					.style("stroke-dasharray", ("3, 3"))

			# Troughs
			troughsGroup = $scope.chart.append("g")
			for trough in $scope.arousal.arousal_troughs
				troughX = trough[0]
				troughY = trough[1]
				troughPosX = getXPosFromValue(troughX)
				troughPosY = getYPosFromValue(troughY)
				troughsGroup.append("line")
					.attr("x1", troughPosX).attr("x2", troughPosX)
					.attr("y1", graphHeight-troughPosY).attr("y2", graphHeight)
					.attr("stroke-width", 1)
					.attr("stroke", "green")
					.style("opacity", 1)
					.style("stroke-dasharray", ("3, 3"))

			# Partitions
			partitionsGroup = $scope.chart.append("g")
			for partition in $scope.arousal.arousal_partitions
				boundX1 = partition[0][0]
				boundY1 = partition[0][1]
				boundPosX1 = getXPosFromValue(boundX1)
				boundPosY1 = getYPosFromValue(boundY1)
				boundX2 = partition[1][0]
				boundY2 = partition[1][1]
				boundPosX2 = getXPosFromValue(boundX2)
				boundPosY2 = getYPosFromValue(boundY2)
				partitionsGroup.append("line")
					.attr("x1", boundPosX1).attr("x2", boundPosX2)
					.attr("y1", graphHeight-boundPosY1).attr("y2", graphHeight-boundPosY1)
					.attr("stroke-width", 1)
					.attr("stroke", "black")
					.style("opacity", 1)
					.style("stroke-dasharray", ("3, 3"))

		$scope.arousalLineVisible = true
		$scope.changeFeaturesLinesOpacity = () ->
			d3.selectAll(".nv-group")
				.transition()
				.style("opacity", 0.5)

			if $scope.arousalLineVisible == true
				d3.select(".nv-group.nv-series-0")
					.transition()
					.style("opacity", 1)

		$scope.$on('legendClick.directive', (angularEvent, event) ->
			label = event.key
			disabled = event.disabled

			if label == 'Arousal curve'
				if disabled == true
					$scope.arousalLineVisible = true
				else
					$scope.arousalLineVisible = false

			$timeout($scope.changeFeaturesLinesOpacity, 500)
		)

		if $scope.arousal.arousal_curve
			#Since there is no event for "render end"
			$timeout($scope.changeFeaturesLinesOpacity, 500)
			$timeout($scope.drawHoverLine, 1000)
			$timeout($scope.drawCrests, 1000)
