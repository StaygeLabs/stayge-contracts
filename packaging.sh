#!/bin/bash

if [ "$1" = "stg" ]; then
    echo "Target : $1"
    cd "$1"
    zip ../dist/stg.zip *.py *.json
elif [ "$1" = "act" ]; then
    echo "Target : $1"
    cd "$1"
    zip ../dist/act.zip *.py *.json
else
    echo "Usage: packaging.sh [stg|act]"
fi
