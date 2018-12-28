#!/bin/bash

if [ "$1" = "testnet" ]; then
    ICON_ENDPOINT=$1
else
    ICON_ENDPOINT="tbears"
fi

echo "ICON_ENDPOINT : $ICON_ENDPOINT"

export ICON_ENDPOINT=$ICON_ENDPOINT

#python -m unittest discover
python -m unittest tests/test_donation.py
