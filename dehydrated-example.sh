#!/usr/bin/env bash

#
# Example how to deploy a DNS challenge using dehydrated DNS hook
#

set -e
set -u
set -o pipefail

case "$1" in
    "deploy_challenge")
        echo "-----BEGIN DEPLOY_CHALLENGE-----" 1>&2
        echo "add _acme-challenge.${2}. 300 in TXT \"${4}\"\n\n" 1>&2
        echo "-----BEGIN DEPLOY_CHALLENGE-----" 1>&2
        ;;
    "clean_challenge")
        echo "-----BEGIN CLEAN_CHALLENGE-----" 1>&2
        printf "delete _acme-challenge.%s. 300 in TXT \"${4}\"\n\n" 1>&2
        echo "-----END CLEAN_CHALLENGE-----" 1>&2
        ;;
    "deploy_cert")
        echo "-----BEGIN DEPLOY_CERT-----" 1>&2
        echo "domain: ${2}" 1>&2
        echo "key_file: ${3}" 1>&2
        echo "cert_file: ${4}" 1>&2
        echo "fullchain_file: ${5}" 1>&2
        echo "chain_file: ${6}" 1>&2
        echo "timestamp: ${7}" 1>&2
        echo "-----END DEPLOY_CERT-----" 1>&2
        ;;
    "unchanged_cert")
        echo "-----BEGIN UNCHANGED_CERT-----" 1>&2
        echo "domain: ${2}" 1>&2
        echo "key_file: ${3}" 1>&2
        echo "cert_file: ${4}" 1>&2
        echo "fullchain_file: ${5}" 1>&2
        echo "chain_file: ${6}" 1>&2
        echo "-----END UNCHANGED_CERT-----" 1>&2
        ;;
    *)
        echo Unknown hook "${1}"
        exit 1
        ;;
esac

exit 0