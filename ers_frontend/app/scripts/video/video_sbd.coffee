angular
	.module 'app.video'
	.controller 'SbdCtrl', ($scope, $timeout, video, sbdResults, $state, $modal, $dragon, $alert, Restangular, ComputingStateType) ->
		# Initialize tooltips on buttons
		$timeout(() ->
			$('[data-toggle="tooltip"]').tooltip()
		, 500)


		$scope.sbdResults = sbdResults
		$scope.displayedSbdResults = [].concat($scope.sbdResults)

		$scope.video = video

		$scope.csvText = $scope.video.shot_boundaries_ground_truth

		$scope.$parent.displayVideo = true

		$scope.showGroundTruth = false

		$scope.showGT = () ->
			$scope.showGroundTruth = !$scope.showGroundTruth

		$scope.showSbdResultRemoveButton = () ->
			_.size($scope.sbdResults) > 1

		# Remove shot
		removeSbdResultModalScope = $scope.$new(true)
		removeSbdResultModalScope.title = "Confirmation"
		removeSbdResultModalScope.content
		removeSbdResultModalScope.sbdResult
		removeSbdResultModalScope.buttons = [
			{
				text: "Remove",
				class: "btn-danger",
				callback: () -> $scope.removeSbdResult(removeSbdResultModalScope.sbdResult)
			}
		]

		removeSbdResultModal = $modal({
			scope: removeSbdResultModalScope,
			template: "/partials/modal.tpl.html",
			show: false
		})

		$scope.showRemoveSbdResultModal = (sbdResult) ->
			removeSbdResultModalScope.sbdResult = sbdResult
			removeSbdResultModalScope.content = "Are your sure you want to remove this shot boundaries detection result ? "
			removeSbdResultModal.$promise.then(removeSbdResultModal.show)

		$scope.removeSbdResult = (sbdResult) ->
			sbdResult.remove().then(()->
				$scope.sbdResults = _.without($scope.sbdResults, sbdResult)
			)

		updateSbdGtModalScope = $scope.$new(true)
		updateSbdGtModalScope.title = "Modify"
		updateSbdGtModalScope.content = "Modify the shot boundaries groung truth for this video."
		updateSbdGtModalScope.csvVal = $scope.video.shot_boundaries_ground_truth
		updateSbdGtModalScope.buttons = [
			{
				text: "Save",
				class: "btn-success",
				callback: (data) -> $scope.sendCSV(data)
			}
		]

		updateSbdGtModal = $modal({
			scope: updateSbdGtModalScope,
			template: "/partials/modal.updateSbdGroundTruth.html",
			show: false
		})

		$scope.showUpdateSbdGtModal = () ->
			updateSbdGtModal.$promise.then(updateSbdGtModal.show)

		#Send groundTruth
		$scope.sendCSV = (data) ->
			$scope.video.patch({shot_boundaries_ground_truth:JSON.parse([data['csv']])})
			$scope.video.shot_boundaries_ground_truth = JSON.parse(data['csv'])

		# Evaluate video shot
		$scope.evaluatingSbd = false
		$scope.evaluateSbd = () ->
			$scope.evaluatingSbd = true
			$dragon.callRouter('evaluate_sbd', 'video', {video_id:$scope.video.id}).then((message) ->
				$scope.evaluatingSbd = false

				# Reload sbd results
				sbdResults = []
				_.forEach($scope.video.shots_detections, (shotsUrl)->
					sbdResult = Restangular.oneUrl('video_shots_results', shotsUrl).get().then((sbdResult)->
						sbdResults.push(sbdResult)
					)
				)

				$scope.sbdResults = sbdResults

				if parseInt(message.data.state) == ComputingStateType.SUCCESS
					title = "Confirmation"
					content = "Shot boundaries detection results sucessfully evaluated!"
					type = "success"
					duration = 4
				else
					title = "Error"
					content = "An error occured during the evaluation of the shot boundaries detection results..."
					type = "danger"
					duration = false

				$alert({
					title: title,
					content: content,
					placement: 'top-right',
					type: type,
					duration: duration,
					show: true
				})
			)