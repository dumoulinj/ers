'use strict'

### Directives ###

# register the module with Angular
angular
	.module 'app.directives', ['app.services']
	.directive 'appVersion', ['version', (version) ->
		(scope, elm, attrs) ->
			elm.text(version)
	]
	.directive 'back', ['$window', ($window) ->
		{
			restrict: 'A',
			link: (scope, elem, attrs) ->
				elem.bind('click', () ->
					$window.history.back()
				)
		}
	]
	.directive "errSrc", ->
		link: (scope, element, attrs) ->
			element.bind "error", ->
				attrs.$set "src", attrs.errSrc  unless attrs.src is attrs.errSrc
	.directive "computingState", () ->
		restrict: 'E'
		scope: {
			state: '='
		}
		templateUrl: '/partials/computing-state.html'