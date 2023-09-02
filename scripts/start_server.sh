#!/usr/bin/env sh

# That's the script we use as an entrypoint for the Docker container.
# It's a good idea to keep it as simple as possible.

# Exit script as soon as a command fails.
set -o errexit

# N.B. The following commands rely on the fact that we've
# initialised some environment variables in the Dockerfile, 
# such as DJANGO_SETTINGS_MODULE and GUNICORN_CMD_ARGS.

# TODO: remove this once we have a proper deployment pipeline
echo "Running Django migrations."
.venv/bin/python src/manage.py makemigrations --noinput

# Go!
echo "Starting Gunicorn."
.venv/bin/gunicorn project.wsgi
