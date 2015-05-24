'use strict'

### Filters ###

angular
	.module 'app.filters', []
	.filter 'interpolate', ['version', (version) ->
		(text) ->
			String(text).replace(/\%VERSION\%/mg, version)
	]
	.filter 'getByProperty', ->
		(propertyName, propertyValue, collection) ->
			i = 0
			len = collection.length
			while i < len
				return collection[i]  if collection[i][propertyName] is +propertyValue
				i++
			null

	.filter 'merge_options' ,->
		(obj1, obj2) ->
			obj3 = {}
			for attrname of obj1
				obj3[attrname] = obj1[attrname]
			for attrname of obj2
				obj3[attrname] = obj2[attrname]
			obj3

	.filter 'capitalize', ->
		(input, all) ->
			if ! !input then input.replace(/([^\W_]+[^\s-]*) */g, ((txt) ->
				txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
			)) else ''

