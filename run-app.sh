#!/usr/bin/env bash
gunicorn --bind 0.0.0.0:80 --workers 2 --log-level error --access-logfile /var/log/vss365today-api.gunicorn.access.log --error-logfile /var/log/vss365today-api.gunicorn.error.log wsgi:app
