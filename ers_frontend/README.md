# e*RS* system frontend application
This AngularJS application is the frontend web application for the e*RS* system. It is managed with brunch.io.
It is based on the angular-brunch-seed skeleton : https://github.com/scotch/angular-brunch-seed.

## Launch the application in development
```
brunch watch -s
``

## Directory Layout
    _public/                  --> Contains generated file for servering the app
                                  These files should not be edited directly
    app/                      --> All of the files to be used in production

      assets                  --> A place for static assets. These files will be copied to
                                  the public directory un-modified.
        customScripts/        --> Additional javascript scripts, not managed by bower or npm
        fonts/                --> Font files

      partials/               --> Jade partial files. This file will be converted to HTML upon save.
        nav.jade                  If you are using HTML this directory will not be present. You will find the template file
        partial1.jade             in the `app/assets/partials` directory instead.
        partial2.jade             If you are using Jade these file will be converted to HTML and compiled into 
                                  `_public/js/partials.js` upon save.
      scripts/                --> Base directory for app scripts
        controllers.js        --> Application controllers
        directives.js         --> Custom angular directives
        filters.js            --> Custom angular filters
        services.js           --> Custom angular services

      styles/                 --> All custom styles. Acceptable files types inculde:
                                  less, and stylus
        app.less              --> A file for importing styles.
      app.coffee              --> Application definition and routes.
      index.jade              --> Index file. This will be converted to assets/index.html on save

    bower_components/         --> The bower_components dirctory is populated by Bower.
                                  It contains  Angular, Bootstrap Font-Awesome 
                                  and other utility files.

    node_modules              --> NodeJS modules

    scripts/                  --> Handy shell scripts
      compile-html.sh         --> Compiles *.jade file to *.html file and places them in app/assets
      compile-tests.sh        --> Compiles coffeescript test to javascript
      development.sh          --> Compiles files and watches for changes
      init.sh                 --> Installs node modules
      production.sh           --> Compiles and compresses files for production use
      server.sh               --> Runs a development server at `http://localhost:3333`
      test.sh                 --> Runs all unit tests
      test-e2e.sh             --> Runs all end-to-end tests using Testacular

    test/                     --> Test source files and libraries
      app/
        scenarios.coffee      --> End-to-end specs
      unit/
        controllers.spec.js   --> Specs for controllers
        directives.spec.js    --> Specs for directives
        filters.spec.js       --> Specs for filters
        services.spec.js      --> Specs for services
      vendor/
        test-results.xml      --> Karma test resuls
        karma-e2e.conf.js     --> Karma end-to-end tests config
        karma.conf.js         --> Karma unit tests config

    vendor/                   --> The vendor directory is can be used for 3rd Party libraries.
                                  Any files located in this directory will be included in js/vendor.js
  bower.json                  --> Bower component config
  config.coffee               --> Brunch config
  package.json                --> node modules config

  server.coffe                --> Custom server, allowing the file-upload feature

