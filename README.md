## External authenticator for Certbot

This plugin helps with domain validation process either by calling an external 
program or by printing JSON challenge to stdout for invoker to solve. 
Handler is compatible with [Dehydrated] DNS hooks.

Supported challenges: _DNS-01_, _HTTP-01_, _TLS-SNI-01_

This plugin supports manual authentication and installation.

## Installation - pip

```bash
pip install certbot
pip install certbot-external-auth
```

## Usage

To use, try something like this:

```bash
certbot --text --agree-tos --email you@example.com \
        --expand --renew-by-default \
        --configurator certbot-external-auth:out \
        --certbot-external-auth:out-public-ip-logging-ok \
        -d example.com certonly
```

There are 3 main modes of operation:

* JSON mode (default)
* Text mode - fallback to the `manual.py` operation
* Handler mode - auth performed by an external program. Supports [Dehydrated] and augmented mode.

If you want it to use as Authenticator and Installer, use
`--configurator certbot-external-auth:out` certbot flag, for Authenticator only
use `-a certbot-external-auth:out`

In authenticator mode one can use certbot actions `certonly` or `renew`. 
If installer mode is enabled too use `run` action - typical for [Dehydrated] hooks.

### JSON Mode

JSON mode produces one-line JSON objects (`\n` separated) with a challenge to process by the invoker 
on the STDOUT. 

After the challenge is processed, the invoker is supposed
to send a new line `\n` character to the STDIN to continue with the process.

Note JSON mode produces also another JSON objects besides challenges, 
e.g., cleanup and reports. The `\n` is expected only for challenges (perform/validate step).

If plugin is installed also as an Installer (or Configurator), it provides also 
commands related to the certificate installation.

Reporter was substituted to produce JSON logs so STDOUT is JSON only.

## Arguments

```
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
```

## Examples
In the examples below I did not solve the challenges so the reporter prints 
out an error. The error is indicated also by returning non-zero return code.

The particular examples for verification methods and handler follows.

### DNS

Run the certbot with the following command:

```bash
certbot --staging \
        --text --agree-tos --email you@example.com \
        --expand --renew-by-default \
        --configurator certbot-external-auth:out \
        --certbot-external-auth:out-public-ip-logging-ok \
        -d "bristol3.pki.enigmabridge.com" \
        -d "bs3.pki.enigmabridge.com" \
        --preferred-challenges dns \
        certonly 2>/dev/null
```

Stderr contains string log / report, not in JSON format.

Stdout:

```json
{"cmd": "perform_challenge", "type": "dns-01", "domain": "bristol3.pki.enigmabridge.com", "token": "_QLSFTRw6qbQaN7gTglBYZuU1L7KAP-bXB_41CAnAvU", "validation": "667drNmQL3vX6bu8YZlgy0wKNBlCny8yrjF1lSaUndc", "txt_domain": "_acme-challenge.bristol3.pki.enigmabridge.com", "key_auth": "_QLSFTRw6qbQaN7gTglBYZuU1L7KAP-bXB_41CAnAvU.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0"}

{"cmd": "perform_challenge", "type": "dns-01", "domain": "bs3.pki.enigmabridge.com", "token": "3gJ87yANDpmuuKVL2ktfQ0_qURQ3mN0IfqgbTU_AGS4", "validation": "ejEDZXYEeYHUxqBAiX4csh8GKkeVX7utK6BBOBshZ1Y", "txt_domain": "_acme-challenge.bs3.pki.enigmabridge.com", "key_auth": "3gJ87yANDpmuuKVL2ktfQ0_qURQ3mN0IfqgbTU_AGS4.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0"}

{"cmd": "cleanup", "type": "dns-01", "status": "pending", "domain": "bristol3.pki.enigmabridge.com", "token": "_QLSFTRw6qbQaN7gTglBYZuU1L7KAP-bXB_41CAnAvU", "validation": "667drNmQL3vX6bu8YZlgy0wKNBlCny8yrjF1lSaUndc", "key_auth": "_QLSFTRw6qbQaN7gTglBYZuU1L7KAP-bXB_41CAnAvU.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "validated": null, "error": null}
{"cmd": "cleanup", "type": "dns-01", "status": "pending", "domain": "bs3.pki.enigmabridge.com", "token": "3gJ87yANDpmuuKVL2ktfQ0_qURQ3mN0IfqgbTU_AGS4", "validation": "ejEDZXYEeYHUxqBAiX4csh8GKkeVX7utK6BBOBshZ1Y", "key_auth": "3gJ87yANDpmuuKVL2ktfQ0_qURQ3mN0IfqgbTU_AGS4.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "validated": null, "error": null}
{"cmd": "report", "messages": [{"priority": 1, "on_crash": true, "lines": ["Congratulations! Your certificate and chain have been saved at /etc/letsencrypt/live/bristol3.pki.enigmabridge.com/fullchain.pem. Your cert will expire on 2017-01-25. To obtain a new or tweaked version of this certificate in the future, simply run certbot again. To non-interactively renew *all* of your certificates, run \"certbot renew\""]}]}
```

After `{"cmd": "validate"}` message the client waits on `\n` on the standard input to continue with the validation.

### DNS installer

Certbot is running with action `run` which causes also Installer plugin part to work.
The installer is the same for all validation modes so it is demonstrated only once.

```bash
certbot --staging \
        --text --agree-tos --email you@example.com \
        --expand --renew-by-default \
        --configurator certbot-external-auth:out \
        --certbot-external-auth:out-public-ip-logging-ok \
        -d "bristol3.pki.enigmabridge.com" \
        -d "bs3.pki.enigmabridge.com" \
        --preferred-challenges dns \
        run 2>/dev/null
```

Stdout:

```json
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
```


### HTTP

Run the certbot with the following command (just `preferred-challenges` changed):

```bash
certbot --staging \
        --text --agree-tos --email you@example.com \
        --expand --renew-by-default \
        --configurator certbot-external-auth:out \
        --certbot-external-auth:out-public-ip-logging-ok \
        -d "bristol3.pki.enigmabridge.com" \
        -d "bs3.pki.enigmabridge.com" \
        --preferred-challenges http \
        certonly 2>/dev/null
```

Stdout:

```json
{"cmd": "perform_challenge", "type": "http-01", "domain": "bristol3.pki.enigmabridge.com", "token": "oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY", "validation": "oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "uri": "http://bristol3.pki.enigmabridge.com/.well-known/acme-challenge/oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY", "command": "mkdir -p /tmp/certbot/public_html/.well-known/acme-challenge\ncd /tmp/certbot/public_html\nprintf \"%s\" oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0 > .well-known/acme-challenge/oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY\n# run only once per server:\n$(command -v python2 || command -v python2.7 || command -v python2.6) -c \\\n\"import BaseHTTPServer, SimpleHTTPServer; \\\ns = BaseHTTPServer.HTTPServer(('', 80), SimpleHTTPServer.SimpleHTTPRequestHandler); \\\ns.serve_forever()\" ", "key_auth": "oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0"}

{"cmd": "perform_challenge", "type": "http-01", "domain": "bs3.pki.enigmabridge.com", "token": "L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0", "validation": "L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "uri": "http://bs3.pki.enigmabridge.com/.well-known/acme-challenge/L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0", "command": "mkdir -p /tmp/certbot/public_html/.well-known/acme-challenge\ncd /tmp/certbot/public_html\nprintf \"%s\" L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0 > .well-known/acme-challenge/L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0\n# run only once per server:\n$(command -v python2 || command -v python2.7 || command -v python2.6) -c \\\n\"import BaseHTTPServer, SimpleHTTPServer; \\\ns = BaseHTTPServer.HTTPServer(('', 80), SimpleHTTPServer.SimpleHTTPRequestHandler); \\\ns.serve_forever()\" ", "key_auth": "L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0"}

{"cmd": "cleanup", "type": "http-01", "status": "pending", "domain": "bristol3.pki.enigmabridge.com", "token": "oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY", "validation": "oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "key_auth": "oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "validated": null, "error": null}
{"cmd": "cleanup", "type": "http-01", "status": "pending", "domain": "bs3.pki.enigmabridge.com", "token": "L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0", "validation": "L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "key_auth": "L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "validated": null, "error": null}
{"cmd": "report", "messages": [{"priority": 1, "on_crash": true, "lines": ["Congratulations! Your certificate and chain have been saved at /etc/letsencrypt/live/bristol3.pki.enigmabridge.com/fullchain.pem. Your cert will expire on 2017-01-25. To obtain a new or tweaked version of this certificate in the future, simply run certbot again. To non-interactively renew *all* of your certificates, run \"certbot renew\""]}]}
```

### TLS-SNI

Run the certbot with the following command (just `preferred-challenges` changed):

```bash
certbot --staging \
        --text --agree-tos --email you@example.com \
        --expand --renew-by-default \
        --configurator certbot-external-auth:out \
        --certbot-external-auth:out-public-ip-logging-ok \
        -d "bristol3.pki.enigmabridge.com" \
        -d "bs3.pki.enigmabridge.com" \
        --preferred-challenges tls-sni \
        certonly 2>/dev/null
```

Stdout:

```json
{"cmd": "perform_challenge", "type": "tls-sni-01", "domain": "bristol3.pki.enigmabridge.com", "token": "xgg9AwsMl8Rtdwh_ZkHozmDEr9G4Z1noCqnbRXp3zyA", "z_domain": "9e18429925564832b4acea536aeb30e8.c06f4638a973d2756ab3ff17b8ed68b8.acme.invalid", "validation": "9e18429925564832b4acea536aeb30e8.c06f4638a973d2756ab3ff17b8ed68b8.acme.invalid", "cert_path": "/var/lib/letsencrypt/xgg9AwsMl8Rtdwh_ZkHozmDEr9G4Z1noCqnbRXp3zyA.crt", "key_path": "/var/lib/letsencrypt/xgg9AwsMl8Rtdwh_ZkHozmDEr9G4Z1noCqnbRXp3zyA.pem", "port": "443", "key_auth": "xgg9AwsMl8Rtdwh_ZkHozmDEr9G4Z1noCqnbRXp3zyA.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "cert_pem": "-----BEGIN CERTIFICATE-----\nMIIDIzCCAgugAwIBAgIRAKlpRT1rCUNQ02c/1ydKaegwDQYJKoZIhvcNAQELBQAw\nEDEOMAwGA1UEAwwFZHVtbXkwHhcNMTYxMDI3MTUyMTQ1WhcNMTYxMTAzMTUyMTQ1\nWjAQMQ4wDAYDVQQDDAVkdW1teTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoC\nggEBAKlZxWiP1LHEd5CP8tL8ymeeE/Yz5S3CB0/JmFY5vx6wZuqJE7TJ4175BiZ6\n8PxmnMt+5NhRLfY6PfXvpy7ypsDbMItCSWpxRfo9BKsgxdczWsyKMVqPwnWnD+Zv\nXHeTqYrzh/I+J/iLxTtEie48GOeE4xhJLlzUATxGonXrtg5IOJevmu/pp3tQ31MC\nBSKSUcw96yzcRytO9HNLNqpjTrtjXb58ztphlBcqgjtTXWbT+pxJef1W8ReMTTXQ\nyNQz77fH0q7CMBiqyDfriPoP2u0ilKrAgLw+pYi35Cs1KwK6Z+LoYvADpe9JDG2t\nl1kdghG5PT12OeTTxUevZqSzkVUCAwEAAaN4MHYwEgYDVR0TAQH/BAgwBgEB/wIB\nADBgBgNVHREEWTBXggVkdW1teYJOOWUxODQyOTkyNTU2NDgzMmI0YWNlYTUzNmFl\nYjMwZTguYzA2ZjQ2MzhhOTczZDI3NTZhYjNmZjE3YjhlZDY4YjguYWNtZS5pbnZh\nbGlkMA0GCSqGSIb3DQEBCwUAA4IBAQCNSKUr8Yf+w2HtcgiA6VEvGTgAmUZGdFGg\niM/5tefansWvyroneK93a7XsPC/IUYwAsnGz/l36qKvFUHtSpbo0mdUk7X3xPN4q\naDPa1zhGIXKCBBuP4GbKesgjMr1RZEYgJ1sRR3LArFLsd2ZdRqlYi1tKkryUOs1+\njVDHGpiUEx0IIOPFMPsnR/83bJ9UkOChwnlBxy8C/MriETKRVczPUYVut1KJ9On0\n4Lebi/4lAt2kknPlMi+Fl1gutcg0d27MIEXKKnyj4ZZVElJ78gbAKYO7S6NK1EyB\ns9U9DJoCATaCNSjDJXaH9oqbliP1s7USrTEh7TTnY75dI0i40/OT\n-----END CERTIFICATE-----\n", "key_pem": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCpWcVoj9SxxHeQ\nj/LS/MpnnhP2M+UtwgdPyZhWOb8esGbqiRO0yeNe+QYmevD8ZpzLfuTYUS32Oj31\n76cu8qbA2zCLQklqcUX6PQSrIMXXM1rMijFaj8J1pw/mb1x3k6mK84fyPif4i8U7\nRInuPBjnhOMYSS5c1AE8RqJ167YOSDiXr5rv6ad7UN9TAgUiklHMPess3EcrTvRz\nSzaqY067Y12+fM7aYZQXKoI7U11m0/qcSXn9VvEXjE010MjUM++3x9KuwjAYqsg3\n64j6D9rtIpSqwIC8PqWIt+QrNSsCumfi6GLwA6XvSQxtrZdZHYIRuT09djnk08VH\nr2aks5FVAgMBAAECggEALQzegPRSJoAXNnO0qv/ocCwTL1may9Nj0ovUZIu0Fdvj\nZNzWSy+xtqAUTMRDu0Eo0NGO2yStT2Uq+nOoS8rtJTyp60HU+eXsMadtyIBNYPQe\nYW8ZtfesSVQJ3MkfFghH/9jM/1odk/bKnvuana+LCHvHVbySAsu7EGfR7ACqS53n\ny1OmLaj1lNx8RGdMgpHB3ItoI1Yb0Mkvd9nLtK6wR13ODEG89YjjZI5MrSot+ZjJ\nr3dt0hix3aZuLop8wWOBty5atDm0ThPMT8tl12Boi8FK0UuF4zGVQp+02SjyBmgx\nUq+JDLEV0uCwuMpuALUT83bAEoI73rVAcxLbrhw5uQKBgQDcTh/BWw6w1oH0t8Gt\norOl2hZDPJtqcfxnGoO46O5gAbOyEWUzpFqqMA2U/hNbkO9/bc+7agArbV1at7dL\nVO7cn4qz0SuQZtFk6MdieHVEl/8IykDPeMF6SdBMKxkrEXgCPqgkjf5H9c+/ffnS\nu3LmizwAV92VaCvD9V69gG4EdwKBgQDEyiSMAGnKaxlvgzSUytARyhQWQ0XWfBrl\nb27G/gHxbSb4vJJ+PFBg6OEsn4ChElIIs6SDuq8zDh41wprlQXnVHkmahnoolOuX\nHr9G6sRC7OKbBaxuh3vAqqQsPKPADCC3TQQDlcPmAdYM3PpbWDmPkI1WmsquDAsT\nUbzmVIZHkwKBgD1Z+Ff1jsrKghhvkB1V4Se/61FAMJvdMIhaBvLY04GjF7LwSzmt\nfJ5GkZG7jBKE812ObDpqE7AEXeoknYP6HCcOuybGipZFO+0ZMmWG3EmE9r4w7Qma\nPG9c3QhJPFIVJFGjt1muvXC20OsoHwmDsETp44TI82lnQEDrNT4a5QiTAoGAGglg\nwoE/ff+jkuR6LYGT+/aPp85ozBMJf/e5YWy0FxxI/rn8a+VRATFusXe9DhKddfdG\nugMWMRwaFSTVV6XNF8x1EpPeT8Y8UXdI+XoQU4aCCN68TLdyQTCSniO7yqoQHhB7\ninnjPGhbyMHoAfPvUbZfbOj4DgUb5gd3hcYDKi8CgYBCdM0XgwxoY6P0znIws6Ka\ngRXivDqHAD1dO5F84rAwpaUVIBXmUBhKZkJ0GbuEc5zV5OLs9mzm81oa8CYBEGnz\nyD0YR12341234123443645457muA6L+DC/vriFC37ueuMLoTWZEbURjIm71+TrCagdJ\nPcobS+a762mUxguRIeiNxQ==\n-----END PRIVATE KEY-----\n"}

{"cmd": "perform_challenge", "type": "tls-sni-01", "domain": "bs3.pki.enigmabridge.com", "token": "CES4DhcXqr4lxuoae0qINKSndCnRUIE6SegCP6hJBdE", "z_domain": "73453e19da495a7d5fe15d7356bc5798.6422f3f5e556a8fc92699ef9b2fe1974.acme.invalid", "validation": "73453e19da495a7d5fe15d7356bc5798.6422f3f5e556a8fc92699ef9b2fe1974.acme.invalid", "cert_path": "/var/lib/letsencrypt/CES4DhcXqr4lxuoae0qINKSndCnRUIE6SegCP6hJBdE.crt", "key_path": "/var/lib/letsencrypt/CES4DhcXqr4lxuoae0qINKSndCnRUIE6SegCP6hJBdE.pem", "port": "443", "key_auth": "CES4DhcXqr4lxuoae0qINKSndCnRUIE6SegCP6hJBdE.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "cert_pem": "-----BEGIN CERTIFICATE-----\nMIIDIjCCAgqgAwIBAgIQGEaZihGes4PR9QWjLDB8/TANBgkqhkiG9w0BAQsFADAQ\nMQ4wDAYDVQQDDAVkdW1teTAeFw0xNjEwMjcxNTIxNDZaFw0xNjExMDMxNTIxNDZa\nMBAxDjAMBgNVBAMMBWR1bW15MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKC\nAQEAsV/srITsHg97SkqyN2Fr2gb06nXLUkF5SgV8/jzNwtltmrAuJWbf+yDWteoY\nc9ZH5kgiWwDUzxiai1kKKjPGso7d36r6mSn5NwJsxPyapNUKGQy4dkwvEjueClgn\ngQDIoIL5nX0EqqAYMrDpnbdHqeg605ZVc/nzbbRN5K/28nwBncg49MIfwuq2niHf\nXR+hcc3MA2cWexdtVxhT4vuB1JORP5BmXu5CQAxXuaC5Fk6WmAo78P6mhMsgGzfb\nIAIsiZxQaf+NftagwvT2dZLvuSpF2ipIGXOX/ooB6vwn+v5wNH0DSjWv1nJUdra7\n0xIDDwRN2ceJX1I24QJKUrYkowIDAQABo3gwdjASBgNVHRMBAf8ECDAGAQH/AgEA\nMGAGA1UdEQRZMFeCBWR1bW15gk43MzQ1M2UxOWRhNDk1YTdkNWZlMTVkNzM1NmJj\nNTc5OC42NDIyZjNmNWU1NTZhOGZjOTI2OTllZjliMmZlMTk3NC5hY21lLmludmFs\naWQwDQYJKoZIhvcNAQELBQADggEBAB1dKs/TLq7b7BEtnwiSr+0SxSWOUzyaYCKM\nh+2qlg6rrxzy2Rec41kGniQCPwOxrZBJJf/qvSQV1hasUG2gvuca2L7eWEbYrIRH\nOUq4kjbzYPIbAKSkaXR/21Rpn5J8TNSfPVMvm2hvTQFylODVnTRLcA0KQJlhkMGn\nuaXCrgQY3wKWCTGYU4KE0AQCyEf/M3wGEAfWjx6KuTfuRLfpXOL+gSEnf+y6n3BK\nE7lzTGZGvqKeRypL1SN7w5Zo6r2m/YKcZ9Sv1Z2f2hG8at0zYWdys/Zj0+xFBjlb\nMFIDwdEzG21AM4ZriRUbiaqpVECtbiBg2tpqK6V1Ga9Nolu9hbs=\n-----END CERTIFICATE-----\n", "key_pem": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCxX+yshOweD3tK\nSrI3YWvaBvTqdctSQXlKBXz+PM3C2W2asC4lZt/7INa16hhz1kfmSCJbANTPGJqL\nWQoqM8ayjt3fqvqZKfk3AmzE/Jqk1QoZDLh2TC8SO54KWCeBAMiggvmdfQSqoBgy\nsOmdt0ep6DrTllVz+fNttE3kr/byfAGdyDj0wh/C6raeId9dH6FxzcwDZxZ7F21X\nGFPi+4HUk5E/kGZe7kJADFe5oLkWTpaYCjvw/qaEyyAbN9sgAiyJnFBp/41+1qDC\n9PZ1ku+5KkXaKkgZc5f+igHq/Cf6/nA0fQNKNa/WclR2trvTEgMPBE3Zx4lfUjbh\nAkpStiSjAgMBAAECggEAWa3lLKib9Org7APuLT/tVrOzuqNJ5FHEMB+sPaKiacSi\nvNYczr4/umm1BQ7RxCdv/Mc1z4sRDZAj+xZOpF2/NWI0XbTFtRDatuxb8BDDY1lv\nHJEo5m7IUdCgrBw8BOZPiZAPAohGBrqg4Wg/BYW4DviiXX4hwFx8rle+FkS9d4VR\nXbVcFk6YreWfX+VXuiAxA6E+ej+Grrc7KVrn+PNxwCaiVEyCnXulp/ni2ZkHTWu8\nzOXhVd2q4J5gVTcyB1oDUx7s7jcvQw/8XowGTBbz0nRMfCPySi+4u0UK1OKqGdah\n/fa/7TMo6wbFLBjg0yzbhxQG/6yL8fkRbY9aG3iZKQKBgQDe5WLKPd6DZl8rVcom\no2CW4DcWKM7ejPFo+Zy/KYOOMeaFDm3CuO4ww/N0YQ/+R92LaYjqiF8ijA2sTyUr\n2LNizS4rejGgDDGsgcLfw+ePn7oAk8utTTuuNsctmJ3bNwLdddp9IBNxJBxncprU\nuFybkOejaG7vNgZDrapJIoB6JQKBgQDLt8uz5TN1cyAyhcwV19L3KZZikmU4SqEH\n6CfYKGkHBeXKiYOP7JE3CymbwN3rr2X4fNVf73rZnJ8RBBzzWwYslMFmIJvEUBeG\n47NeVgefyAlsR6gNWYLHSqn1bZdBfU6+naeZ09txdmhfuXvEZhvaWO4pn0vDuxH2\nqC111hyVJwKBgQCFa69HueMAqn2bFf4sRK1jgpDWzdSOeLVkjc2ay8G4kvwWdz2S\nSlohjJmk9xi4r9HYSnKvWLQBnO3uT23DojI2mPTjB4C++a2eQgohIUXxvb177PwF\nH27y6E0vaORMvNAVOh9vuIyKs//gmEQ/wp+EayeMs817mM4FIuYEYweelQKBgQCs\n6QHjXWWCCQeJGnuRBrEvzIKyg+OaFe38UhaPqC0NIvpaIMIkRP00pSrZ4qf6RdPd\nR8esOA4j6oYw4TbZb6cb698DmiXcSMbPXTF/nrG18wnceC2xtwoDseH0SOKbWYqe\nzB3XuTSHZ6NLrJnap3h4qgbsGSMrrPqgSzray7NS/QKBgEgMVMyVQZiDIWCIfhGT\nmN4F5jci5CelXs37x1AOIgWL6bVgACB0u8B0P9YZGejKI6uZ8xZYIbnCOvZqTrtS\nTJPGBf23456456234523564352345346577QVesr2yMLI6t7PqoQSqJpw\nIp70HxIrTO4pBys08WVCHbXx\n-----END PRIVATE KEY-----\n"}

{"cmd": "cleanup", "type": "tls-sni-01", "status": "valid", "domain": "bristol3.pki.enigmabridge.com", "token": "xgg9AwsMl8Rtdwh_ZkHozmDEr9G4Z1noCqnbRXp3zyA", "validation": null, "key_auth": "xgg9AwsMl8Rtdwh_ZkHozmDEr9G4Z1noCqnbRXp3zyA.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "validated": null, "error": null}
{"cmd": "cleanup", "type": "tls-sni-01", "status": "valid", "domain": "bs3.pki.enigmabridge.com", "token": "CES4DhcXqr4lxuoae0qINKSndCnRUIE6SegCP6hJBdE", "validation": null, "key_auth": "CES4DhcXqr4lxuoae0qINKSndCnRUIE6SegCP6hJBdE.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "validated": null, "error": null}
{"cmd": "report", "messages": [{"priority": 1, "on_crash": true, "lines": ["Congratulations! Your certificate and chain have been saved at /etc/letsencrypt/live/bristol3.pki.enigmabridge.com/fullchain.pem. Your cert will expire on 2017-01-25. To obtain a new or tweaked version of this certificate in the future, simply run certbot again. To non-interactively renew *all* of your certificates, run \"certbot renew\""]}]}
```

## Example - Dehydrated

The following section demonstrates usage of the plugin with [Dehydrated] DNS hooks.

Note the certbot is run with action `run` so deployment callbacks are called too.

In this repository there is [dehydrated-example.sh] which is a hook stub used in this example.


```bash
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
```

Stdout:

```json
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
```

Stderr:

```
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
```

## Example - Handler

### DNS

In this repository there is a default [handler-example.sh] which can be used as a handler.

```bash
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
```

Stdout:

```json
{"cmd": "perform_challenge", "type": "dns-01", "domain": "bristol3.pki.enigmabridge.com", "token": "_QLSFTRw6qbQaN7gTglBYZuU1L7KAP-bXB_41CAnAvU", "validation": "667drNmQL3vX6bu8YZlgy0wKNBlCny8yrjF1lSaUndc", "txt_domain": "_acme-challenge.bristol3.pki.enigmabridge.com", "key_auth": "_QLSFTRw6qbQaN7gTglBYZuU1L7KAP-bXB_41CAnAvU.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0"}
{"cmd": "perform_challenge", "type": "dns-01", "domain": "bs3.pki.enigmabridge.com", "token": "3gJ87yANDpmuuKVL2ktfQ0_qURQ3mN0IfqgbTU_AGS4", "validation": "ejEDZXYEeYHUxqBAiX4csh8GKkeVX7utK6BBOBshZ1Y", "txt_domain": "_acme-challenge.bs3.pki.enigmabridge.com", "key_auth": "3gJ87yANDpmuuKVL2ktfQ0_qURQ3mN0IfqgbTU_AGS4.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0"}
{"cmd": "cleanup", "type": "dns-01", "status": "pending", "domain": "bristol3.pki.enigmabridge.com", "token": "_QLSFTRw6qbQaN7gTglBYZuU1L7KAP-bXB_41CAnAvU", "validation": "667drNmQL3vX6bu8YZlgy0wKNBlCny8yrjF1lSaUndc", "key_auth": "_QLSFTRw6qbQaN7gTglBYZuU1L7KAP-bXB_41CAnAvU.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "validated": null, "error": null}
{"cmd": "cleanup", "type": "dns-01", "status": "pending", "domain": "bs3.pki.enigmabridge.com", "token": "3gJ87yANDpmuuKVL2ktfQ0_qURQ3mN0IfqgbTU_AGS4", "validation": "ejEDZXYEeYHUxqBAiX4csh8GKkeVX7utK6BBOBshZ1Y", "key_auth": "3gJ87yANDpmuuKVL2ktfQ0_qURQ3mN0IfqgbTU_AGS4.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "validated": null, "error": null}
{"cmd": "report", "messages": [{"priority": 1, "on_crash": true, "lines": ["Congratulations! Your certificate and chain have been saved at /etc/letsencrypt/live/bristol3.pki.enigmabridge.com/fullchain.pem. Your cert will expire on 2017-01-25. To obtain a new or tweaked version of this certificate in the future, simply run certbot again. To non-interactively renew *all* of your certificates, run \"certbot renew\""]}]}
```

Stderr: 

```
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
```

### HTTP

Run the certbot with the following command (just `preferred-challenges` changed):

```bash
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
```

Stdout:

```json
{"cmd": "perform_challenge", "type": "http-01", "domain": "bristol3.pki.enigmabridge.com", "token": "oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY", "validation": "oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "uri": "http://bristol3.pki.enigmabridge.com/.well-known/acme-challenge/oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY", "command": "mkdir -p /tmp/certbot/public_html/.well-known/acme-challenge\ncd /tmp/certbot/public_html\nprintf \"%s\" oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0 > .well-known/acme-challenge/oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY\n# run only once per server:\n$(command -v python2 || command -v python2.7 || command -v python2.6) -c \\\n\"import BaseHTTPServer, SimpleHTTPServer; \\\ns = BaseHTTPServer.HTTPServer(('', 80), SimpleHTTPServer.SimpleHTTPRequestHandler); \\\ns.serve_forever()\" ", "key_auth": "oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0"}
{"cmd": "perform_challenge", "type": "http-01", "domain": "bs3.pki.enigmabridge.com", "token": "L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0", "validation": "L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "uri": "http://bs3.pki.enigmabridge.com/.well-known/acme-challenge/L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0", "command": "mkdir -p /tmp/certbot/public_html/.well-known/acme-challenge\ncd /tmp/certbot/public_html\nprintf \"%s\" L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0 > .well-known/acme-challenge/L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0\n# run only once per server:\n$(command -v python2 || command -v python2.7 || command -v python2.6) -c \\\n\"import BaseHTTPServer, SimpleHTTPServer; \\\ns = BaseHTTPServer.HTTPServer(('', 80), SimpleHTTPServer.SimpleHTTPRequestHandler); \\\ns.serve_forever()\" ", "key_auth": "L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0"}
{"cmd": "cleanup", "type": "http-01", "status": "pending", "domain": "bristol3.pki.enigmabridge.com", "token": "oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY", "validation": "oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "key_auth": "oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "validated": null, "error": null}
{"cmd": "cleanup", "type": "http-01", "status": "pending", "domain": "bs3.pki.enigmabridge.com", "token": "L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0", "validation": "L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "key_auth": "L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "validated": null, "error": null}
{"cmd": "report", "messages": [{"priority": 1, "on_crash": true, "lines": ["Congratulations! Your certificate and chain have been saved at /etc/letsencrypt/live/bristol3.pki.enigmabridge.com/fullchain.pem. Your cert will expire on 2017-01-25. To obtain a new or tweaked version of this certificate in the future, simply run certbot again. To non-interactively renew *all* of your certificates, run \"certbot renew\""]}]}
```

Stderr: 

```
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
```

### TLS-SNI

Run the certbot with the following command (just `preferred-challenges` changed):

```bash
certbot --staging \
        --text --agree-tos --email you@example.com \
        --expand --renew-by-default \
        --configurator certbot-external-auth:out \
        --certbot-external-auth:out-public-ip-logging-ok \
        -d "bristol3.pki.enigmabridge.com" \
        -d "bs3.pki.enigmabridge.com" \
        --preferred-challenges tls-sni \
        --certbot-external-auth:out-handler ./handler-example.sh \
        certonly 2>/dev/null
```

Stdout:

```json
{"cmd": "perform_challenge", "type": "tls-sni-01", "domain": "bristol3.pki.enigmabridge.com", "token": "xgg9AwsMl8Rtdwh_ZkHozmDEr9G4Z1noCqnbRXp3zyA", "z_domain": "9e18429925564832b4acea536aeb30e8.c06f4638a973d2756ab3ff17b8ed68b8.acme.invalid", "validation": "9e18429925564832b4acea536aeb30e8.c06f4638a973d2756ab3ff17b8ed68b8.acme.invalid", "cert_path": "/var/lib/letsencrypt/xgg9AwsMl8Rtdwh_ZkHozmDEr9G4Z1noCqnbRXp3zyA.crt", "key_path": "/var/lib/letsencrypt/xgg9AwsMl8Rtdwh_ZkHozmDEr9G4Z1noCqnbRXp3zyA.pem", "port": "443", "key_auth": "xgg9AwsMl8Rtdwh_ZkHozmDEr9G4Z1noCqnbRXp3zyA.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "cert_pem": "-----BEGIN CERTIFICATE-----\nMIIDIjCCAgqgAwIBAgIQL7xAiyGGk2XO7z+MAyWxUTANBgkqhkiG9w0BAQsFADAQ\nMQ4wDAYDVQQDDAVkdW1teTAeFw0xNjEwMjcxNTI3MjRaFw0xNjExMDMxNTI3MjRa\nMBAxDjAMBgNVBAMMBWR1bW15MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKC\nAQEAn9lru0+nkHAhKoOe6VCd+tBEThcjMb+bYiY5LpMDA1SJdOw7/h+xo6mdQdTi\naUV+CCJvyo5EZeHs8hsIYgT8wzla9QACwptbPIPN4ieD7EEhjzw/fTF6JBsoewBU\nJQqP9Z7K67EquTj9B0DddUc6/R7eLWP2THcNf5DXa/+F7Mkl1RWZCaXwNheymNJ9\nlk5qqQnW5GoXHtnb1U0XH4dIDbCG/kBZ1w9NwVktbOT3wNcPTp9Afly05jn9pOb2\n5pAyntspnImd7IpDlYG/eYo3SS+OeD1XO8C/Qtx9BYE/BQtNdfSnGpGL70zT4rQz\nhvY6UJosfSdRrKaEwg3AkRAB1wIDAQABo3gwdjASBgNVHRMBAf8ECDAGAQH/AgEA\nMGAGA1UdEQRZMFeCBWR1bW15gk45ZTE4NDI5OTI1NTY0ODMyYjRhY2VhNTM2YWVi\nMzBlOC5jMDZmNDYzOGE5NzNkMjc1NmFiM2ZmMTdiOGVkNjhiOC5hY21lLmludmFs\naWQwDQYJKoZIhvcNAQELBQADggEBAD/bhdmAB9r2diWE5/P9yoBBv2TkVzPmF3W5\nA7DPVICERcvCXWqSUM5Evl66YFNkFeGY9NnT7/1EhwaCyfQqs0KRo1WoE6cQZn5i\nF/d5Zw97MDKF6ny1edZgC5mCvTvVgDOFrdsYAL3BH5KXzDhljPnPJ4bKkq6cPY2M\netO+2x+LYqxZpgwLXbEcIJGddFIPHIGa6rMHcwqq4qbR7rK2QZg0RlVicU1cg5Nz\nYPYso6knGlauWj0wh3siuAZxWj3ulwiSpkOH9Nc/O3sM1QZW/KUsauB9zwbqcfmp\nqOFUAR5LW6M9AoA8Jpsb/ELWz64BNQ0c/UoF5iwg6+lgkg9cntU=\n-----END CERTIFICATE-----\n", "key_pem": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCf2Wu7T6eQcCEq\ng57pUJ360EROFyMxv5tiJjkukwMDVIl07Dv+H7GjqZ1B1OJpRX4IIm/KjkRl4ezy\nGwhiBPzDOVr1AALCm1s8g83iJ4PsQSGPPD99MXokGyh7AFQlCo/1nsrrsSq5OP0H\nQN11Rzr9Ht4tY/ZMdw1/kNdr/4XsySXVFZkJpfA2F7KY0n2WTmqpCdbkahce2dvV\nTRcfh0gNsIb+QFnXD03BWS1s5PfA1w9On0B+XLTmOf2k5vbmkDKe2ymciZ3sikOV\ngb95ijdJL454PVc7wL9C3H0FgT8FC0119KcakYvvTNPitDOG9jpQmix9J1GspoTC\nDcCREAHXAgMBAAECggEBAJo8DEHwyqqINsgxtaxD2BsAx1dd5dyDl6btYLE6smaN\nNBA4PG6oIBvdddnmUgvnPIMWzyzvdrmjc5/rS3xgeY7ZEZViTEd/5VmPh6EWJalY\n8sulA1GF4udhuP5tw8L13Q/PBtbB3IpZnXNZOBWIBDflh9TeJfGD0edrVyBirdNY\nf64Xm7DI59tqEv8aG1c9CbmmreP7XQqbK7zbXEg/PP+JfedBdccKPrlcDnzSoA78\n+XoNHPI0GyJ2JhSzApfulJyloa1MGd20XUyJgDTT66zaiCI/UoTUvAUolBDdZqJw\nRiGYFPb5yDI3SnW98WUurLE+VpE15fKNoZlGl6ToQSkCgYEA1FQrWPSzIltDJwui\ncQNWKQpT0Pin4rYb9TjrY5qwDJAoAjBjjvbKphBA63OO3O8xy7TlZn13CAV9Kok8\nI/LYLzANZTNYwfRy0h3aGQj/0qX0O6hdse742Yo6KGrpTGH1ur/Xb1x3H0poevEK\nB/hYYQV2IGv/wcWIKN+bygPsRl0CgYEAwLoHUIl1b1wqGzAN1Zl/jsiXCeGyhGGV\nWMFQkWFjCuYAAVd+gFOzKji6mEIAHg8oHDe3UkODYxkDXJJhxg/rT/qX/sTMeo65\nIcRihVe6PS/dKHA6gTMmQwuQHrKggAHsGFMz9qDHF3QuBXhYT6Xi72LLoYwt4IEj\nJLzc+Xr3fcMCgYBJ0PlA89FTIGc4K9NNdtt9aRm6jLfRGX6ewisTdbO+ql8+Y5Q5\nH5NUKFJpiMMiDAZDy5/1AalgIIhjQVKnLMX7obkGddNlmpZQdhBco8RMd2VxWBc6\nxNm+x09wvbpd07CaPBepn3vKZRPtqd7S5oPTNxLaMrG3q/SqQRLoKHT8AQKBgQC1\n6qLe5XFBFUj1cs2MMqDSAQt4m17rUEUtiwPmxns7nVCh85mHvfnfP77520rLFNly\nkTDsaKfLUZ/3sICz+PDQBKWWKOMuSCv98KZiYSV9fgGOmyjOLZ7PKEn4f/m5+paF\ne3wQL0DeJZ8PMMKDI/1qouG9clkXki2/DrqyjtywCwKBgHrwsxNOandciH8BZ0vr\nvuZnzs/6KIpywHM8u/qRI8P3l/2nQx/rbh9Bip+k3wK6MMmKbYCU2ZS322eldOqW\nmT6iwRkseQsm/sO7IbcO/6pvWDS23452346456345654365+adEEqD3m\nE2UjyPLbhfR9Ey8KBetqmgy9\n-----END PRIVATE KEY-----\n"}
{"cmd": "perform_challenge", "type": "tls-sni-01", "domain": "bs3.pki.enigmabridge.com", "token": "CES4DhcXqr4lxuoae0qINKSndCnRUIE6SegCP6hJBdE", "z_domain": "73453e19da495a7d5fe15d7356bc5798.6422f3f5e556a8fc92699ef9b2fe1974.acme.invalid", "validation": "73453e19da495a7d5fe15d7356bc5798.6422f3f5e556a8fc92699ef9b2fe1974.acme.invalid", "cert_path": "/var/lib/letsencrypt/CES4DhcXqr4lxuoae0qINKSndCnRUIE6SegCP6hJBdE.crt", "key_path": "/var/lib/letsencrypt/CES4DhcXqr4lxuoae0qINKSndCnRUIE6SegCP6hJBdE.pem", "port": "443", "key_auth": "CES4DhcXqr4lxuoae0qINKSndCnRUIE6SegCP6hJBdE.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "cert_pem": "-----BEGIN CERTIFICATE-----\nMIIDIjCCAgqgAwIBAgIQOBpsqM/b5w2xCpImjT8EeTANBgkqhkiG9w0BAQsFADAQ\nMQ4wDAYDVQQDDAVkdW1teTAeFw0xNjEwMjcxNTI3MjRaFw0xNjExMDMxNTI3MjRa\nMBAxDjAMBgNVBAMMBWR1bW15MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKC\nAQEAq0gNleuNFlA4bNVPPEOUp1HQhg0nHi75VPyzfPG8iDcOltW+iwrfMz7eRk1T\nYruXvQxisoH1hyv2ndEFH7hqc5IRX8kCt9lPNSmBYov+krLG8Sxy1uqTQ5y81YXy\nyr/oTSNGtIceyjW4oN+HtlIHOJjlFkvhSammmLP5S/GlR8Qo33bpAVXx1paNClJt\nH1bAYc3wZ6RNXVCFazbaE5yzN1WucsXrwFYkxyPA/sf76/OLsCaHGdSH2v2L5S+h\nPKRFQoI9AsbRU6uIiP7WsGTn1BnivXvtlLEw3VZMS3BuzPNn4Tam/h16fxViTb5c\nJQabxOOOX5m5t3rUOYLP2j08iwIDAQABo3gwdjASBgNVHRMBAf8ECDAGAQH/AgEA\nMGAGA1UdEQRZMFeCBWR1bW15gk43MzQ1M2UxOWRhNDk1YTdkNWZlMTVkNzM1NmJj\nNTc5OC42NDIyZjNmNWU1NTZhOGZjOTI2OTllZjliMmZlMTk3NC5hY21lLmludmFs\naWQwDQYJKoZIhvcNAQELBQADggEBABHFzi+TrNUsU4LswMJqJ5NqU3LjwdZxe974\n+eP3s4cOpoRwBh7PQKzlc4KiB1qv2MTqTjVNiGnFEw3bvs6oUHM610U0yOvuxdIy\nAZ6KfzOO2Hoj8V4v/c+uO2yqiCK33JTprYnie+fgodt3GDv0JcQuUznfBSRS4T2A\nbM3yEZSLKyQL3EmA8Y6DJov/Dh7B8sEepXv3lewO3NxhubhDzG90zYqYq0Ddn56D\nWnduSJ6wIxu/R0ccryBr4nO8ZENqC7h7//GNE7wtCyeNeHyJ/ePcD00MDWyiy80o\nk/GFatmNr8iT73UnN5qgt7LpVxzHHRxcIVPJWu2YDVaGH4oA28o=\n-----END CERTIFICATE-----\n", "key_pem": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCrSA2V640WUDhs\n1U88Q5SnUdCGDSceLvlU/LN88byINw6W1b6LCt8zPt5GTVNiu5e9DGKygfWHK/ad\n0QUfuGpzkhFfyQK32U81KYFii/6SssbxLHLW6pNDnLzVhfLKv+hNI0a0hx7KNbig\n34e2Ugc4mOUWS+FJqaaYs/lL8aVHxCjfdukBVfHWlo0KUm0fVsBhzfBnpE1dUIVr\nNtoTnLM3Va5yxevAViTHI8D+x/vr84uwJocZ1Ifa/YvlL6E8pEVCgj0CxtFTq4iI\n/tawZOfUGeK9e+2UsTDdVkxLcG7M82fhNqb+HXp/FWJNvlwlBpvE445fmbm3etQ5\ngs/aPTyLAgMBAAECggEATh97MtpRa9ADLIDOtyoL75U9iycMpJPAXac1JtQLrgWO\nvfWYB0taKsGOGHrEgdAWkb/IdKsaFiFTRwBDWgh/ZV9GVW4Vs02G9zSLMyuvXbH1\nU6N2bdhoevpOlwWVjCykBCsG4OiQfqKqJ5ZNDDe123bBZr4Nb8/VkOjl2GHLhUOP\nz4ootHaPxBjqmHxAJO+b7xeiX48qNdQEoE7wKBqet3nmmk8tunHgrDWPQ8q6M/DK\nvh1lH3/yrppPb346xKMdhgoGgcjBXLyOSSlmiDEUqTj0qjATassTUQCOfR+ZmJ+l\nRJsqOtxANaHeDKI6KMph7XyHuN6T+GUSXR8ke5ozwQKBgQDi0R3cY728mbyNZq4f\naNa9duux9I7bmqQeRTKs0uWat3MgbpLAbnU9t3RimRbvA9RyB1ex+kND6SMY+3p6\n17FIxCicQXkPxbTfxWFXm7wD41RnbpGTSdkWtBtXErfuHiFZhKEMq5MscqmYO2dL\nsNaNjaN0RDyBbsFJ8z2vFeHYeQKBgQDBUba9OHDhHWXp+h2RFegtrlJaenhUBGSU\nd56RSloQkXzUNN0DbmIpFxmAGB4SgIDy0lwumBK8pLLmNJQSrBWIY0qM40rrilmi\nlU2LQy7/dpBm5gyqBGzlIY7Skt3I7aL4pApBt6UIdQXpq0swAz0nDZLAwOgoXRB1\nvGiJH6DEIwKBgQDScJzY7v2KL8U+GEdzQu0CCoTxreqhm5+rqh4zNNTssEozjAPC\nYHmMklp8ZHdfuVjxlxhpO74PEw6KTkC8GsUUs1LObvyogpGnkFUZWJefr9qOwIp2\ncmzlYKOBLQ/T8MaWbLSTsdixw4zQfkT/eAoIeaJu7CSLHjxdpT3U5WOOWQKBgQCT\nvsbBkKw8cAJessf8BVkf6HWKLsVduMnB6jXm5oM03GwhppEvOSKOMthLXKNHEqz6\nZ6kJ9zGCuQD9DTwJlTkTtobYbDHrGB5vMlpET8FQfqXX7oPJQH6VE3ObHaGhGXUP\nQBeSqC7Z6s3tCvv4otEO0sHQzN3hU1bsFGV0PxbYLwKBgFaM8g0A8YrGM4zx8yJ3\nlGMDLC1q7WFwRhG9/Aq5ARlrkf7o1yxRRJskTUh3Ssn7o2PbMqivp6MjVZVMwEoi\ntl2K/hjWoPcK8l0rxLAU15GJL282IAm9QNW12341235435311324WKAo\nL+0/t9g8UU9gJYerfvAAsQAj\n-----END PRIVATE KEY-----\n"}
{"cmd": "cleanup", "type": "tls-sni-01", "status": "valid", "domain": "bristol3.pki.enigmabridge.com", "token": "xgg9AwsMl8Rtdwh_ZkHozmDEr9G4Z1noCqnbRXp3zyA", "validation": null, "key_auth": "xgg9AwsMl8Rtdwh_ZkHozmDEr9G4Z1noCqnbRXp3zyA.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "validated": null, "error": null}
{"cmd": "cleanup", "type": "tls-sni-01", "status": "valid", "domain": "bs3.pki.enigmabridge.com", "token": "CES4DhcXqr4lxuoae0qINKSndCnRUIE6SegCP6hJBdE", "validation": null, "key_auth": "CES4DhcXqr4lxuoae0qINKSndCnRUIE6SegCP6hJBdE.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "validated": null, "error": null}
{"cmd": "report", "messages": [{"priority": 1, "on_crash": true, "lines": ["Congratulations! Your certificate and chain have been saved at /etc/letsencrypt/live/bristol3.pki.enigmabridge.com/fullchain.pem. Your cert will expire on 2017-01-25. To obtain a new or tweaked version of this certificate in the future, simply run certbot again. To non-interactively renew *all* of your certificates, run \"certbot renew\""]}]}
```

Stderr: 

```
Saving debug log to /var/log/letsencrypt/letsencrypt.log
Starting new HTTPS connection (1): acme-staging.api.letsencrypt.org
Renewing an existing certificate
Performing the following challenges:
tls-sni-01 challenge for bristol3.pki.enigmabridge.com
tls-sni-01 challenge for bs3.pki.enigmabridge.com
Handler output (pre-perform):

-----BEGIN PRE-PERFORM-----
-----END PRE-PERFORM-----

Handler output (perform):

-----BEGIN PERFORM-----
cmd: perform
type: tls-sni-01
domain: bristol3.pki.enigmabridge.com
uri: 
validation: 9e18429925564832b4acea536aeb30e8.c06f4638a973d2756ab3ff17b8ed68b8.acme.invalid
key-auth: xgg9AwsMl8Rtdwh_ZkHozmDEr9G4Z1noCqnbRXp3zyA.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0
z_domain: 9e18429925564832b4acea536aeb30e8.c06f4638a973d2756ab3ff17b8ed68b8.acme.invalid
cert_path: /var/lib/letsencrypt/xgg9AwsMl8Rtdwh_ZkHozmDEr9G4Z1noCqnbRXp3zyA.crt
key_path: /var/lib/letsencrypt/xgg9AwsMl8Rtdwh_ZkHozmDEr9G4Z1noCqnbRXp3zyA.pem
port: 443
json: {"cmd": "perform_challenge", "type": "tls-sni-01", "domain": "bristol3.pki.enigmabridge.com", "token": "xgg9AwsMl8Rtdwh_ZkHozmDEr9G4Z1noCqnbRXp3zyA", "z_domain": "9e18429925564832b4acea536aeb30e8.c06f4638a973d2756ab3ff17b8ed68b8.acme.invalid", "validation": "9e18429925564832b4acea536aeb30e8.c06f4638a973d2756ab3ff17b8ed68b8.acme.invalid", "cert_path": "/var/lib/letsencrypt/xgg9AwsMl8Rtdwh_ZkHozmDEr9G4Z1noCqnbRXp3zyA.crt", "key_path": "/var/lib/letsencrypt/xgg9AwsMl8Rtdwh_ZkHozmDEr9G4Z1noCqnbRXp3zyA.pem", "port": "443", "key_auth": "xgg9AwsMl8Rtdwh_ZkHozmDEr9G4Z1noCqnbRXp3zyA.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "cert_pem": "-----BEGIN CERTIFICATE-----\nMIIDIjCCAgqgAwIBAgIQL7xAiyGGk2XO7z+MAyWxUTANBgkqhkiG9w0BAQsFADAQ\nMQ4wDAYDVQQDDAVkdW1teTAeFw0xNjEwMjcxNTI3MjRaFw0xNjExMDMxNTI3MjRa\nMBAxDjAMBgNVBAMMBWR1bW15MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKC\nAQEAn9lru0+nkHAhKoOe6VCd+tBEThcjMb+bYiY5LpMDA1SJdOw7/h+xo6mdQdTi\naUV+CCJvyo5EZeHs8hsIYgT8wzla9QACwptbPIPN4ieD7EEhjzw/fTF6JBsoewBU\nJQqP9Z7K67EquTj9B0DddUc6/R7eLWP2THcNf5DXa/+F7Mkl1RWZCaXwNheymNJ9\nlk5qqQnW5GoXHtnb1U0XH4dIDbCG/kBZ1w9NwVktbOT3wNcPTp9Afly05jn9pOb2\n5pAyntspnImd7IpDlYG/eYo3SS+OeD1XO8C/Qtx9BYE/BQtNdfSnGpGL70zT4rQz\nhvY6UJosfSdRrKaEwg3AkRAB1wIDAQABo3gwdjASBgNVHRMBAf8ECDAGAQH/AgEA\nMGAGA1UdEQRZMFeCBWR1bW15gk45ZTE4NDI5OTI1NTY0ODMyYjRhY2VhNTM2YWVi\nMzBlOC5jMDZmNDYzOGE5NzNkMjc1NmFiM2ZmMTdiOGVkNjhiOC5hY21lLmludmFs\naWQwDQYJKoZIhvcNAQELBQADggEBAD/bhdmAB9r2diWE5/P9yoBBv2TkVzPmF3W5\nA7DPVICERcvCXWqSUM5Evl66YFNkFeGY9NnT7/1EhwaCyfQqs0KRo1WoE6cQZn5i\nF/d5Zw97MDKF6ny1edZgC5mCvTvVgDOFrdsYAL3BH5KXzDhljPnPJ4bKkq6cPY2M\netO+2x+LYqxZpgwLXbEcIJGddFIPHIGa6rMHcwqq4qbR7rK2QZg0RlVicU1cg5Nz\nYPYso6knGlauWj0wh3siuAZxWj3ulwiSpkOH9Nc/O3sM1QZW/KUsauB9zwbqcfmp\nqOFUAR5LW6M9AoA8Jpsb/ELWz64BNQ0c/UoF5iwg6+lgkg9cntU=\n-----END CERTIFICATE-----\n", "key_pem": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCf2Wu7T6eQcCEq\ng57pUJ360EROFyMxv5tiJjkukwMDVIl07Dv+H7GjqZ1B1OJpRX4IIm/KjkRl4ezy\nGwhiBPzDOVr1AALCm1s8g83iJ4PsQSGPPD99MXokGyh7AFQlCo/1nsrrsSq5OP0H\nQN11Rzr9Ht4tY/ZMdw1/kNdr/4XsySXVFZkJpfA2F7KY0n2WTmqpCdbkahce2dvV\nTRcfh0gNsIb+QFnXD03BWS1s5PfA1w9On0B+XLTmOf2k5vbmkDKe2ymciZ3sikOV\ngb95ijdJL454PVc7wL9C3H0FgT8FC0119KcakYvvTNPitDOG9jpQmix9J1GspoTC\nDcCREAHXAgMBAAECggEBAJo8DEHwyqqINsgxtaxD2BsAx1dd5dyDl6btYLE6smaN\nNBA4PG6oIBvdddnmUgvnPIMWzyzvdrmjc5/rS3xgeY7ZEZViTEd/5VmPh6EWJalY\n8sulA1GF4udhuP5tw8L13Q/PBtbB3IpZnXNZOBWIBDflh9TeJfGD0edrVyBirdNY\nf64Xm7DI59tqEv8aG1c9CbmmreP7XQqbK7zbXEg/PP+JfedBdccKPrlcDnzSoA78\n+XoNHPI0GyJ2JhSzApfulJyloa1MGd20XUyJgDTT66zaiCI/UoTUvAUolBDdZqJw\nRiGYFPb5yDI3SnW98WUurLE+VpE15fKNoZlGl6ToQSkCgYEA1FQrWPSzIltDJwui\ncQNWKQpT0Pin4rYb9TjrY5qwDJAoAjBjjvbKphBA63OO3O8xy7TlZn13CAV9Kok8\nI/LYLzANZTNYwfRy0h3aGQj/0qX0O6hdse742Yo6KGrpTGH1ur/Xb1x3H0poevEK\nB/hYYQV2IGv/wcWIKN+bygPsRl0CgYEAwLoHUIl1b1wqGzAN1Zl/jsiXCeGyhGGV\nWMFQkWFjCuYAAVd+gFOzKji6mEIAHg8oHDe3UkODYxkDXJJhxg/rT/qX/sTMeo65\nIcRihVe6PS/dKHA6gTMmQwuQHrKggAHsGFMz9qDHF3QuBXhYT6Xi72LLoYwt4IEj\nJLzc+Xr3fcMCgYBJ0PlA89FTIGc4K9NNdtt9aRm6jLfRGX6ewisTdbO+ql8+Y5Q5\nH5NUKFJpiMMiDAZDy5/1AalgIIhjQVKnLMX7obkGddNlmpZQdhBco8RMd2VxWBc6\nxNm+x09wvbpd07CaPBepn3vKZRPtqd7S5oPTNxLaMrG3q/SqQRLoKHT8AQKBgQC1\n6qLe5XFBFUj1cs2MMqDSAQt4m17rUEUtiwPmxns7nVCh85mHvfnfP77520rLFNly\nkTDsaKfLUZ/3sICz+PDQBKWWKOMuSCv98KZiYSV9fgGOmyjOLZ7PKEn4f/m5+paF\ne3wQL0DeJZ8PMMKDI/1qouG9clkXki2/DrqyjtywCwKBgHrwsxNOandciH8BZ0vr\nvuZnzs/6KIpywHM8u/qRI8P3l/2nQx/rbh9Bip+k3wK6MMmKbYCU2ZS322eldOqW\nmT6iwRkseQsm/sO7IbcO/6pvW2345234523453425342523452345EqD3m\nE2UjyPLbhfR9Ey8KBetqmgy9\n-----END PRIVATE KEY-----\n"}
-----END PERFORM-----

Self-verify of challenge failed.
Handler output (perform):

-----BEGIN PERFORM-----
cmd: perform
type: tls-sni-01
domain: bs3.pki.enigmabridge.com
uri: 
validation: 73453e19da495a7d5fe15d7356bc5798.6422f3f5e556a8fc92699ef9b2fe1974.acme.invalid
key-auth: CES4DhcXqr4lxuoae0qINKSndCnRUIE6SegCP6hJBdE.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0
z_domain: 73453e19da495a7d5fe15d7356bc5798.6422f3f5e556a8fc92699ef9b2fe1974.acme.invalid
cert_path: /var/lib/letsencrypt/CES4DhcXqr4lxuoae0qINKSndCnRUIE6SegCP6hJBdE.crt
key_path: /var/lib/letsencrypt/CES4DhcXqr4lxuoae0qINKSndCnRUIE6SegCP6hJBdE.pem
port: 443
json: {"cmd": "perform_challenge", "type": "tls-sni-01", "domain": "bs3.pki.enigmabridge.com", "token": "CES4DhcXqr4lxuoae0qINKSndCnRUIE6SegCP6hJBdE", "z_domain": "73453e19da495a7d5fe15d7356bc5798.6422f3f5e556a8fc92699ef9b2fe1974.acme.invalid", "validation": "73453e19da495a7d5fe15d7356bc5798.6422f3f5e556a8fc92699ef9b2fe1974.acme.invalid", "cert_path": "/var/lib/letsencrypt/CES4DhcXqr4lxuoae0qINKSndCnRUIE6SegCP6hJBdE.crt", "key_path": "/var/lib/letsencrypt/CES4DhcXqr4lxuoae0qINKSndCnRUIE6SegCP6hJBdE.pem", "port": "443", "key_auth": "CES4DhcXqr4lxuoae0qINKSndCnRUIE6SegCP6hJBdE.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "cert_pem": "-----BEGIN CERTIFICATE-----\nMIIDIjCCAgqgAwIBAgIQOBpsqM/b5w2xCpImjT8EeTANBgkqhkiG9w0BAQsFADAQ\nMQ4wDAYDVQQDDAVkdW1teTAeFw0xNjEwMjcxNTI3MjRaFw0xNjExMDMxNTI3MjRa\nMBAxDjAMBgNVBAMMBWR1bW15MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKC\nAQEAq0gNleuNFlA4bNVPPEOUp1HQhg0nHi75VPyzfPG8iDcOltW+iwrfMz7eRk1T\nYruXvQxisoH1hyv2ndEFH7hqc5IRX8kCt9lPNSmBYov+krLG8Sxy1uqTQ5y81YXy\nyr/oTSNGtIceyjW4oN+HtlIHOJjlFkvhSammmLP5S/GlR8Qo33bpAVXx1paNClJt\nH1bAYc3wZ6RNXVCFazbaE5yzN1WucsXrwFYkxyPA/sf76/OLsCaHGdSH2v2L5S+h\nPKRFQoI9AsbRU6uIiP7WsGTn1BnivXvtlLEw3VZMS3BuzPNn4Tam/h16fxViTb5c\nJQabxOOOX5m5t3rUOYLP2j08iwIDAQABo3gwdjASBgNVHRMBAf8ECDAGAQH/AgEA\nMGAGA1UdEQRZMFeCBWR1bW15gk43MzQ1M2UxOWRhNDk1YTdkNWZlMTVkNzM1NmJj\nNTc5OC42NDIyZjNmNWU1NTZhOGZjOTI2OTllZjliMmZlMTk3NC5hY21lLmludmFs\naWQwDQYJKoZIhvcNAQELBQADggEBABHFzi+TrNUsU4LswMJqJ5NqU3LjwdZxe974\n+eP3s4cOpoRwBh7PQKzlc4KiB1qv2MTqTjVNiGnFEw3bvs6oUHM610U0yOvuxdIy\nAZ6KfzOO2Hoj8V4v/c+uO2yqiCK33JTprYnie+fgodt3GDv0JcQuUznfBSRS4T2A\nbM3yEZSLKyQL3EmA8Y6DJov/Dh7B8sEepXv3lewO3NxhubhDzG90zYqYq0Ddn56D\nWnduSJ6wIxu/R0ccryBr4nO8ZENqC7h7//GNE7wtCyeNeHyJ/ePcD00MDWyiy80o\nk/GFatmNr8iT73UnN5qgt7LpVxzHHRxcIVPJWu2YDVaGH4oA28o=\n-----END CERTIFICATE-----\n", "key_pem": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCrSA2V640WUDhs\n1U88Q5SnUdCGDSceLvlU/LN88byINw6W1b6LCt8zPt5GTVNiu5e9DGKygfWHK/ad\n0QUfuGpzkhFfyQK32U81KYFii/6SssbxLHLW6pNDnLzVhfLKv+hNI0a0hx7KNbig\n34e2Ugc4mOUWS+FJqaaYs/lL8aVHxCjfdukBVfHWlo0KUm0fVsBhzfBnpE1dUIVr\nNtoTnLM3Va5yxevAViTHI8D+x/vr84uwJocZ1Ifa/YvlL6E8pEVCgj0CxtFTq4iI\n/tawZOfUGeK9e+2UsTDdVkxLcG7M82fhNqb+HXp/FWJNvlwlBpvE445fmbm3etQ5\ngs/aPTyLAgMBAAECggEATh97MtpRa9ADLIDOtyoL75U9iycMpJPAXac1JtQLrgWO\nvfWYB0taKsGOGHrEgdAWkb/IdKsaFiFTRwBDWgh/ZV9GVW4Vs02G9zSLMyuvXbH1\nU6N2bdhoevpOlwWVjCykBCsG4OiQfqKqJ5ZNDDe123bBZr4Nb8/VkOjl2GHLhUOP\nz4ootHaPxBjqmHxAJO+b7xeiX48qNdQEoE7wKBqet3nmmk8tunHgrDWPQ8q6M/DK\nvh1lH3/yrppPb346xKMdhgoGgcjBXLyOSSlmiDEUqTj0qjATassTUQCOfR+ZmJ+l\nRJsqOtxANaHeDKI6KMph7XyHuN6T+GUSXR8ke5ozwQKBgQDi0R3cY728mbyNZq4f\naNa9duux9I7bmqQeRTKs0uWat3MgbpLAbnU9t3RimRbvA9RyB1ex+kND6SMY+3p6\n17FIxCicQXkPxbTfxWFXm7wD41RnbpGTSdkWtBtXErfuHiFZhKEMq5MscqmYO2dL\nsNaNjaN0RDyBbsFJ8z2vFeHYeQKBgQDBUba9OHDhHWXp+h2RFegtrlJaenhUBGSU\nd56RSloQkXzUNN0DbmIpFxmAGB4SgIDy0lwumBK8pLLmNJQSrBWIY0qM40rrilmi\nlU2LQy7/dpBm5gyqBGzlIY7Skt3I7aL4pApBt6UIdQXpq0swAz0nDZLAwOgoXRB1\nvGiJH6DEIwKBgQDScJzY7v2KL8U+GEdzQu0CCoTxreqhm5+rqh4zNNTssEozjAPC\nYHmMklp8ZHdfuVjxlxhpO74PEw6KTkC8GsUUs1LObvyogpGnkFUZWJefr9qOwIp2\ncmzlYKOBLQ/T8MaWbLSTsdixw4zQfkT/eAoIeaJu7CSLHjxdpT3U5WOOWQKBgQCT\nvsbBkKw8cAJessf8BVkf6HWKLsVduMnB6jXm5oM03GwhppEvOSKOMthLXKNHEqz6\nZ6kJ9zGCuQD9DTwJlTkTtobYbDHrGB5vMlpET8FQfqXX7oPJQH6VE3ObHaGhGXUP\nQBeSqC7Z6s3tCvv4otEO0sHQzN3hU1bsFGV0PxbYLwKBgFaM8g0A8YrGM4zx8yJ3\nlGMDLC1q7WFwRhG9/Aq5ARlrkf7o1yxRRJskTUh3Ssn7o2PbMqivp6MjVZVMwEoi\ntl2K/hjWoPcK8l0rxLAU15GJL28223452345234523452345352534WKAo\nL+0/t9g8UU9gJYerfvAAsQAj\n-----END PRIVATE KEY-----\n"}
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
type: tls-sni-01
domain: bristol3.pki.enigmabridge.com
status: valid
token: xgg9AwsMl8Rtdwh_ZkHozmDEr9G4Z1noCqnbRXp3zyA
error: None
json: {"cmd": "cleanup", "type": "tls-sni-01", "status": "valid", "domain": "bristol3.pki.enigmabridge.com", "token": "xgg9AwsMl8Rtdwh_ZkHozmDEr9G4Z1noCqnbRXp3zyA", "validation": null, "key_auth": "xgg9AwsMl8Rtdwh_ZkHozmDEr9G4Z1noCqnbRXp3zyA.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "validated": null, "error": null}
-----END CLEANUP-----

Handler output (cleanup):

-----BEGIN CLEANUP-----
cmd: cleanup
type: tls-sni-01
domain: bs3.pki.enigmabridge.com
status: valid
token: CES4DhcXqr4lxuoae0qINKSndCnRUIE6SegCP6hJBdE
error: None
json: {"cmd": "cleanup", "type": "tls-sni-01", "status": "valid", "domain": "bs3.pki.enigmabridge.com", "token": "CES4DhcXqr4lxuoae0qINKSndCnRUIE6SegCP6hJBdE", "validation": null, "key_auth": "CES4DhcXqr4lxuoae0qINKSndCnRUIE6SegCP6hJBdE.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "validated": null, "error": null}
-----END CLEANUP-----

Handler output (post-cleanup):

-----BEGIN POST-CLEANUP-----
-----END POST-CLEANUP-----

Generating key (2048 bits): /etc/letsencrypt/keys/0243_key-certbot.pem
Creating CSR: /etc/letsencrypt/csr/0243_csr-certbot.pem
```



## Future work

* Add compatibility with [Dehydrated] DNS hooks
* Communicate challenges via named pipes
* Communicate challenges via sockets

## Manual Installation

To install, first install certbot (either on the root or in a virtualenv),
then:

```bash
python setup.py install
```

## Credits

The plugin is based on the
 
* Let's Encrypt nginx plugin 
* [certbot-external]
*  `manual.py` certbot plugin.

Once ticket [2782] is resolved this won't be needed. 

[certbot-external]: https://github.com/marcan/certbot-external
[2782]: https://github.com/certbot/certbot/issues/2782
[handler-example.sh]: https://github.com/EnigmaBridge/certbot-external-auth/blob/master/handler-example.sh
[dehydrated-example.sh]: https://github.com/EnigmaBridge/certbot-external-auth/blob/master/dehydrated-example.sh
[Dehydrated]: https://github.com/lukas2511/dehydrated
