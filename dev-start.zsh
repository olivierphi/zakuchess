#!/bin/zsh

# A quick script, so that I can just run `source ~/_WORK/me/zakuchess/dev-start.zsh` to get started :-) 

# @link https://stackoverflow.com/questions/2683279/how-to-detect-if-a-script-is-being-sourced
[[ ! $ZSH_EVAL_CONTEXT =~ :file$ ]] && echo "Script must be sourced" && exit 1

cd ${0:A:h}/ # Change to the directory of the current file

nvm use

export PATH=${PWD}/node_modules/.bin:${PATH}
echo "Prepended the current 'node_modules/.bin' folder to the PATH."
