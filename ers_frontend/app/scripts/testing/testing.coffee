'use strict'

# app.testing Module
#
# @abstract Testing controllers


angular
.module 'app.testing', []
.config ($stateProvider, $urlRouterProvider) ->
	$stateProvider
	.state 'testing', {
		url: '/testing',
		templateUrl: '/partials/testing.html',
		controller: 'TestingCtrl',
	}

.controller 'TestingCtrl',($scope, $dragon, ComputingStateType, Restangular) ->
	# Check connection with django rest framework
	$scope.testDRFState = ComputingStateType.NO
	$scope.testDRF = () ->
		$scope.testDRFState = ComputingStateType.IN_PROGRESS
		try
			Restangular.one('testing/test_server').get().then((response) ->
				$scope.testDRFState = response.state
			)
		catch
			$scope.testDRFState = ComputingStateType.FAILED

	# Check connection with swampdragon server
	$scope.testDragonState = ComputingStateType.NO
	$scope.testDragon = () ->
		$scope.testDragonState = ComputingStateType.IN_PROGRESS
		try
			$dragon.callRouter('test', 'test_server').then((response) ->
				$scope.testDragonState = response.data.state
			)
		catch
			$scope.testDragonState = ComputingStateType.FAILED

	# Check connection with celery broker
	$scope.testCeleryState = ComputingStateType.NO
	$scope.testCelery = () ->
		$scope.testCeleryState = ComputingStateType.IN_PROGRESS
		try
			$dragon.callRouter('test_celery', 'test_server').then((response) ->
				$scope.testCeleryState = response.data.state
			)
		catch
			$scope.testCeleryState = ComputingStateType.FAILED