#!/usr/bin/env bash
gunicorn --bind 0.0.0.0:5000 --workers 2 --log-level error --error-log-file /app/log/error.log wsgi:app
