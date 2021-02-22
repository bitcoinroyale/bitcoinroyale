#!/bin/sh
set -e

# display info about elcash revision
echo "BitcoinVault revision: ${BVAULTD_COMMIT}"

# Prepare configuration from templates
dockerize -template /templates/bvaultd.conf.tmpl:/bitcoinvault/bvaultd.conf

exec "$@"
