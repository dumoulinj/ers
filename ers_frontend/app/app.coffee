'use strict'

angular
	.module 'app', [
		'ngCookies'
		'ngResource'
		'ngAnimate'
		'ui.router'
		'mgcrea.ngStrap'
		'angular-loading-bar'
		'restangular'
		'SwampDragonServices'
		'partials'
		'app.directives'
		'app.filters'
		'app.services'
		'app.testing'
		'app.datasets'
		'app.video'
		'nvd3ChartDirectives'
		'com.2fdevs.videogular'
		'com.2fdevs.videogular.plugins.controls'
		'com.2fdevs.videogular.plugins.overlayplay'
		'com.2fdevs.videogular.plugins.buffering'
		'app.home'
		'angularFileUpload'
		'smart-table'
		'angularSpinner'
		'checklist-model'
		'hue'
	]

	.constant("ComputingStateType", {
		"NO": 0,
		"IN_PROGRESS": 1,
		"SUCCESS": 2,
		"FAILED": 3,
		"WARNING": 4
	})

	.run (Restangular) ->
		# TODO: change base REST api url here:
		Restangular.setBaseUrl('http://localhost:8000')

		# Self reference
		Restangular.setRestangularFields({
			selfLink: 'url'
		})

		Restangular.setRequestSuffix('/')
