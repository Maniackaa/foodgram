#!/bin/bash
gunicorn --bind 0.0.0.0:$GUNICORN_PORT foodgram.wsgi
