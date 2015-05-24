angular
	.module 'app.video'
	.controller 'SbdDetailCtrl', ($scope, $timeout, $state, $alert, $filter, videoPart, sbdResult, Restangular, $stateParams) ->
		$scope.$parent.$parent.displayVideo = true
		$scope.video.video_part = videoPart
		$scope.sbdResult = sbdResult

		$scope.formatDate = () ->
			formattedDate = $scope.sbdResult.date.replace('T', ' ')
			formattedDate = formattedDate.replace('Z', '')
			$scope.sbdResult.formattedDate = formattedDate

		$scope.formatDate()

		$scope.cancel = () ->
			Restangular.one('video_processor/video_shots_results',$stateParams.sbdResultId).get().then((sbdResult)->
				$scope.sbdResult = sbdResult
				$scope.formatDate()
			)

		#Save the comment
		$scope.save = (sbdResult) ->
			s = $filter('getByProperty')('id',sbdResult['id'],$scope.$parent.sbdResults)
			s.comment = sbdResult.comment
			$scope.$parent.sbdResults
			sbdResult.patch({comment: sbdResult.comment}).then((r)->
				if sbdResult.id
					$state.transitionTo($state.current, { sbdResultId: sbdResult.id }, {
						reload: true
					})

					$alert({
						title: 'Confirmation',
						content: 'Shot boundaries detection result successfully edited!',
						placement: 'top-right',
						type: 'success',
						duration: 4,
						show: true
					})

				# Get number of videos in dataset folder
				else
					$alert({
						title: 'Error',
						content: 'Problem during edition of the shot boundaries detection result...',
						placement: 'top-right',
						type: 'danger',
						show: true
					})
			)

		$scope.API = null
		hoverLine = null
		precision = 4

		updateTimeline = (posX) ->
			#frame2seconds(posX, $scope.video.video_part.fps)
			hoverLine.attr("x1", posX).attr("x2", posX)

		$scope.onVideoPlayerReady = (API) ->
			$scope.videoAPI = API
			$scope.shotChart = d3.select('#shotCurveId svg g g g.nv-linesWrap')

		$scope.$on('someEvent', (e) ->
			$scope.$parent.shot_style = {border:'solid 5px red'}
		)

		$scope.$parent.$parent.onUpdateTime = (currentTime, totalTime) ->
			$scope.$parent.$parent.crtTime = currentTime
			$scope.$parent.$parent.shot_style = {border:'solid 5px transparent'}
			frameNb = seconds2frame(currentTime, $scope.video.video_part.fps)
			for x in $scope.shotBoundaries
				if(Math.abs(frameNb -  x.frame) < precision )
					$scope.$parent.$parent.shot_style = {border:'solid 5px '+ $scope.colorArray[x.type] }
					break
				else if(x.frame > d3.round(frameNb,0))
					$scope.$parent.$parent.shot_style = {border:'solid 5px transparent'}
					break

			pos = getXPosFromValue(currentTime)
			#pos = seconds2frame(currentTime, $scope.video.video_part.fps)
			updateTimeline(pos)

		$scope.videoConfig = {
			autoHide: true,
			autoHideTime: 1000,
			autoPlay: false,
			responsive: true,
			stretch: "fill"
		}

		# Prepare data for graph
		$scope.shotBoundaries = []
		_.forEach($scope.sbdResult.shot_boundaries, (shot_b) ->
			$scope.shotBoundaries.push(shot_b)
		)

		$scope.shotBoundariesDataBounds = []
		$scope.shotBoundariesDataBounds.push({"serie": 0, "x": 0, "y": 0, "size": 1})
		existingFrames = []
		_.forEach($scope.shotBoundaries, (x) ->
			if _.size(x) == 2 and !_.includes(existingFrames, x.frame)
				$scope.shotBoundariesDataBounds.push({"serie": x.type, "x": x.frame, "y":0, "size": 1})
				existingFrames.push(x.frame)
		)

		$scope.showThumb = false

		shotsDetected = _.filter($scope.shotBoundariesDataBounds, {'serie': 0})
		truePositives = _.filter($scope.shotBoundariesDataBounds, {'serie': 1})
		falsePositives = _.filter($scope.shotBoundariesDataBounds, {'serie': 2})
		misses = _.filter($scope.shotBoundariesDataBounds, {'serie': 3})


		$scope.shotBoundariesData = []

		if _.size(shotsDetected) > 0
			$scope.shotBoundariesData.push({
				key: "Shots detected"
				values: shotsDetected
			})

		if _.size(truePositives) > 0
			$scope.shotBoundariesData.push({
				key: "True positives"
				values: truePositives
			})

		if _.size(falsePositives) > 0
			$scope.shotBoundariesData.push({
				key: "False positives"
				values: falsePositives
			})

		if _.size(misses) > 0
			$scope.shotBoundariesData.push({
				key: "Misses"
				values: misses
			})

		graphWidth = 0
		graphHeight = 0
		maxXValue = 0
		ratio = 0

		getXPosFromValue = (value) ->
			value * ratio
			#graphWidth * value / 3160

		getYPosFromValue = (value) ->
			graphHeight * value / 1

		$scope.yAxisTickFormatFunction = () ->
			(d) ->
				d3.round(d, 2)

		$scope.xAxisTickFormatFunction = () ->
			(d) ->
				frame2seconds(d, $scope.video.video_part.fps)

		# Chart Events
		$scope.$on('elementClick.directive', (angularEvent, event) ->
			seek = frame2seconds(event.point.x, $scope.video.video_part.fps)
			$scope.videoAPI.seekTime(seek)
			pos = getXPosFromValue(seek, $scope.video.video_part.fps)
			updateTimeline(pos)
		)

		draw = () ->
			$scope.chart = d3.select('#shotCurveId .nv-wrap')
			$scope.arousalCurveChart = d3.select('#shotCurveId')
			rect = d3.select('.nv-scatterWrap')

			rect = rect[0][0].childNodes.item(0).childNodes.item(0).childNodes.item(0).childNodes.item(0)

			# Chart hover lines
			graphWidth = rect.width.animVal.value
			graphHeight = rect.height.animVal.value
			maxXValue = graphWidth

			ratio = graphWidth / d3.round(frame2seconds($scope.shotBoundariesDataBounds[$scope.shotBoundariesDataBounds.length-1].x,$scope.video.video_part.fps),12)
			# Playing line
			pos = getXPosFromValue($scope.$parent.$parent.crtTime)
			hoverLine = $scope.chart.append("line")
				.attr("x1", pos).attr("x2", pos)
				.attr("y1", 0).attr("y2", graphHeight)
				.attr("stroke-width", 1)
				.attr("stroke", "grey")
		$timeout(draw, 1000)

		#Form of the scatterf graph
		$scope.shapeFunction = ->
			(d) ->
				"triangle-up"

		$scope.colorArray = ['blue','green', 'red', 'orange']

		$scope.colorFunction = () ->
			return (d, i) ->
				$scope.colorArray[i]
		$scope.shot_style = {border:'solid 5px transparent'}

#		$scope.points = []
#		for x in $scope.shotBoundariesData
#			for y in x.values
#				$scope.points.push(y.x)
#
#
#		$scope.points.sort (a, b) ->
#			a - b
#		#Display thumbtails from shot
#		$scope.$on "tooltipShow.directive", (angularEvent, event) ->
#			console.log(angularEvent)
#			console.log(event)
#			i=0
#			for x in $scope.points
#				if x == event.point.x
#					break
#				else if x >= event.point.x
#					i=-1
#					break
#				i++
#			angularEvent.targetScope.$parent.showThumb = true
#			angularEvent.targetScope.$parent.$digest()
#			angularEvent.targetScope.$parent.linkStart = thumbnails[i]['src']+"/start.png"
#			angularEvent.targetScope.$parent.linkMid = thumbnails[i]['src']+"/mid.png"
#			angularEvent.targetScope.$parent.linkEnd = thumbnails[i]['src']+"/end.png"




#		#Hide thumbtails
#		$scope.$on "tooltipHide.directive", (angularEvent, event) ->
#			angularEvent.targetScope.$parent.showThumb = false
#			angularEvent.targetScope.$parent.$digest()




