Project homepage: http://ers.humantech.institute/#/

# e*RS*
e*RS* is an emotion recognition system dedicated to researchers, whose purpose is to help them with emotion recognition in movies tasks.

To see what you can do with e*RS*, have a look to http://ers.humantech.institute/#/presentation

## Installation
e*RS* works on Linux and Mac OS X. (it is planned to dockerize it soon)

The script install_ers_ubuntu.sh is provided to install all dependencies on Ubuntu (tested on Ubuntu 14.10). Run it with sudo.

If you want to manually install the system, follow these instructions:

### Dependencies
Install main dependencies (many of these dependencies are available on Mac OS X with macport or brew):
* Python 2.7
* MySQL 5.5
* OpenCV 2.4.9 with python support (http://sourceforge.net/projects/opencvlibrary/files/opencv-unix/2.4.9/opencv-2.4.9.zip/download)
* OpenSMILE 2.0-rc1 (http://sourceforge.net/projects/opensmile/files/opensmile-2.0-rc1.tar.gz)
* ffmpeg (https://www.ffmpeg.org/)
* Redis (http://redis.io/)
* SoX 14.4.1 (http://sourceforge.net/projects/sox/files/sox/)
* pip (https://pip.pypa.io/en/latest/installing.html)
* git (http://git-scm.com/)
* NodeJS (https://nodejs.org/)
* npm (https://nodejs.org/download/)

Then, install python packages:
```shell
sudo pip install -r requirements.txt
```

Then, install web packages:
```shell
cd ers_frontend
sudo npm install
bower install
```

### Database
Create a database with information specified in ers_backend/ers_backend/settings.py in the Database configuration part. Default are:
* Database name : ers_backend_db
* User          : root
* Password      : root

Control that the user root has all privileges on this database.

## Running e*RS*
You can use the provided scripts to run the required services. Be sure to call each script from this path, and not from the script folder.

### 1. Celery workers (using Redis broker)
```shell
./scripts/run_redis.sh
```

```shell
./scripts/rund_celery.sh
```

### 2. Django REST server
```shell
./scripts/run_django.sh
```

### 3. SwampDragon WebSockets server
```shell
./scripts/run_swampdragon.sh
```

### 4. Frontend web server
```shell
./scripts/run_brunch.sh
```

## Test e*RS*
### Backend
We don't provide test videos for legal issues. You have to add test videos manually (use small .avi videos like 30 seconds maximum).

First, create the following folders:
```
$ers_installation_path$/datasets/test_dataset
$ers_installation_path$/datasets/test_dataset/video
$ers_installation_path$/datasets/test_dataset/video/anger
$ers_installation_path$/datasets/test_dataset/video/neutral
```

Then, add test videos:
```
$ers_installation_path$/datasets/test_dataset/video/1_shot.avi
$ers_installation_path$/datasets/test_dataset/video/anger/anger.avi
$ers_installation_path$/datasets/test_dataset/video/neutral/neutral.avi
```

1_shot.avi should contain 1 and only 1 shot boundary (an easy one, hard cut).

Then, launch the Django project unit tests to verify that the backend is working:
```shell
cd ers_backend
python manage.py test
```

### Frontend
Open your web browser and go to http://localhost:3333/#/home to verify that the web application is accessible.

Then go to the page "Test server", and click on each buttons to test the connection with the different backend services.
![Alt text](/test_server.png?raw=true "Test server result")

## License
This software is released under the [MIT License](https://github.com/dumoulinj/ers/blob/master/LICENSE).

