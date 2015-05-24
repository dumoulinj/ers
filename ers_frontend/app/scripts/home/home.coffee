'use strict'

# app.home Module
#
# @abstract Home controllers


angular
.module 'app.home', []
	.config ($stateProvider, $urlRouterProvider) ->
		$stateProvider
			.state 'home', {
				url: '/home',
				templateUrl: '/partials/home.html',
				controller: 'HomeCtrl'
			}
			.state 'about', {
				url: '/about',
				templateUrl: '/partials/about.html',
				controller: 'AboutCtrl'
			}

	.controller 'HomeCtrl',($scope) ->
		$scope.features = [
			{
				"text": "Video datasets management"
				"icon": "glyphicon-wrench"
				"subFeatures" : [
					{
						"text": "Create/Update/Delete datasets"
					}
					{
						"text": "Scan video folder for existing videos"
					}
					{
						"text": "Upload videos to the server by drag & drop"
					}
					{
						"text": "Bulk upload videos of a same emotion class"
					}
					{
						"text": "Prepare videos (conversion in a good video format, extract audio)"
					}
				]
			}
			{
				"text": "Shot boundaries detection"
				"icon": "glyphicon-camera"
				"subFeatures" : [
					{
						"text": "Configuration (algorithms, thresholds, ...)"
					}
					{
						"text": "Evaluation against ground truth (csv list of shot boundaries)"
					}
					{
						"text": "Dynamic visualization (linked with the video) of the detected shot boundaries with color feedback to differentiate between true positives, false positives and misses"
					}
				]
			}
			{
				"text": "Features extraction"
				"icon": "glyphicon-tasks"
				"subFeatures" : [
					{
						"text": "Audio and visual features extraction"
					}
					{
						"text": "State of the art audio features extraction, with functionals (mean, min, max, skewness, etc.) "
					}
					{
						"text": "Dynamic visualization (linked with the video) of extracted features visualization"
					}
				]
			}
			{
				"text": "Emotion modeling"
				"icon": "glyphicon-star-empty"
				"subFeatures" : [
					{
						"text": "Arousal modeling, with dynamic visualization linked to the video"
					}
					{
						"text": "Valence modeling (coming soon)"
					}
					{
						"text": "Emotion classification (coming soon)"
					}
				]
			}
		]

	.controller 'AboutCtrl',($scope, $timeout) ->
		# Initialize tooltips on buttons
		$timeout(() ->
			$('[data-toggle="tooltip"]').tooltip()
		, 500)

		$scope.about = {
			mail: 'joel.dumoulin@hefr.ch'
			homepage: 'http://joel.dumoulin.ch'
			linkedIn: 'http://ch.linkedin.com/pub/joël-dumoulin/60/b58/814/'
			scholar: 'https://scholar.google.ch/citations?user=4qMFFxkAAAAJ&hl=fr&oi=ao'
			academia: 'https://eia-fr.academia.edu/JoëlDumoulin'
			researchGate: 'https://www.researchgate.net/profile/Joel_Dumoulin'
		}

		licenses = {
			MIT: "MIT License",
			BSD: "BSD",
			BSD3: "3-clause BSD License",
			APACHE2: "Apache License, Version 2.0",
			GNU: "GNU Lesser General Public License (LGPL) version 2.1"
		}

		$scope.usedProjects = {
			"frontend": [
				{
					"name": "Angular JS",
					"url": "https://angularjs.org/"
					"license": licenses.MIT
				},
				{
					"name": "Jade",
					"url": "http://jade-lang.com/"
					"license": licenses.MIT
				},
				{
					"name": "CoffeeScript",
					"url": "http://coffeescript.org/"
					"license": licenses.MIT
				}
				{
					"name": "Brunch.io",
					"url": "http://brunch.io/"
					"license": licenses.MIT
				},
				{
					"name": "Node.js",
					"url": "https://nodejs.org/"
					"license": licenses.MIT
				},
				{
					"name": "Bower",
					"url": "http://bower.io/"
					"license": licenses.MIT
				},
				{
					"name": "Swampdragon",
					"url": "https://github.com/inaffect-ag/swampdragon-bower"
					"license": "Copyright (c) 2014, jonas hagstedt All rights reserved"
				},
				{
					"name": "Bootstrap",
					"url": "http://getbootstrap.com/"
					"license": licenses.MIT
				},
				{
					"name": "Bootswatch Paper theme",
					"url": "https://bootswatch.com/paper/"
					"license": licenses.MIT
				},
				{
					"name": "Fontawesome",
					"url": "http://fortawesome.github.io/Font-Awesome/"
					"license": licenses.MIT
				},
				{
					"name": "Jquery",
					"url": "https://jquery.com/"
					"license": licenses.MIT
				},
				{
					"name": "lodash",
					"url": "https://lodash.com/"
					"license": licenses.MIT
				},
				{
					"name": "D3.js",
					"url": "http://d3js.org/"
					"license": licenses.BSD
				},
				{
					"name": "nvd3",
					"url": "http://nvd3.org/"
					"license": licenses.APACHE
				},
				{
					"name": "Angular nvd3 directives",
					"url": "https://github.com/angularjs-nvd3-directives/angularjs-nvd3-directives"
					"license": licenses.APACHE
				},
				{
					"name": "Restangular",
					"url": "https://github.com/mgonto/restangular"
					"license": licenses.MIT
				},
				{
					"name": "Angular ui router",
					"url": "https://github.com/angular-ui/ui-router"
					"license": licenses.MIT
				},
				{
					"name": "AngularStrap",
					"url": "http://mgcrea.github.io/angular-strap/"
					"license": licenses.MIT
				},
				{
					"name": "Angular motion",
					"url": "https://github.com/mgcrea/angular-motion"
					"license": licenses.MIT
				},
				{
					"name": "Angular loading bar",
					"url": "http://chieffancypants.github.io/angular-loading-bar/"
					"license": licenses.MIT
				},
				{
					"name": "Angular smart table",
					"url": "http://lorenzofox3.github.io/smart-table-website/"
					"license": licenses.MIT
				},
				{
					"name": "Angular file upload",
					"url": "https://github.com/danialfarid/ng-file-upload"
					"license": licenses.MIT
				},
				{
					"name": "Angular spinner",
					"url": "https://github.com/urish/angular-spinner"
					"license": licenses.MIT
				},
				{
					"name": "Videogular",
					"url": "http://www.videogular.com/"
					"license": licenses.MIT
				},
				{
					"name": "Checklist-model",
					"url": "http://vitalets.github.io/checklist-model/"
					"license": licenses.MIT
				}

			],
			"backend": [
				{
					"name": "Django",
					"url": "https://www.djangoproject.com/"
					"license": licenses.BSD3
				},
				{
					"name": "Django Rest Framework",
					"url": "http://www.django-rest-framework.org/"
					"license": "Copyright (c) 2011-2015, Tom Christie All rights reserved."
				},
				{
					"name": "Swampdragon",
					"url": "http://swampdragon.net/"
					"license": licenses.BSD
				},
				{
					"name": "OpenCV",
					"url": "http://opencv.org/"
					"license": licenses.BSD3
				},
				{
					"name": "FFmpeg",
					"url": "https://www.ffmpeg.org/"
					"license": licenses.GNU
				},
				{
					"name": "OpenSMILE",
					"url": "http://www.audeering.com/research/opensmile"
					"license": "audEERING Research License Agreement"
				},
				{
					"name": "Numpy",
					"url": "http://www.numpy.org/"
					"license": licenses.BSD
				},
				{
					"name": "Django enumfield",
					"url": "https://github.com/5monkeys/django-enumfield"
					"license": licenses.MIT
				},
				{
					"name": "Django annoying",
					"url": "https://github.com/skorokithakis/django-annoying"
					"license": licenses.BSD
				},
				{
					"name": "Django cors headers",
					"url": "https://github.com/ottoyiu/django-cors-headers"
					"license": licenses.MIT
				},
				{
					"name": "Celery",
					"url": "http://www.celeryproject.org/"
					"license": licenses.BSD
				},
				{
					"name": "Pillow",
					"url": "https://github.com/python-pillow/Pillow"
					"license": "Standard PIL License"
				},
				{
					"name": "Python video converter",
					"url": "https://github.com/senko/python-video-converter"
					"license": "Not specified"
				}
			]
		}