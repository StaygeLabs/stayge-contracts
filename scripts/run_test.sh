#!/bin/bash

if [ "$1" = "testnet" ]; then
    ICON_ENDPOINT=$1
else
    ICON_ENDPOINT="tbears"
fi

echo "ICON_ENDPOINT : $ICON_ENDPOINT"

export ICON_ENDPOINT=$ICON_ENDPOINT

cd ..;python -m unittest discover
