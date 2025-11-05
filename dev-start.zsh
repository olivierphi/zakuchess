#!/bin/zsh

# A quick script, so we can just run `source ~/_WORK/me/zakuchess-django-reboot/dev-start.zsh` to get started :-) 

# @link https://stackoverflow.com/questions/2683279/how-to-detect-if-a-script-is-being-sourced
[[ ! $ZSH_EVAL_CONTEXT =~ :file$ ]] && echo "Script must be sourced" && exit 1

cd ${0:A:h}/ # Change to the directory of the current file

# Activate Python venv:
source .venv/bin/activate
# Select Node.js version:
# nvm use - not yet :-)

alias run_in_dotenv='uv run --env-file .env.local -- '

alias uv="${PWD}/bin/uv"
alias uvx="${PWD}/bin/uvx"
alias djm='DJANGO_SETTINGS_MODULE=project.settings.development run_in_dotenv python manage.py'
alias test='DJANGO_SETTINGS_MODULE=project.settings.test run_in_dotenv pytest -x --reuse-db'
alias test-no-reuse='DJANGO_SETTINGS_MODULE=project.settings.test run_in_dotenv pytest -x'

# Show the aliases we just defined:
alias uv && alias uvx && alias djm && alias test && alias test-no-reuse
