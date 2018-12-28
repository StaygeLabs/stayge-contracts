#!/bin/bash

if [ "$1" = "testnet" ]; then
    echo "Mode : testnet"
    tbears deploy -m update -k conf/test_owner.keystore donation -p test123! -c conf/update_donation_config-testnet.json
else
    echo "Mode : tbears"
    tbears deploy -m update -k conf/test_owner.keystore donation -p test123! -c conf/update_donation_config-tbears.json
fi





