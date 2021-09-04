#!/usr/bin/env bash
gunicorn --bind 0.0.0.0:80 --workers 2 --log-level error --access-logfile /var/log/access.log --error-logfile /var/log/error.log wsgi:app
