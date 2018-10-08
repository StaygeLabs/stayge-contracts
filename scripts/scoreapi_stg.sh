#!/bin/bash

if [ "$1" = "testnet" ]; then
    echo "Mode : testnet"
    tbears scoreapi -u https://bicon.net.solidwallet.io/api/v3 cx40ba15981ad7b0d7db0ebbaa01280cf8495cec34
else
    echo "Mode : tbears"
    tbears scoreapi -u http://127.0.0.1:9000/api/v3 cx63eb7813408055717194f2f25aaeb3e837a3858d
fi



