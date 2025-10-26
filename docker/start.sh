#!/usr/bin/env bash

if [[ -f ~/.docker_custom_env ]]
then
    . ~/.docker_custom_env
elif [[ -f ~/.docker_tizy ]]
then
    . ~/.docker_tizy
fi

. $(dirname "$0")/env.sh

start=$(dirname "$0")/../../developyzer/docker/start.sh
if [[ -f ${start} ]]
then
    . ${start}
else
    echo "You need to clone git@gitlab.tizy-studio.fr/cloud/developyzer.git in the same workspace"
fi