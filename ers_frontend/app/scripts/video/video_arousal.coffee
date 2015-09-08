angular
	.module 'app.video'
	.controller 'ArousalCtrl', ($scope, $timeout, video, arousal, featureTypes, featureFunctionTypes, hue) ->
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
			try
				hoverLine.attr("x1", posX).attr("x2", posX)

		$scope.onVideoPlayerReady = (API) ->
			$scope.videoAPI = API
			$scope.arousalChart = d3.select('#arousalCurveId svg g g g.nv-linesWrap')

		$scope.$parent.onUpdateTime = (currentTime, totalTime) ->
			frameNb = seconds2frame(currentTime, $scope.video.video_part.fps)
			pos = getXPosFromValue(frameNb)
			updateTimeline(pos)
			$scope.$parent.crtTime = currentTime

			# Fake
			emotionFrame = d3.round(currentTime,0) * $scope.video.video_part.fps
			if frameEmotions.values[emotionFrame]?
				$scope.currentFrame = emotionFrame

			if $scope.currentEmotion != 'neutral'
				frameNb = d3.round(frameNb,0)
				if frameNb - $scope.lastEmotionIntensityChange > 25
					$scope.lastEmotionIntensityChange = frameNb
					intensity = $scope.arousal.arousal_curve[frameNb][1]
					$scope.changeEmotionIntensity(intensity)


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

			$scope.lastEmotionIntensityChange = 0

			emotionFrame = d3.round(seek,0) * $scope.video.video_part.fps
			if frameEmotions.values[emotionFrame]?
				$scope.currentFrame = emotionFrame
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

		# Fake
		$scope.lastEmotionIntensityChange = 0
		$scope.currentEmotion = 'neutral'

		frameEmotions = {values: []}
		#	Neutral
		frameEmotions.values[0 * $scope.video.video_part.fps] = [0.1,0.1,0.05,0.2,0.05,0,0.5]
		frameEmotions.values[1 * $scope.video.video_part.fps] = [0.1,0.1,0.05,0.2,0.15,0,0.4]
		frameEmotions.values[2 * $scope.video.video_part.fps] = [0.0,0.2,0.05,0.2,0.05,0,0.5]
		frameEmotions.values[3 * $scope.video.video_part.fps] = [0.1,0.1,0.05,0,0.05,0,0.7]
		frameEmotions.values[4 * $scope.video.video_part.fps] = [0.1,0.1,0.05,0.2,0.1,0,0.45]
		frameEmotions.values[5 * $scope.video.video_part.fps] = [0.1,0.1,0.06,0.1,0.05,0,0.5]
		frameEmotions.values[6 * $scope.video.video_part.fps] = [0.1,0.0,0.05,0.3,0.05,0,0.5]
		frameEmotions.values[7 * $scope.video.video_part.fps] = [0.1,0.1,0.05,0.0,0.05,0.2,0.5]
		frameEmotions.values[8 * $scope.video.video_part.fps] = [0.1,0.1,0.05,0.2,0.1,0,0.45]
		frameEmotions.values[9 * $scope.video.video_part.fps] = [0.1,0.1,0.05,0.1,0.05,0,0.6]
		frameEmotions.values[18 * $scope.video.video_part.fps] = [0.1,0.1,0.05,0,0.05,0,0.7]
		frameEmotions.values[19 * $scope.video.video_part.fps] = [0.1,0.1,0.05,0.2,0.15,0,0.4]
		frameEmotions.values[20 * $scope.video.video_part.fps] = [0.1,0.1,0.05,0.2,0.05,0,0.5]
		frameEmotions.values[21 * $scope.video.video_part.fps] = [0.1,0.1,0.05,0,0.05,0,0.7]
		frameEmotions.values[39 * $scope.video.video_part.fps] = [0.1,0.1,0.05,0.0,0.05,0.2,0.5]
		frameEmotions.values[40 * $scope.video.video_part.fps] = [0.1,0.1,0.05,0.2,0.05,0,0.5]
		frameEmotions.values[41 * $scope.video.video_part.fps] = [0.1,0.1,0.05,0.0,0.05,0.2,0.5]
		frameEmotions.values[42 * $scope.video.video_part.fps] = [0.1,0.1,0.05,0,0.05,0,0.7]
		frameEmotions.values[43 * $scope.video.video_part.fps] = [0.1,0.1,0.05,0.2,0.05,0,0.5]
		frameEmotions.values[53 * $scope.video.video_part.fps] = [0.1,0.1,0.05,0.2,0.05,0,0.5]
		frameEmotions.values[54 * $scope.video.video_part.fps] = [0.1,0.1,0.05,0.2,0.05,0,0.5]
		frameEmotions.values[110 * $scope.video.video_part.fps] = [0.1,0.1,0.05,0.2,0.05,0,0.5]
		frameEmotions.values[111 * $scope.video.video_part.fps] = [0.1,0.1,0.05,0.2,0.05,0,0.5]
		frameEmotions.values[112 * $scope.video.video_part.fps] = [0.1,0.1,0.05,0,0.05,0,0.7]
		frameEmotions.values[113 * $scope.video.video_part.fps] = [0.1,0.1,0.05,0.2,0.05,0,0.5]
		frameEmotions.values[114 * $scope.video.video_part.fps] = [0.1,0.1,0.05,0.0,0.05,0.2,0.5]
		frameEmotions.values[115 * $scope.video.video_part.fps] = [0.1,0.1,0.05,0.2,0.05,0,0.5]
		frameEmotions.values[116 * $scope.video.video_part.fps] = [0.1,0.1,0.05,0.2,0.05,0,0.5]
		frameEmotions.values[117 * $scope.video.video_part.fps] = [0.1,0.1,0.05,0.2,0.05,0,0.5]
		frameEmotions.values[118 * $scope.video.video_part.fps] = [0.1,0.1,0.05,0,0.05,0,0.7]
		frameEmotions.values[119 * $scope.video.video_part.fps] = [0.1,0.1,0.05,0.2,0.05,0,0.5]
		frameEmotions.values[120 * $scope.video.video_part.fps] = [0.1,0.1,0.05,0.2,0.05,0,0.5]
		frameEmotions.values[121 * $scope.video.video_part.fps] = [0.1,0.1,0.05,0.0,0.05,0.2,0.5]
		frameEmotions.values[122 * $scope.video.video_part.fps] = [0.1,0.1,0.05,0.2,0.05,0,0.5]
		frameEmotions.values[123 * $scope.video.video_part.fps] = [0.1,0.1,0.05,0.2,0.05,0,0.5]
		frameEmotions.values[124 * $scope.video.video_part.fps] = [0.1,0.1,0.05,0,0.05,0,0.7]
		frameEmotions.values[128 * $scope.video.video_part.fps] = [0.1,0.1,0.05,0.2,0.05,0,0.5]
		frameEmotions.values[129 * $scope.video.video_part.fps] = [0.1,0.1,0.05,0.2,0.05,0,0.5]


		#Disgust
		frameEmotions.values[10 * $scope.video.video_part.fps] = [0.1,0.5,0.05,0.2,0.05,0,0.1]
		frameEmotions.values[11 * $scope.video.video_part.fps] = [0.1,0.6,0.05,0.1,0.05,0,0.1]
		frameEmotions.values[12 * $scope.video.video_part.fps] = [0.1,0.4,0.05,0.2,0.15,0,0.1]
		frameEmotions.values[13 * $scope.video.video_part.fps] = [0.1,0.5,0.05,0.2,0.05,0,0.1]
		frameEmotions.values[14 * $scope.video.video_part.fps] = [0.1,0.4,0.05,0.2,0.15,0,0.1]
		frameEmotions.values[15 * $scope.video.video_part.fps] = [0.1,0.6,0.05,0.1,0.05,0,0.1]
		frameEmotions.values[16 * $scope.video.video_part.fps] = [0.1,0.5,0.05,0.2,0.05,0,0.1]
		frameEmotions.values[17 * $scope.video.video_part.fps] = [0.1,0.4,0.05,0.2,0.15,0,0.1]

		#Surprise
		frameEmotions.values[140 * $scope.video.video_part.fps] = [0.1,0,0.05,0.1,0.05,0.6,0.1]
		frameEmotions.values[141 * $scope.video.video_part.fps] = [0.2,0,0.05,0.1,0.05,0.5,0.1]
		frameEmotions.values[142 * $scope.video.video_part.fps] = [0.1,0,0.15,0.2,0.05,0.4,0.1]
		frameEmotions.values[143 * $scope.video.video_part.fps] = [0.1,0,0.05,0.1,0.05,0.6,0.1]
		frameEmotions.values[144 * $scope.video.video_part.fps] = [0.1,0,0.15,0.2,0.05,0.4,0.1]
		frameEmotions.values[145 * $scope.video.video_part.fps] = [0.2,0,0.05,0.1,0.05,0.5,0.1]
		frameEmotions.values[146 * $scope.video.video_part.fps] = [0.1,0,0.05,0.1,0.05,0.6,0.1]
		frameEmotions.values[147 * $scope.video.video_part.fps] = [0.1,0,0.15,0.2,0.05,0.4,0.1]
		frameEmotions.values[148 * $scope.video.video_part.fps] = [0.1,0,0.05,0.1,0.05,0.6,0.1]
		frameEmotions.values[21 * $scope.video.video_part.fps] = [0.1,0,0.05,0.1,0.05,0.6,0.1]
		frameEmotions.values[22 * $scope.video.video_part.fps] = [0.2,0,0.05,0.1,0.05,0.5,0.1]
		frameEmotions.values[23 * $scope.video.video_part.fps] = [0.1,0,0.05,0.1,0.05,0.6,0.1]
		frameEmotions.values[24 * $scope.video.video_part.fps] = [0.2,0,0.05,0.1,0.05,0.5,0.1]
		frameEmotions.values[25 * $scope.video.video_part.fps] = [0.1,0,0.05,0.1,0.05,0.6,0.1]
		frameEmotions.values[26 * $scope.video.video_part.fps] = [0.2,0,0.05,0.1,0.05,0.5,0.1]

		#	Fear
		frameEmotions.values[30 * $scope.video.video_part.fps] = [0.1,0,0.45,0.3,0.05,0,0.1]
		frameEmotions.values[31 * $scope.video.video_part.fps] = [0.1,0.05,0.5,0.2,0.05,0,0.1]
		frameEmotions.values[32 * $scope.video.video_part.fps] = [0.1,0.05,0.5,0.2,0.05,0,0.1]
		frameEmotions.values[33 * $scope.video.video_part.fps] = [0.1,0.05,0.7,0.1,0.05,0,0.1]
		frameEmotions.values[34 * $scope.video.video_part.fps] = [0.1,0.05,0.5,0.2,0.05,0,0.1]
		frameEmotions.values[35 * $scope.video.video_part.fps] = [0.1,0,0.45,0.3,0.05,0,0.1]
		frameEmotions.values[36 * $scope.video.video_part.fps] = [0.1,0.05,0.5,0.2,0.05,0,0.1]
		frameEmotions.values[37 * $scope.video.video_part.fps] = [0.1,0.05,0.5,0.2,0.05,0,0.1]
		frameEmotions.values[38 * $scope.video.video_part.fps] = [0.1,0.05,0.5,0.2,0.05,0,0.1]
		frameEmotions.values[44 * $scope.video.video_part.fps] = [0.1,0,0.45,0.3,0.05,0,0.1]
		frameEmotions.values[45 * $scope.video.video_part.fps] = [0.1,0.05,0.7,0.1,0.05,0,0.1]
		frameEmotions.values[46 * $scope.video.video_part.fps] = [0.1,0.05,0.5,0.2,0.05,0,0.1]
		frameEmotions.values[47 * $scope.video.video_part.fps] = [0.1,0.05,0.5,0.2,0.05,0,0.1]
		frameEmotions.values[48 * $scope.video.video_part.fps] = [0.1,0.05,0.5,0.2,0.05,0,0.1]
		frameEmotions.values[49 * $scope.video.video_part.fps] = [0.1,0.05,0.5,0.2,0.05,0,0.1]
		frameEmotions.values[50 * $scope.video.video_part.fps] = [0.1,0.05,0.5,0.2,0.05,0,0.1]
		frameEmotions.values[51 * $scope.video.video_part.fps] = [0.1,0.05,0.7,0.1,0.05,0,0.1]
		frameEmotions.values[52 * $scope.video.video_part.fps] = [0.1,0.05,0.5,0.2,0.05,0,0.1]
		frameEmotions.values[72 * $scope.video.video_part.fps] = [0.1,0.05,0.5,0.2,0.05,0,0.1]
		frameEmotions.values[73 * $scope.video.video_part.fps] = [0.1,0,0.45,0.3,0.05,0,0.1]
		frameEmotions.values[74 * $scope.video.video_part.fps] = [0.1,0.05,0.7,0.1,0.05,0,0.1]
		frameEmotions.values[75 * $scope.video.video_part.fps] = [0.1,0.05,0.5,0.2,0.05,0,0.1]
		frameEmotions.values[76 * $scope.video.video_part.fps] = [0.1,0.05,0.5,0.2,0.05,0,0.1]

		#	Anger
		frameEmotions.values[27 * $scope.video.video_part.fps] = [0.4,0.15,0.1,0.2,0.05,0,0.1]
		frameEmotions.values[28 * $scope.video.video_part.fps] = [0.5,0.05,0.1,0.2,0.05,0,0.1]
		frameEmotions.values[29 * $scope.video.video_part.fps] = [0.7,0.05,0.1,0.1,0.05,0,0.1]
		frameEmotions.values[55 * $scope.video.video_part.fps] = [0.5,0.05,0.1,0.2,0.05,0,0.1]
		frameEmotions.values[56 * $scope.video.video_part.fps] = [0.5,0.05,0.1,0.2,0.05,0,0.1]
		frameEmotions.values[57 * $scope.video.video_part.fps] = [0.4,0.15,0.1,0.2,0.05,0,0.1]
		frameEmotions.values[58 * $scope.video.video_part.fps] = [0.5,0.05,0.1,0.2,0.05,0,0.1]
		frameEmotions.values[59 * $scope.video.video_part.fps] = [0.5,0.05,0.1,0.2,0.05,0,0.1]
		frameEmotions.values[60 * $scope.video.video_part.fps] = [0.5,0.05,0.1,0.2,0.05,0,0.1]
		frameEmotions.values[61 * $scope.video.video_part.fps] = [0.4,0.15,0.1,0.2,0.05,0,0.1]
		frameEmotions.values[62 * $scope.video.video_part.fps] = [0.7,0.05,0.1,0.1,0.05,0,0.1]
		frameEmotions.values[63 * $scope.video.video_part.fps] = [0.5,0.05,0.1,0.2,0.05,0,0.1]
		frameEmotions.values[64 * $scope.video.video_part.fps] = [0.5,0.05,0.1,0.2,0.05,0,0.1]
		frameEmotions.values[65 * $scope.video.video_part.fps] = [0.4,0.15,0.1,0.2,0.05,0,0.1]
		frameEmotions.values[66 * $scope.video.video_part.fps] = [0.5,0.05,0.1,0.2,0.05,0,0.1]
		frameEmotions.values[67 * $scope.video.video_part.fps] = [0.5,0.05,0.1,0.2,0.05,0,0.1]
		frameEmotions.values[68 * $scope.video.video_part.fps] = [0.5,0.05,0.1,0.2,0.05,0,0.1]
		frameEmotions.values[69 * $scope.video.video_part.fps] = [0.5,0.05,0.1,0.2,0.05,0,0.1]
		frameEmotions.values[70 * $scope.video.video_part.fps] = [0.5,0.05,0.1,0.2,0.05,0,0.1]
		frameEmotions.values[71 * $scope.video.video_part.fps] = [0.7,0.05,0.1,0.1,0.05,0,0.1]
		frameEmotions.values[77 * $scope.video.video_part.fps] = [0.5,0.05,0.1,0.2,0.05,0,0.1]
		frameEmotions.values[78 * $scope.video.video_part.fps] = [0.4,0.15,0.1,0.2,0.05,0,0.1]
		frameEmotions.values[79 * $scope.video.video_part.fps] = [0.5,0.05,0.1,0.2,0.05,0,0.1]
		frameEmotions.values[80 * $scope.video.video_part.fps] = [0.5,0.05,0.1,0.2,0.05,0,0.1]
		frameEmotions.values[81 * $scope.video.video_part.fps] = [0.7,0.05,0.1,0.1,0.05,0,0.1]
		frameEmotions.values[82 * $scope.video.video_part.fps] = [0.5,0.05,0.1,0.2,0.05,0,0.1]
		frameEmotions.values[83 * $scope.video.video_part.fps] = [0.4,0.15,0.1,0.2,0.05,0,0.1]
		frameEmotions.values[84 * $scope.video.video_part.fps] = [0.7,0.05,0.1,0.1,0.05,0,0.1]
		frameEmotions.values[85 * $scope.video.video_part.fps] = [0.5,0.05,0.1,0.2,0.05,0,0.1]
		frameEmotions.values[86 * $scope.video.video_part.fps] = [0.5,0.05,0.1,0.2,0.05,0,0.1]
		frameEmotions.values[87 * $scope.video.video_part.fps] = [0.5,0.05,0.1,0.2,0.05,0,0.1]
		frameEmotions.values[88 * $scope.video.video_part.fps] = [0.4,0.15,0.1,0.2,0.05,0,0.1]
		frameEmotions.values[89 * $scope.video.video_part.fps] = [0.7,0.05,0.1,0.1,0.05,0,0.1]
		frameEmotions.values[90 * $scope.video.video_part.fps] = [0.5,0.05,0.1,0.2,0.05,0,0.1]
		frameEmotions.values[91 * $scope.video.video_part.fps] = [0.5,0.05,0.1,0.2,0.05,0,0.1]
		frameEmotions.values[92 * $scope.video.video_part.fps] = [0.5,0.05,0.1,0.2,0.05,0,0.1]
		frameEmotions.values[93 * $scope.video.video_part.fps] = [0.4,0.15,0.1,0.2,0.05,0,0.1]
		frameEmotions.values[94 * $scope.video.video_part.fps] = [0.5,0.05,0.1,0.2,0.05,0,0.1]
		frameEmotions.values[95 * $scope.video.video_part.fps] = [0.7,0.05,0.1,0.1,0.05,0,0.1]
		frameEmotions.values[96 * $scope.video.video_part.fps] = [0.5,0.05,0.1,0.2,0.05,0,0.1]
		frameEmotions.values[97 * $scope.video.video_part.fps] = [0.5,0.05,0.1,0.2,0.05,0,0.1]
		frameEmotions.values[98 * $scope.video.video_part.fps] = [0.5,0.05,0.1,0.2,0.05,0,0.1]
		frameEmotions.values[99 * $scope.video.video_part.fps] = [0.7,0.05,0.1,0.1,0.05,0,0.1]
		frameEmotions.values[109 * $scope.video.video_part.fps] = [0.5,0.05,0.1,0.2,0.05,0,0.1]
		frameEmotions.values[125 * $scope.video.video_part.fps] = [0.5,0.05,0.1,0.2,0.05,0,0.1]
		frameEmotions.values[126 * $scope.video.video_part.fps] = [0.4,0.15,0.1,0.2,0.05,0,0.1]
		frameEmotions.values[127 * $scope.video.video_part.fps] = [0.5,0.05,0.1,0.2,0.05,0,0.1]

		$scope.lastEmotionIntensityChange = 0
		$scope.currentFrame = 0

		$scope.$watch "currentFrame", ->
			$scope.emotion_data = [
				{
					"key": "Anger"
					"values": [[0,frameEmotions.values[$scope.currentFrame][0]]]
				}
				{
					"key": "Disgust"
					"values": [[0,frameEmotions.values[$scope.currentFrame][1]]]
				}
				{
					"key": "Fear"
					"values": [[0,frameEmotions.values[$scope.currentFrame][2]]]
				}
				{
					"key": "Happiness"
					"values": [[0,frameEmotions.values[$scope.currentFrame][3]]]
				}
				{
					"key": "Sadness"
					"values": [[0,frameEmotions.values[$scope.currentFrame][4]]]
				}
				{
					"key": "Surprise"
					"values": [[0,frameEmotions.values[$scope.currentFrame][5]]]
				}
				{
					"key": "Neutral"
					"values": [[0,frameEmotions.values[$scope.currentFrame][6]]]
				}
			]
			emotion_data = $scope.emotion_data
			emotion = _.max(emotion_data, (emotion_data) -> emotion_data.values[0][1]).key.toLowerCase()
			if emotion != $scope.currentEmotion
				$scope.currentEmotion = emotion
				$scope.changeEmotion(emotion)


		colorArray = ['red', 'green', 'blue', 'yellow', 'grey', 'pink', 'black']
		emotionColors = {
			"anger": colorArray[0]
			"disgust": colorArray[1]
			"fear": colorArray[2]
			"happiness": colorArray[3]
			"sadness": colorArray[4]
			"surprise": colorArray[5]
			"neutral": colorArray[6]
		}
		$scope.colorFunction = () ->
			(d, i) ->
				colorArray[i]

		emotionLabels = ["anger", "disgust", "fear", "happiness", "sadness", "surprise", "neutral"]
		labelIndex = -1
		$scope.valueFormatFunction = () ->
			(d) ->
				labelIndex = (labelIndex + 1) % 7
				emotionLabels[labelIndex]


		$scope.hueConf = {}
		$scope.hueConf.bridgeIP = "192.168.1.104"
		$scope.hueConf.username = "219eed47213d5bf20998f37cd9f9af"


		myHue = hue
		myHue.setup
			username:$scope.hueConf.username
			bridgeIP:$scope.hueConf.bridgeIP


		$scope.emotions = {
			'anger': {
				'xy': [0.5902476752399157, 0.3283797984252815],
				'bri': 255
			},
			'disgust': {
				'xy': [0.4275256269827939, 0.4973783122840834],
				'bri': 120
			},
			'fear': {
				'xy': [0.20603474805814748, 0.11706984540187726],
				'bri': 200
			},
			'happiness': {
				'xy': [0.4579764229120156, 0.4779167810349834],
				'bri': 255
			},
			'sadness': {
				'xy': [0.32791887891898774, 0.35369898666404803],
				'bri': 100
			},
			'surprise': {
				'xy': [0.3390085575518037, 0.28520761959488344],
				'bri': 255
			}
		}

		$scope.changeEmotion = (emotion) ->
			$scope.$parent.shot_style = {border:'solid 5px ' + emotionColors[emotion]}

			if emotion == 'neutral'
				myHue.setLightState(2, {on: false})
			else
#				myHue.setLightState(2, {on: true, xy: $scope.emotions[emotion]['xy'], bri: $scope.emotions[emotion]['bri']})
				myHue.setLightState(2, {on: true, xy: $scope.emotions[emotion]['xy']})


		intensity2bri = (intensity) ->
			min = 0.8

			if intensity > min
				Math.floor((intensity - min) * (255.0 / (1 - min)))
			else
				0

		$scope.changeEmotionIntensity = (intensity) ->
			bri = intensity2bri(intensity)
			myHue.setLightState(2, {bri: bri})
			console.log("Brightness: " + bri)
