#!/bin/bash
 
cd ers_backend

python manage.py migrate

# start development server on public ip interface, on port 8000
python manage.py runserver 0.0.0.0:8000
