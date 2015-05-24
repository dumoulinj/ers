# e*RS* system backend application
This Django application is the backend of the e*RS* system.

## Launch the application in development
```shell
python manage.py runserver
````

```shell
python server.py
````

```shell
celery -A ers_backend worker --loglevel=info
```

## Directory Layout
    arousal_modeler/    --> App for arousal modeling
    audio_processor/    --> App for processing of audio features
    dataset_manager/    --> Main app, for managing the videos datasets
    ers_backend/        --> ers_backend project directory, containing the settings.py and urls.py
    testing/            --> App for the testing server page
    video_processor/    --> App for processing of video features

    manage.py           --> Django manage.py script
    server.py           --> Python script used to launch the SwampDragon websockets endpoint

