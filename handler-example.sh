#!/usr/bin/env bash

# Note: keep stdout clean, as it may be used to pass data back in the future,
# and it is used to signal NotImplemented.
# Inspiration taken from: https://github.com/marcan/letsencrypt-external

set -e
cmd="$1"
shift

echo ">> handler-example.sh: ${cmd}" 1>&2

case "$cmd" in
    pre-perform)
        echo "-----BEGIN PRE-PERFORM-----" 1>&2
        echo "-----END PRE-PERFORM-----" 1>&2
        ;;
    perform)
        echo "-----BEGIN PERFORM-----" 1>&2
        echo "cmd: ${cmd}" 1>&2
        echo "type: ${type}" 1>&2
        echo "domain: ${domain}" 1>&2
        echo "uri: ${uri}" 1>&2
        echo "validation: ${validation}" 1>&2
        echo "key-auth: ${key_auth}" 1>&2
        echo "z_domain: ${z_domain}" 1>&2
        echo "cert_path: ${cert_path}" 1>&2
        echo "key_path: ${key_path}" 1>&2
        echo "port: ${port}" 1>&2
        echo "json: ${cbot_json}" 1>&2
        echo "-----END PERFORM-----" 1>&2
        ;;
    post-perform)
        echo "-----BEGIN POST-PERFORM-----" 1>&2
        echo "-----END POST-PERFORM-----" 1>&2
        ;;
    pre-cleanup)
        echo "-----BEGIN PRE-CLEANUP-----" 1>&2
        echo "-----END PRE-CLEANUP-----" 1>&2
        ;;
    cleanup)
        echo "-----BEGIN CLEANUP-----" 1>&2
        echo "cmd: ${cmd}" 1>&2
        echo "type: ${type}" 1>&2
        echo "domain: ${domain}" 1>&2
        echo "status: ${status}" 1>&2
        echo "token: ${token}" 1>&2
        echo "error: ${error}" 1>&2
        echo "json: ${cbot_json}" 1>&2
        echo "-----END CLEANUP-----" 1>&2
        ;;
    post-cleanup)
        echo "-----BEGIN POST-CLEANUP-----" 1>&2
        echo "-----END POST-CLEANUP-----" 1>&2
        ;;
    *)
        # Signalizing the given command is not implemented
        echo "NotImplemented"
        exit 1
        ;;
esac
