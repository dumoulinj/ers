exports.startServer = (port, path, callback) ->
	# callback doesn't take any parameters and (if provided) should be called after server is started
	# should return an instance of http.Server
	fs = require('fs')
	path = require('path')
	express  = require('express')
	http = require('http')
	app      = express()
	#var mongoose = require('mongoose');                     // mongoose for mongodb
	morgan = require('morgan')#             // log requests to the console (express4)
	bodyParser = require('body-parser')#    // pull information from HTML POST (express4)
	methodOverride = require('method-override')# // simulate DELETE and PUT (express4)

	#// configuration =================

	#mongoose.connect('mongodb://node:node@mongo.onmodulus.net:27017/uwO3mypu');     // connect to mongoDB database on modulus.io

	app.use(express.static(__dirname + '/_public'))#// set the static files location /public/img will be /img for users
	app.use(morgan('dev'))                                         #// log every request to the console
	app.use(bodyParser.urlencoded({'extended':'true'}))            #// parse application/x-www-form-urlencoded
	app.use(bodyParser.json())                                     #// parse application/json
	app.use(bodyParser.json({ type: 'application/vnd.api+json' })) #// parse application/vnd.api+json as json
	app.use(methodOverride())

	#// listen (start app with node server.js) ======================================
	#app.listen(port)
	#console.log("App listening on port "+port)


	multipart = require("connect-multiparty")
	app.use multipart(uploadDir: __dirname + '/_public')
	multipart = require("connect-multiparty")
	multipartMiddleware = multipart()
	app.post '/upload', multipartMiddleware, (req, resp) ->
		datasetsVideoPath = req.body.path
		if !fs.existsSync(datasetsVideoPath)
			fs.mkdirSync(datasetsVideoPath)
		fs.rename req.files.file.path, datasetsVideoPath + "/" + req.files.file.originalFilename, (err) ->
			throw err  if err
			console.log "File " + req.files.file.originalFilename + " correctly copied in " + datasetsVideoPath
		resp.send('ok')

	server = http.createServer(app)
	server.listen port, (error) ->
		console.log "Application started on http://localhost:" + port  unless false
		callback error, port
	server