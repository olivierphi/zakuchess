#!/bin/zsh

# A quick script, so that I can just run `source ~/_WORK/me/zakuchess-astro/dev-start.zsh` to get started :-)

# @link https://stackoverflow.com/questions/2683279/how-to-detect-if-a-script-is-being-sourced
[[ ! $ZSH_EVAL_CONTEXT =~ :file$ ]] && echo "Script must be sourced" && exit 1

cd ${0:A:h}/ # Change to the directory of the current file

# Activate Python venv:
source .venv/bin/activate
# Select Node.js version:
nvm use

alias uv='bin/uv'
alias dev='make dev'
alias astro='./node_modules/.bin/astro'
alias test='pytest -x'

# Show the aliases we just defined:
alias uv && alias dev && alias astro && alias test
