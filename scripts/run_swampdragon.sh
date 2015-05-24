#!/bin/bash
 
cd ers_backend

python manage.py migrate

# start server.py for swampdragon instance
python server.py