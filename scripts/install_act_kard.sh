#!/bin/bash

if [ "$1" = "testnet" ]; then
    echo "Mode : testnet"
    tbears deploy -m install -k ../conf/test_owner.keystore stg -p test123! -c ../conf/install_act_kard_config-testnet.json
else
    echo "Mode : tbears"
    tbears deploy -m install -k ../conf/test_owner.keystore stg -p test123! -c ../conf/install_act_kard_config-tbears.json
fi

