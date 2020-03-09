# External authenticator for Certbot


[![Build Status](https://travis-ci.org/EnigmaBridge/certbot-external-auth.png?branch=master)](https://travis-ci.org/EnigmaBridge/certbot-external-auth})


Automation - the main goal of letsencrypt is to make certificate
management hassle-free. It works like that in most situations but each
user has to deal with its own network configuration (NAT, firewalls,
DNS, proxy, ...). The more mechanisms we have for verifying domain
control, the easier the letsencrypt use becomes.

The biggest hassle with letsencrypt is verification of domain control as
it requires your server to talk to letsencrypt servers and respond to
challenges provided (changing DNS records, or adding files to certain
locations). This process is necessary is it prevents random people
getting certificates for your own domain. This plugin helps with domain
verification process. It offers three modes:

1. JSON mode - its output is in JSON format that can be processed by the
   certbot caller (e.g., Ansible).
2. Handler mode - when it provides data for external authentication
   programs - e.g., [Dehydrated](https://github.com/lukas2511/dehydrated)
   that
   supports DNS updates for a number of registrars - here is the
   [list](https://github.com/lukas2511/dehydrated/wiki/Examples-for-DNS-01-hooks).
3. Manual mode - a fallback option when no automation is available and
   users have to do some changes (e.g., DNS updates) by hand.

We also support challenges for all three verification protocols:

-  DNS
-  HTTP

This plugin does not communicate with letsencrypt but it provides data
for letsencrypt clients in the correct format so the domain control
verification can be automated.

## Installation - pip
s

    pip install certbot
    pip install certbot-ext-auth

## Usage

Here is an example of a typical use:

    certbot --text --agree-tos --email you@example.com \
            --expand --renew-by-default \
            --configurator certbot-external-auth:out \
            --certbot-external-auth:out-public-ip-logging-ok \
            -d example.com certonly

There are 3 main modes of operation:

-  JSON mode (default)
-  Text mode - fallback to the ``manual.py`` operation
-  Handler mode - auth performed by an external program. Supports
   [Dehydrated](https://github.com/lukas2511/dehydrated) and
   augmented mode.

If you want it to use as Authenticator and Installer, use
``--configurator certbot-external-auth:out`` certbot flag, for
Authenticator only use ``-a certbot-external-auth:out``

In authenticator mode one can use certbot actions ``certonly`` or
``renew``. If installer mode is enabled too use ``run`` action - typical
for [Dehydrated](https://github.com/lukas2511/dehydrated) hooks.

### JSON Mode

JSON mode produces one-line JSON objects (``\n`` separated) with a
challenge to process by the invoker on the STDOUT.

After the challenge is processed, the invoker is supposed to send a new
line ``\n`` character to the STDIN to continue with the process.

*Note JSON mode produces also another JSON objects besides challenges,
e.g., cleanup and reports. The ``\n`` is expected only for challenges
(perform/validate step).*

If plugin is installed also as an Installer (or Configurator), it
provides also commands related to the certificate installation.

Reporter was substituted to produce JSON logs so STDOUT is JSON only.

## Arguments


    --certbot-external-auth:out-public-ip-logging-ok
            Skips public IP query check, required for JSON mode

    --certbot-external-auth:out-text-mode
            Defaults to manual.py text stdout, no JSON

    --certbot-external-auth:out-handler
            If set, enables handler mode. Commands are 
            sent to the handler script for processing. 
            Arguments are sent in ENV.
            
    --certbot-external-auth:out-dehydrated-dns
            If handler mode is enabled, compatibility 
            with dehydrated-dns hooks is enabled

## Errors


Processing errors are indicated by non-zero return codes returned by
this plugin.

## Examples

The particular examples of verification methods and handler follows. At
first the JSON mode examples are given, then handler examples follow.

Please note there is a ``--staging`` argument in the following commands, meaning you will get just testing LetsEncrypt certificate.
Once this works for you, remove this argument so you get proper valid LetsEncrypt certificate.

### DNS

Run the certbot with the following command:

    certbot --staging \
            --text --agree-tos --email you@example.com \
            --expand --renew-by-default \
            --configurator certbot-external-auth:out \
            --certbot-external-auth:out-public-ip-logging-ok \
            -d "bristol3.pki.enigmabridge.com" \
            -d "bs3.pki.enigmabridge.com" \
            --preferred-challenges dns \
            certonly 2>/dev/null

Stderr contains string log / report, not in JSON format.

Stdout:


    {"cmd": "perform_challenge", "type": "dns-01", "domain": "bristol3.pki.enigmabridge.com", "token": "_QLSFTRw6qbQaN7gTglBYZuU1L7KAP-bXB_41CAnAvU", "validation": "667drNmQL3vX6bu8YZlgy0wKNBlCny8yrjF1lSaUndc", "txt_domain": "_acme-challenge.bristol3.pki.enigmabridge.com", "key_auth": "_QLSFTRw6qbQaN7gTglBYZuU1L7KAP-bXB_41CAnAvU.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0"}

    {"cmd": "perform_challenge", "type": "dns-01", "domain": "bs3.pki.enigmabridge.com", "token": "3gJ87yANDpmuuKVL2ktfQ0_qURQ3mN0IfqgbTU_AGS4", "validation": "ejEDZXYEeYHUxqBAiX4csh8GKkeVX7utK6BBOBshZ1Y", "txt_domain": "_acme-challenge.bs3.pki.enigmabridge.com", "key_auth": "3gJ87yANDpmuuKVL2ktfQ0_qURQ3mN0IfqgbTU_AGS4.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0"}

    {"cmd": "cleanup", "type": "dns-01", "status": "pending", "domain": "bristol3.pki.enigmabridge.com", "token": "_QLSFTRw6qbQaN7gTglBYZuU1L7KAP-bXB_41CAnAvU", "validation": "667drNmQL3vX6bu8YZlgy0wKNBlCny8yrjF1lSaUndc", "key_auth": "_QLSFTRw6qbQaN7gTglBYZuU1L7KAP-bXB_41CAnAvU.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "validated": null, "error": null}
    {"cmd": "cleanup", "type": "dns-01", "status": "pending", "domain": "bs3.pki.enigmabridge.com", "token": "3gJ87yANDpmuuKVL2ktfQ0_qURQ3mN0IfqgbTU_AGS4", "validation": "ejEDZXYEeYHUxqBAiX4csh8GKkeVX7utK6BBOBshZ1Y", "key_auth": "3gJ87yANDpmuuKVL2ktfQ0_qURQ3mN0IfqgbTU_AGS4.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "validated": null, "error": null}
    {"cmd": "report", "messages": [{"priority": 1, "on_crash": true, "lines": ["Congratulations! Your certificate and chain have been saved at /etc/letsencrypt/live/bristol3.pki.enigmabridge.com/fullchain.pem. Your cert will expire on 2017-01-25. To obtain a new or tweaked version of this certificate in the future, simply run certbot again. To non-interactively renew *all* of your certificates, run \"certbot renew\""]}]}

After ``{"cmd": "validate"}`` message the client waits on ``\n`` on the
standard input to continue with the validation.

### DNS installer


Certbot is running with action ``run`` which causes also Installer
plugin part to work. The installer is the same for all validation modes
so it is demonstrated only once.

    certbot --staging \
            --text --agree-tos --email you@example.com \
            --expand --renew-by-default \
            --configurator certbot-external-auth:out \
            --certbot-external-auth:out-public-ip-logging-ok \
            -d "bristol3.pki.enigmabridge.com" \
            -d "bs3.pki.enigmabridge.com" \
            --preferred-challenges dns \
            run 2>/dev/null

Stdout:

    {"cmd": "perform_challenge", "type": "dns-01", "domain": "bristol3.pki.enigmabridge.com", "token": "_QLSFTRw6qbQaN7gTglBYZuU1L7KAP-bXB_41CAnAvU", "validation": "667drNmQL3vX6bu8YZlgy0wKNBlCny8yrjF1lSaUndc", "txt_domain": "_acme-challenge.bristol3.pki.enigmabridge.com", "key_auth": "_QLSFTRw6qbQaN7gTglBYZuU1L7KAP-bXB_41CAnAvU.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0"}

    {"cmd": "perform_challenge", "type": "dns-01", "domain": "bs3.pki.enigmabridge.com", "token": "3gJ87yANDpmuuKVL2ktfQ0_qURQ3mN0IfqgbTU_AGS4", "validation": "ejEDZXYEeYHUxqBAiX4csh8GKkeVX7utK6BBOBshZ1Y", "txt_domain": "_acme-challenge.bs3.pki.enigmabridge.com", "key_auth": "3gJ87yANDpmuuKVL2ktfQ0_qURQ3mN0IfqgbTU_AGS4.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0"}

    {"cmd": "cleanup", "type": "dns-01", "status": "pending", "domain": "bristol3.pki.enigmabridge.com", "token": "_QLSFTRw6qbQaN7gTglBYZuU1L7KAP-bXB_41CAnAvU", "validation": "667drNmQL3vX6bu8YZlgy0wKNBlCny8yrjF1lSaUndc", "key_auth": "_QLSFTRw6qbQaN7gTglBYZuU1L7KAP-bXB_41CAnAvU.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "validated": null, "error": null}
    {"cmd": "cleanup", "type": "dns-01", "status": "pending", "domain": "bs3.pki.enigmabridge.com", "token": "3gJ87yANDpmuuKVL2ktfQ0_qURQ3mN0IfqgbTU_AGS4", "validation": "ejEDZXYEeYHUxqBAiX4csh8GKkeVX7utK6BBOBshZ1Y", "key_auth": "3gJ87yANDpmuuKVL2ktfQ0_qURQ3mN0IfqgbTU_AGS4.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "validated": null, "error": null}
    {"cmd": "deploy_cert", "domain": "bristol3.pki.enigmabridge.com", "cert_path": "/etc/letsencrypt/live/bristol3.pki.enigmabridge.com/cert.pem", "key_path": "/etc/letsencrypt/live/bristol3.pki.enigmabridge.com/privkey.pem", "chain_path": "/etc/letsencrypt/live/bristol3.pki.enigmabridge.com/chain.pem", "fullchain_path": "/etc/letsencrypt/live/bristol3.pki.enigmabridge.com/fullchain.pem", "timestamp": 1477582237, "cert_timestamp": 1477582245.9930167}
    {"cmd": "save", "title": null, "temporary": false}
    {"cmd": "deploy_cert", "domain": "bs3.pki.enigmabridge.com", "cert_path": "/etc/letsencrypt/live/bristol3.pki.enigmabridge.com/cert.pem", "key_path": "/etc/letsencrypt/live/bristol3.pki.enigmabridge.com/privkey.pem", "chain_path": "/etc/letsencrypt/live/bristol3.pki.enigmabridge.com/chain.pem", "fullchain_path": "/etc/letsencrypt/live/bristol3.pki.enigmabridge.com/fullchain.pem", "timestamp": 1477582237, "cert_timestamp": 1477582245.9930167}
    {"cmd": "save", "title": null, "temporary": false}
    {"cmd": "save", "title": "Deployed ACME Certificate", "temporary": false}
    {"cmd": "restart"}
    {"cmd": "report", "messages": [{"priority": 1, "on_crash": true, "lines": ["Congratulations! Your certificate and chain have been saved at /etc/letsencrypt/live/bristol3.pki.enigmabridge.com/fullchain.pem. Your cert will expire on 2017-01-25. To obtain a new or tweaked version of this certificate in the future, simply run certbot again with the \"certonly\" option. To non-interactively renew *all* of your certificates, run \"certbot renew\""]}]}

### HTTP

Run the certbot with the following command (just
``preferred-challenges`` changed):

    certbot --staging \
            --text --agree-tos --email you@example.com \
            --expand --renew-by-default \
            --configurator certbot-external-auth:out \
            --certbot-external-auth:out-public-ip-logging-ok \
            -d "bristol3.pki.enigmabridge.com" \
            -d "bs3.pki.enigmabridge.com" \
            --preferred-challenges http \
            certonly 2>/dev/null

Stdout:

    {"cmd": "perform_challenge", "type": "http-01", "domain": "bristol3.pki.enigmabridge.com", "token": "oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY", "validation": "oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "uri": "http://bristol3.pki.enigmabridge.com/.well-known/acme-challenge/oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY", "command": "mkdir -p /tmp/certbot/public_html/.well-known/acme-challenge\ncd /tmp/certbot/public_html\nprintf \"%s\" oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0 > .well-known/acme-challenge/oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY\n# run only once per server:\n$(command -v python2 || command -v python2.7 || command -v python2.6) -c \\\n\"import BaseHTTPServer, SimpleHTTPServer; \\\ns = BaseHTTPServer.HTTPServer(('', 80), SimpleHTTPServer.SimpleHTTPRequestHandler); \\\ns.serve_forever()\" ", "key_auth": "oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0"}

    {"cmd": "perform_challenge", "type": "http-01", "domain": "bs3.pki.enigmabridge.com", "token": "L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0", "validation": "L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "uri": "http://bs3.pki.enigmabridge.com/.well-known/acme-challenge/L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0", "command": "mkdir -p /tmp/certbot/public_html/.well-known/acme-challenge\ncd /tmp/certbot/public_html\nprintf \"%s\" L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0 > .well-known/acme-challenge/L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0\n# run only once per server:\n$(command -v python2 || command -v python2.7 || command -v python2.6) -c \\\n\"import BaseHTTPServer, SimpleHTTPServer; \\\ns = BaseHTTPServer.HTTPServer(('', 80), SimpleHTTPServer.SimpleHTTPRequestHandler); \\\ns.serve_forever()\" ", "key_auth": "L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0"}

    {"cmd": "cleanup", "type": "http-01", "status": "pending", "domain": "bristol3.pki.enigmabridge.com", "token": "oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY", "validation": "oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "key_auth": "oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "validated": null, "error": null}
    {"cmd": "cleanup", "type": "http-01", "status": "pending", "domain": "bs3.pki.enigmabridge.com", "token": "L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0", "validation": "L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "key_auth": "L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "validated": null, "error": null}
    {"cmd": "report", "messages": [{"priority": 1, "on_crash": true, "lines": ["Congratulations! Your certificate and chain have been saved at /etc/letsencrypt/live/bristol3.pki.enigmabridge.com/fullchain.pem. Your cert will expire on 2017-01-25. To obtain a new or tweaked version of this certificate in the future, simply run certbot again. To non-interactively renew *all* of your certificates, run \"certbot renew\""]}]}

## Example - Dehydrated

The following section demonstrates usage of the plugin with
[Dehydrated](https://github.com/lukas2511/dehydrated) DNS hooks.

Note the certbot is run with action ``run`` so deployment callbacks are
called too.

In this repository there is
[dehydrated-example.sh](https://github.com/EnigmaBridge/certbot-external-auth/blob/master/dehydrated-example.sh)
which is a hook stub used in this example. When using your own handler
please make sure the file is executable (has ``x`` flag,
``chmod +x handler-file``).

    certbot --staging \
            --text --agree-tos --email you@example.com \
            --expand --renew-by-default \
            --configurator certbot-external-auth:out \
            --certbot-external-auth:out-public-ip-logging-ok \
            -d "bristol3.pki.enigmabridge.com" \
            -d "bs3.pki.enigmabridge.com" \
            --preferred-challenges dns \
            --certbot-external-auth:out-handler ./dehydrated-example.sh \
            --certbot-external-auth:out-dehydrated-dns \
            run 2>/dev/null

Stdout:

    {"cmd": "perform_challenge", "type": "dns-01", "domain": "bristol3.pki.enigmabridge.com", "token": "_QLSFTRw6qbQaN7gTglBYZuU1L7KAP-bXB_41CAnAvU", "validation": "667drNmQL3vX6bu8YZlgy0wKNBlCny8yrjF1lSaUndc", "txt_domain": "_acme-challenge.bristol3.pki.enigmabridge.com", "key_auth": "_QLSFTRw6qbQaN7gTglBYZuU1L7KAP-bXB_41CAnAvU.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0"}
    {"cmd": "perform_challenge", "type": "dns-01", "domain": "bs3.pki.enigmabridge.com", "token": "3gJ87yANDpmuuKVL2ktfQ0_qURQ3mN0IfqgbTU_AGS4", "validation": "ejEDZXYEeYHUxqBAiX4csh8GKkeVX7utK6BBOBshZ1Y", "txt_domain": "_acme-challenge.bs3.pki.enigmabridge.com", "key_auth": "3gJ87yANDpmuuKVL2ktfQ0_qURQ3mN0IfqgbTU_AGS4.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0"}
    {"cmd": "cleanup", "type": "dns-01", "status": "pending", "domain": "bristol3.pki.enigmabridge.com", "token": "_QLSFTRw6qbQaN7gTglBYZuU1L7KAP-bXB_41CAnAvU", "validation": "667drNmQL3vX6bu8YZlgy0wKNBlCny8yrjF1lSaUndc", "key_auth": "_QLSFTRw6qbQaN7gTglBYZuU1L7KAP-bXB_41CAnAvU.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "validated": null, "error": null}
    {"cmd": "cleanup", "type": "dns-01", "status": "pending", "domain": "bs3.pki.enigmabridge.com", "token": "3gJ87yANDpmuuKVL2ktfQ0_qURQ3mN0IfqgbTU_AGS4", "validation": "ejEDZXYEeYHUxqBAiX4csh8GKkeVX7utK6BBOBshZ1Y", "key_auth": "3gJ87yANDpmuuKVL2ktfQ0_qURQ3mN0IfqgbTU_AGS4.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "validated": null, "error": null}
    {"cmd": "deploy_cert", "domain": "bristol3.pki.enigmabridge.com", "cert_path": "/etc/letsencrypt/live/bristol3.pki.enigmabridge.com/cert.pem", "key_path": "/etc/letsencrypt/live/bristol3.pki.enigmabridge.com/privkey.pem", "chain_path": "/etc/letsencrypt/live/bristol3.pki.enigmabridge.com/chain.pem", "fullchain_path": "/etc/letsencrypt/live/bristol3.pki.enigmabridge.com/fullchain.pem", "timestamp": 1477582423, "cert_timestamp": 1477582428.9469378}
    {"cmd": "save", "title": null, "temporary": false}
    {"cmd": "deploy_cert", "domain": "bs3.pki.enigmabridge.com", "cert_path": "/etc/letsencrypt/live/bristol3.pki.enigmabridge.com/cert.pem", "key_path": "/etc/letsencrypt/live/bristol3.pki.enigmabridge.com/privkey.pem", "chain_path": "/etc/letsencrypt/live/bristol3.pki.enigmabridge.com/chain.pem", "fullchain_path": "/etc/letsencrypt/live/bristol3.pki.enigmabridge.com/fullchain.pem", "timestamp": 1477582423, "cert_timestamp": 1477582428.9469378}
    {"cmd": "save", "title": null, "temporary": false}
    {"cmd": "save", "title": "Deployed ACME Certificate", "temporary": false}
    {"cmd": "restart"}
    {"cmd": "report", "messages": [{"priority": 1, "on_crash": true, "lines": ["Congratulations! Your certificate and chain have been saved at /etc/letsencrypt/live/bristol3.pki.enigmabridge.com/fullchain.pem. Your cert will expire on 2017-01-25. To obtain a new or tweaked version of this certificate in the future, simply run certbot again with the \"certonly\" option. To non-interactively renew *all* of your certificates, run \"certbot renew\""]}]}

Stderr:

    Saving debug log to /var/log/letsencrypt/letsencrypt.log
    Starting new HTTPS connection (1): acme-staging.api.letsencrypt.org
    Renewing an existing certificate
    Performing the following challenges:
    dns-01 challenge for bristol3.pki.enigmabridge.com
    dns-01 challenge for bs3.pki.enigmabridge.com
    Handler output (deploy_challenge):

    -----BEGIN DEPLOY_CHALLENGE-----
    add _acme-challenge.bristol3.pki.enigmabridge.com. 300 in TXT "667drNmQL3vX6bu8YZlgy0wKNBlCny8yrjF1lSaUndc"\n\n
    -----BEGIN DEPLOY_CHALLENGE-----

    Self-verify of challenge failed.
    Handler output (deploy_challenge):

    -----BEGIN DEPLOY_CHALLENGE-----
    add _acme-challenge.bs3.pki.enigmabridge.com. 300 in TXT "ejEDZXYEeYHUxqBAiX4csh8GKkeVX7utK6BBOBshZ1Y"\n\n
    -----BEGIN DEPLOY_CHALLENGE-----

    Self-verify of challenge failed.
    Waiting for verification...
    Cleaning up challenges
    Handler output (clean_challenge):

    -----BEGIN CLEAN_CHALLENGE-----
    delete _acme-challenge.. 300 in TXT "667drNmQL3vX6bu8YZlgy0wKNBlCny8yrjF1lSaUndc"

    -----END CLEAN_CHALLENGE-----

    Handler output (clean_challenge):

    -----BEGIN CLEAN_CHALLENGE-----
    delete _acme-challenge.. 300 in TXT "ejEDZXYEeYHUxqBAiX4csh8GKkeVX7utK6BBOBshZ1Y"

    -----END CLEAN_CHALLENGE-----

    Generating key (2048 bits): /etc/letsencrypt/keys/0246_key-certbot.pem
    Creating CSR: /etc/letsencrypt/csr/0246_csr-certbot.pem
    Handler output (deploy_cert):

    -----BEGIN DEPLOY_CERT-----
    domain: bristol3.pki.enigmabridge.com
    key_file: /etc/letsencrypt/live/bristol3.pki.enigmabridge.com/privkey.pem
    cert_file: /etc/letsencrypt/live/bristol3.pki.enigmabridge.com/cert.pem
    fullchain_file: /etc/letsencrypt/live/bristol3.pki.enigmabridge.com/fullchain.pem
    chain_file: /etc/letsencrypt/live/bristol3.pki.enigmabridge.com/chain.pem
    timestamp: 1477582423
    -----END DEPLOY_CERT-----

    Handler output (deploy_cert):

    -----BEGIN DEPLOY_CERT-----
    domain: bs3.pki.enigmabridge.com
    key_file: /etc/letsencrypt/live/bristol3.pki.enigmabridge.com/privkey.pem
    cert_file: /etc/letsencrypt/live/bristol3.pki.enigmabridge.com/cert.pem
    fullchain_file: /etc/letsencrypt/live/bristol3.pki.enigmabridge.com/fullchain.pem
    chain_file: /etc/letsencrypt/live/bristol3.pki.enigmabridge.com/chain.pem
    timestamp: 1477582423
    -----END DEPLOY_CERT-----


    -------------------------------------------------------------------------------
    Your existing certificate has been successfully renewed, and the new certificate
    has been installed.

    The new certificate covers the following domains:
    https://bristol3.pki.enigmabridge.com and https://bs3.pki.enigmabridge.com

    You should test your configuration at:
    https://www.ssllabs.com/ssltest/analyze.html?d=bristol3.pki.enigmabridge.com
    https://www.ssllabs.com/ssltest/analyze.html?d=bs3.pki.enigmabridge.com
    -------------------------------------------------------------------------------

## Example - Handler

### DNS

In this repository there is a default
[handler-example.sh](https://github.com/EnigmaBridge/certbot-external-auth/blob/master/handler-example.sh)
which can be used as a handler. When using your own handler please make
sure the file is executable (has ``x`` flag, ``chmod +x handler-file``).

    certbot --staging \
            --text --agree-tos --email you@example.com \
            --expand --renew-by-default \
            --configurator certbot-external-auth:out \
            --certbot-external-auth:out-public-ip-logging-ok \
            -d "bristol3.pki.enigmabridge.com" \
            -d "bs3.pki.enigmabridge.com" \
            --preferred-challenges dns \
            --certbot-external-auth:out-handler ./handler-example.sh \
            certonly 2>/dev/null

Stdout:

    {"cmd": "perform_challenge", "type": "dns-01", "domain": "bristol3.pki.enigmabridge.com", "token": "_QLSFTRw6qbQaN7gTglBYZuU1L7KAP-bXB_41CAnAvU", "validation": "667drNmQL3vX6bu8YZlgy0wKNBlCny8yrjF1lSaUndc", "txt_domain": "_acme-challenge.bristol3.pki.enigmabridge.com", "key_auth": "_QLSFTRw6qbQaN7gTglBYZuU1L7KAP-bXB_41CAnAvU.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0"}
    {"cmd": "perform_challenge", "type": "dns-01", "domain": "bs3.pki.enigmabridge.com", "token": "3gJ87yANDpmuuKVL2ktfQ0_qURQ3mN0IfqgbTU_AGS4", "validation": "ejEDZXYEeYHUxqBAiX4csh8GKkeVX7utK6BBOBshZ1Y", "txt_domain": "_acme-challenge.bs3.pki.enigmabridge.com", "key_auth": "3gJ87yANDpmuuKVL2ktfQ0_qURQ3mN0IfqgbTU_AGS4.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0"}
    {"cmd": "cleanup", "type": "dns-01", "status": "pending", "domain": "bristol3.pki.enigmabridge.com", "token": "_QLSFTRw6qbQaN7gTglBYZuU1L7KAP-bXB_41CAnAvU", "validation": "667drNmQL3vX6bu8YZlgy0wKNBlCny8yrjF1lSaUndc", "key_auth": "_QLSFTRw6qbQaN7gTglBYZuU1L7KAP-bXB_41CAnAvU.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "validated": null, "error": null}
    {"cmd": "cleanup", "type": "dns-01", "status": "pending", "domain": "bs3.pki.enigmabridge.com", "token": "3gJ87yANDpmuuKVL2ktfQ0_qURQ3mN0IfqgbTU_AGS4", "validation": "ejEDZXYEeYHUxqBAiX4csh8GKkeVX7utK6BBOBshZ1Y", "key_auth": "3gJ87yANDpmuuKVL2ktfQ0_qURQ3mN0IfqgbTU_AGS4.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "validated": null, "error": null}
    {"cmd": "report", "messages": [{"priority": 1, "on_crash": true, "lines": ["Congratulations! Your certificate and chain have been saved at /etc/letsencrypt/live/bristol3.pki.enigmabridge.com/fullchain.pem. Your cert will expire on 2017-01-25. To obtain a new or tweaked version of this certificate in the future, simply run certbot again. To non-interactively renew *all* of your certificates, run \"certbot renew\""]}]}

Stderr:

    Saving debug log to /var/log/letsencrypt/letsencrypt.log
    Starting new HTTPS connection (1): acme-staging.api.letsencrypt.org
    Renewing an existing certificate
    Performing the following challenges:
    dns-01 challenge for bristol3.pki.enigmabridge.com
    dns-01 challenge for bs3.pki.enigmabridge.com
    Handler output (pre-perform):

    -----BEGIN PRE-PERFORM-----
    -----END PRE-PERFORM-----

    Handler output (perform):

    -----BEGIN PERFORM-----
    cmd: perform
    type: dns-01
    domain: bristol3.pki.enigmabridge.com
    uri: 
    validation: 667drNmQL3vX6bu8YZlgy0wKNBlCny8yrjF1lSaUndc
    key-auth: _QLSFTRw6qbQaN7gTglBYZuU1L7KAP-bXB_41CAnAvU.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0
    z_domain: 
    cert_path: 
    key_path: 
    port: 
    json: {"cmd": "perform_challenge", "type": "dns-01", "domain": "bristol3.pki.enigmabridge.com", "token": "_QLSFTRw6qbQaN7gTglBYZuU1L7KAP-bXB_41CAnAvU", "validation": "667drNmQL3vX6bu8YZlgy0wKNBlCny8yrjF1lSaUndc", "txt_domain": "_acme-challenge.bristol3.pki.enigmabridge.com", "key_auth": "_QLSFTRw6qbQaN7gTglBYZuU1L7KAP-bXB_41CAnAvU.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0"}
    -----END PERFORM-----

    Self-verify of challenge failed.
    Handler output (perform):

    -----BEGIN PERFORM-----
    cmd: perform
    type: dns-01
    domain: bs3.pki.enigmabridge.com
    uri: 
    validation: ejEDZXYEeYHUxqBAiX4csh8GKkeVX7utK6BBOBshZ1Y
    key-auth: 3gJ87yANDpmuuKVL2ktfQ0_qURQ3mN0IfqgbTU_AGS4.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0
    z_domain: 
    cert_path: 
    key_path: 
    port: 
    json: {"cmd": "perform_challenge", "type": "dns-01", "domain": "bs3.pki.enigmabridge.com", "token": "3gJ87yANDpmuuKVL2ktfQ0_qURQ3mN0IfqgbTU_AGS4", "validation": "ejEDZXYEeYHUxqBAiX4csh8GKkeVX7utK6BBOBshZ1Y", "txt_domain": "_acme-challenge.bs3.pki.enigmabridge.com", "key_auth": "3gJ87yANDpmuuKVL2ktfQ0_qURQ3mN0IfqgbTU_AGS4.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0"}
    -----END PERFORM-----

    Self-verify of challenge failed.
    Handler output (post-perform):

    -----BEGIN POST-PERFORM-----
    -----END POST-PERFORM-----

    Waiting for verification...
    Cleaning up challenges
    Handler output (pre-cleanup):

    -----BEGIN PRE-CLEANUP-----
    -----END PRE-CLEANUP-----

    Handler output (cleanup):

    -----BEGIN CLEANUP-----
    cmd: cleanup
    type: dns-01
    domain: bristol3.pki.enigmabridge.com
    status: pending
    token: _QLSFTRw6qbQaN7gTglBYZuU1L7KAP-bXB_41CAnAvU
    error: None
    json: {"cmd": "cleanup", "type": "dns-01", "status": "pending", "domain": "bristol3.pki.enigmabridge.com", "token": "_QLSFTRw6qbQaN7gTglBYZuU1L7KAP-bXB_41CAnAvU", "validation": "667drNmQL3vX6bu8YZlgy0wKNBlCny8yrjF1lSaUndc", "key_auth": "_QLSFTRw6qbQaN7gTglBYZuU1L7KAP-bXB_41CAnAvU.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "validated": null, "error": null}
    -----END CLEANUP-----

    Handler output (cleanup):

    -----BEGIN CLEANUP-----
    cmd: cleanup
    type: dns-01
    domain: bs3.pki.enigmabridge.com
    status: pending
    token: 3gJ87yANDpmuuKVL2ktfQ0_qURQ3mN0IfqgbTU_AGS4
    error: None
    json: {"cmd": "cleanup", "type": "dns-01", "status": "pending", "domain": "bs3.pki.enigmabridge.com", "token": "3gJ87yANDpmuuKVL2ktfQ0_qURQ3mN0IfqgbTU_AGS4", "validation": "ejEDZXYEeYHUxqBAiX4csh8GKkeVX7utK6BBOBshZ1Y", "key_auth": "3gJ87yANDpmuuKVL2ktfQ0_qURQ3mN0IfqgbTU_AGS4.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "validated": null, "error": null}
    -----END CLEANUP-----

    Handler output (post-cleanup):

    -----BEGIN POST-CLEANUP-----
    -----END POST-CLEANUP-----

    Generating key (2048 bits): /etc/letsencrypt/keys/0240_key-certbot.pem
    Creating CSR: /etc/letsencrypt/csr/0240_csr-certbot.pem

### HTTP

Run the certbot with the following command (just
``preferred-challenges`` changed):

    certbot --staging \
            --text --agree-tos --email you@example.com \
            --expand --renew-by-default \
            --configurator certbot-external-auth:out \
            --certbot-external-auth:out-public-ip-logging-ok \
            -d "bristol3.pki.enigmabridge.com" \
            -d "bs3.pki.enigmabridge.com" \
            --preferred-challenges http \
            --certbot-external-auth:out-handler ./handler-example.sh \
            certonly 2>/dev/null

Stdout:

    {"cmd": "perform_challenge", "type": "http-01", "domain": "bristol3.pki.enigmabridge.com", "token": "oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY", "validation": "oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "uri": "http://bristol3.pki.enigmabridge.com/.well-known/acme-challenge/oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY", "command": "mkdir -p /tmp/certbot/public_html/.well-known/acme-challenge\ncd /tmp/certbot/public_html\nprintf \"%s\" oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0 > .well-known/acme-challenge/oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY\n# run only once per server:\n$(command -v python2 || command -v python2.7 || command -v python2.6) -c \\\n\"import BaseHTTPServer, SimpleHTTPServer; \\\ns = BaseHTTPServer.HTTPServer(('', 80), SimpleHTTPServer.SimpleHTTPRequestHandler); \\\ns.serve_forever()\" ", "key_auth": "oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0"}
    {"cmd": "perform_challenge", "type": "http-01", "domain": "bs3.pki.enigmabridge.com", "token": "L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0", "validation": "L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "uri": "http://bs3.pki.enigmabridge.com/.well-known/acme-challenge/L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0", "command": "mkdir -p /tmp/certbot/public_html/.well-known/acme-challenge\ncd /tmp/certbot/public_html\nprintf \"%s\" L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0 > .well-known/acme-challenge/L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0\n# run only once per server:\n$(command -v python2 || command -v python2.7 || command -v python2.6) -c \\\n\"import BaseHTTPServer, SimpleHTTPServer; \\\ns = BaseHTTPServer.HTTPServer(('', 80), SimpleHTTPServer.SimpleHTTPRequestHandler); \\\ns.serve_forever()\" ", "key_auth": "L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0"}
    {"cmd": "cleanup", "type": "http-01", "status": "pending", "domain": "bristol3.pki.enigmabridge.com", "token": "oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY", "validation": "oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "key_auth": "oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "validated": null, "error": null}
    {"cmd": "cleanup", "type": "http-01", "status": "pending", "domain": "bs3.pki.enigmabridge.com", "token": "L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0", "validation": "L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "key_auth": "L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "validated": null, "error": null}
    {"cmd": "report", "messages": [{"priority": 1, "on_crash": true, "lines": ["Congratulations! Your certificate and chain have been saved at /etc/letsencrypt/live/bristol3.pki.enigmabridge.com/fullchain.pem. Your cert will expire on 2017-01-25. To obtain a new or tweaked version of this certificate in the future, simply run certbot again. To non-interactively renew *all* of your certificates, run \"certbot renew\""]}]}

Stderr:

    Saving debug log to /var/log/letsencrypt/letsencrypt.log
    Starting new HTTPS connection (1): acme-staging.api.letsencrypt.org
    Renewing an existing certificate
    Performing the following challenges:
    http-01 challenge for bristol3.pki.enigmabridge.com
    http-01 challenge for bs3.pki.enigmabridge.com
    Handler output (pre-perform):

    -----BEGIN PRE-PERFORM-----
    -----END PRE-PERFORM-----

    Handler output (perform):

    -----BEGIN PERFORM-----
    cmd: perform
    type: http-01
    domain: bristol3.pki.enigmabridge.com
    uri: http://bristol3.pki.enigmabridge.com/.well-known/acme-challenge/oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY
    validation: oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0
    key-auth: oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0
    z_domain: 
    cert_path: 
    key_path: 
    port: 
    json: {"cmd": "perform_challenge", "type": "http-01", "domain": "bristol3.pki.enigmabridge.com", "token": "oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY", "validation": "oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "uri": "http://bristol3.pki.enigmabridge.com/.well-known/acme-challenge/oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY", "command": "mkdir -p /tmp/certbot/public_html/.well-known/acme-challenge\ncd /tmp/certbot/public_html\nprintf \"%s\" oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0 > .well-known/acme-challenge/oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY\n# run only once per server:\n$(command -v python2 || command -v python2.7 || command -v python2.6) -c \\\n\"import BaseHTTPServer, SimpleHTTPServer; \\\ns = BaseHTTPServer.HTTPServer(('', 80), SimpleHTTPServer.SimpleHTTPRequestHandler); \\\ns.serve_forever()\" ", "key_auth": "oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0"}
    -----END PERFORM-----

    Starting new HTTP connection (1): bristol3.pki.enigmabridge.com
    Unable to reach http://bristol3.pki.enigmabridge.com/.well-known/acme-challenge/oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY: HTTPConnectionPool(host='bristol3.pki.enigmabridge.com', port=80): Max retries exceeded with url: /.well-known/acme-challenge/oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY (Caused by NewConnectionError('<requests.packages.urllib3.connection.HTTPConnection object at 0x7ff5bc837d90>: Failed to establish a new connection: [Errno 111] Connection refused',))
    Self-verify of challenge failed.
    Handler output (perform):

    -----BEGIN PERFORM-----
    cmd: perform
    type: http-01
    domain: bs3.pki.enigmabridge.com
    uri: http://bs3.pki.enigmabridge.com/.well-known/acme-challenge/L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0
    validation: L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0
    key-auth: L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0
    z_domain: 
    cert_path: 
    key_path: 
    port: 
    json: {"cmd": "perform_challenge", "type": "http-01", "domain": "bs3.pki.enigmabridge.com", "token": "L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0", "validation": "L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "uri": "http://bs3.pki.enigmabridge.com/.well-known/acme-challenge/L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0", "command": "mkdir -p /tmp/certbot/public_html/.well-known/acme-challenge\ncd /tmp/certbot/public_html\nprintf \"%s\" L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0 > .well-known/acme-challenge/L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0\n# run only once per server:\n$(command -v python2 || command -v python2.7 || command -v python2.6) -c \\\n\"import BaseHTTPServer, SimpleHTTPServer; \\\ns = BaseHTTPServer.HTTPServer(('', 80), SimpleHTTPServer.SimpleHTTPRequestHandler); \\\ns.serve_forever()\" ", "key_auth": "L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0"}
    -----END PERFORM-----

    Starting new HTTP connection (1): bs3.pki.enigmabridge.com
    Unable to reach http://bs3.pki.enigmabridge.com/.well-known/acme-challenge/L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0: HTTPConnectionPool(host='bs3.pki.enigmabridge.com', port=80): Max retries exceeded with url: /.well-known/acme-challenge/L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0 (Caused by NewConnectionError('<requests.packages.urllib3.connection.HTTPConnection object at 0x7ff5bc837f10>: Failed to establish a new connection: [Errno 111] Connection refused',))
    Self-verify of challenge failed.
    Handler output (post-perform):

    -----BEGIN POST-PERFORM-----
    -----END POST-PERFORM-----

    Waiting for verification...
    Cleaning up challenges
    Handler output (pre-cleanup):

    -----BEGIN PRE-CLEANUP-----
    -----END PRE-CLEANUP-----

    Handler output (cleanup):

    -----BEGIN CLEANUP-----
    cmd: cleanup
    type: http-01
    domain: bristol3.pki.enigmabridge.com
    status: pending
    token: oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY
    error: None
    json: {"cmd": "cleanup", "type": "http-01", "status": "pending", "domain": "bristol3.pki.enigmabridge.com", "token": "oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY", "validation": "oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "key_auth": "oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "validated": null, "error": null}
    -----END CLEANUP-----

    Handler output (cleanup):

    -----BEGIN CLEANUP-----
    cmd: cleanup
    type: http-01
    domain: bs3.pki.enigmabridge.com
    status: pending
    token: L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0
    error: None
    json: {"cmd": "cleanup", "type": "http-01", "status": "pending", "domain": "bs3.pki.enigmabridge.com", "token": "L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0", "validation": "L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "key_auth": "L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "validated": null, "error": null}
    -----END CLEANUP-----

    Handler output (post-cleanup):

    -----BEGIN POST-CLEANUP-----
    -----END POST-CLEANUP-----

    Generating key (2048 bits): /etc/letsencrypt/keys/0242_key-certbot.pem
    Creating CSR: /etc/letsencrypt/csr/0242_csr-certbot.pem

## Future work

-  Add compatibility with
   [Dehydrated](https://github.com/lukas2511/dehydrated) DNS hooks
-  Communicate challenges via named pipes
-  Communicate challenges via sockets

## Manual Installation

To install, first install certbot (either on the root or in a
virtualenv), then:

    python setup.py install

## Credits

The plugin is based on the

-  Let's Encrypt nginx plugin
-  [certbot-external](https://github.com/marcan/certbot-external)
-  ``manual.py`` certbot plugin.

Once ticket [2782](https://github.com/certbot/certbot/issues/2782) is
resolved this won't be needed.
