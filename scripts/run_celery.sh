#!/bin/bash

cd ers_backend

# run Celery worker for our project
celery -A ers_backend worker --loglevel=info
