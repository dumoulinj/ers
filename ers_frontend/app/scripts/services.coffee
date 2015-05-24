'use strict'

# app.services Module
#
# @abstract Services definition for RestFUL part

`function getCookie(name) {
	var cookieValue = null;
	if (document.cookie && document.cookie != '') {
		var cookies = document.cookie.split(';');
		for (var i = 0; i < cookies.length; i++) {
			var cookie = cookies[i].trim();
			// Does this cookie string begin with the name we want?
			if (cookie.substring(0, name.length + 1) == (name + '=')) {
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
}`

angular
	.module 'app.services', []
	.config ["$httpProvider", (provider) ->
		provider.defaults.headers.post["X-CSRFToken"] = getCookie('csrftoken')
		#provider.defaults.useXDomain = true;
		#delete provider.defaults.headers.common['X-Requested-With'];
		return
	]
	.factory 'DatasetsResource', (Restangular) ->
		Restangular.service('dataset_manager/datasets')
	.factory 'VideosResource', (Restangular) ->
		Restangular.service('dataset_manager/videos')

