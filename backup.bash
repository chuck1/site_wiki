#!/bin/bash

datetime=$(date '+%Y%m%d_%H%M%S')

filename=/home/crymal/P_DRIVE/data/backup/django_work/data_$datetime.json

mkdir -p $(dirname $filename)

echo $filename

python manage.py dumpdata > $filename

