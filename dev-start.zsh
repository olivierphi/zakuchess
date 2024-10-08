#!/bin/zsh

# A quick script, so that I can just run `source ~/_WORK/me/zakuchess/dev-start.zsh` to get started :-) 

# @link https://stackoverflow.com/questions/2683279/how-to-detect-if-a-script-is-being-sourced
[[ ! $ZSH_EVAL_CONTEXT =~ :file$ ]] && echo "Script must be sourced" && exit 1

cd ${0:A:h}/ # Change to the directory of the current file

# Activate Python venv:
source .venv/bin/activate
# Select Node.js version:
nvm use

export DJANGO_SETTINGS_MODULE=project.settings.development
alias run_in_dotenv='dotenv -f .env.local run -- '

alias uv='bin/uv'
alias djm='run_in_dotenv python src/manage.py'
alias test='DJANGO_SETTINGS_MODULE=project.settings.test run_in_dotenv pytest -x --reuse-db'
alias test-no-reuse='DJANGO_SETTINGS_MODULE=project.settings.test run_in_dotenv pytest -x'

# Show the aliases we just defined:
alias uv && alias djm && alias test && alias test-no-reuse
