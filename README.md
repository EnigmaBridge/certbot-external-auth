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

### Example - DNS

Run the certbot with the following command:

```bash
certbot --staging \
        --text --agree-tos --email you@example.com \
        --expand --renew-by-default \
        --configurator certbot-external-auth:out \
        --certbot-external-auth:out-public-ip-logging-ok \
        -d "stoke2.pki.enigmabridge.com" \
        -d "st2.pki.enigmabridge.com" \
        --preferred-challenges dns \
        certonly 2>/dev/null
```

Stderr contains string log / report, not in JSON format.

Stdout:

```json
{"cmd": "perform", "type": "dns-01", "domain": "bristol3.pki.enigmabridge.com", "token": "_QLSFTRw6qbQaN7gTglBYZuU1L7KAP-bXB_41CAnAvU", "validation": "667drNmQL3vX6bu8YZlgy0wKNBlCny8yrjF1lSaUndc", "txt_domain": "_acme-challenge.bristol3.pki.enigmabridge.com", "key_auth": "_QLSFTRw6qbQaN7gTglBYZuU1L7KAP-bXB_41CAnAvU.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0"}

{"cmd": "perform", "type": "dns-01", "domain": "bs3.pki.enigmabridge.com", "token": "3gJ87yANDpmuuKVL2ktfQ0_qURQ3mN0IfqgbTU_AGS4", "validation": "ejEDZXYEeYHUxqBAiX4csh8GKkeVX7utK6BBOBshZ1Y", "txt_domain": "_acme-challenge.bs3.pki.enigmabridge.com", "key_auth": "3gJ87yANDpmuuKVL2ktfQ0_qURQ3mN0IfqgbTU_AGS4.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0"}

{"cmd": "cleanup", "type": "dns-01", "status": "pending", "domain": "bristol3.pki.enigmabridge.com", "token": "_QLSFTRw6qbQaN7gTglBYZuU1L7KAP-bXB_41CAnAvU", "validation": "667drNmQL3vX6bu8YZlgy0wKNBlCny8yrjF1lSaUndc", "key_auth": "_QLSFTRw6qbQaN7gTglBYZuU1L7KAP-bXB_41CAnAvU.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "validated": null, "error": null}
{"cmd": "cleanup", "type": "dns-01", "status": "pending", "domain": "bs3.pki.enigmabridge.com", "token": "3gJ87yANDpmuuKVL2ktfQ0_qURQ3mN0IfqgbTU_AGS4", "validation": "ejEDZXYEeYHUxqBAiX4csh8GKkeVX7utK6BBOBshZ1Y", "key_auth": "3gJ87yANDpmuuKVL2ktfQ0_qURQ3mN0IfqgbTU_AGS4.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "validated": null, "error": null}
{"cmd": "report", "messages": [{"priority": 1, "on_crash": true, "lines": ["Congratulations! Your certificate and chain have been saved at /etc/letsencrypt/live/bristol3.pki.enigmabridge.com/fullchain.pem. Your cert will expire on 2017-01-25. To obtain a new or tweaked version of this certificate in the future, simply run certbot again. To non-interactively renew *all* of your certificates, run \"certbot renew\""]}]}
```

After `{"cmd": "validate"}` message the client waits on `\n` on the standard input to continue with the validation.

### Example - HTTP

Run the certbot with the following command (just `preferred-challenges` changed):

```bash
certbot --staging \
        --text --agree-tos --email you@example.com \
        --expand --renew-by-default \
        --configurator certbot-external-auth:out \
        --certbot-external-auth:out-public-ip-logging-ok \
        -d "stoke2.pki.enigmabridge.com" \
        -d "st2.pki.enigmabridge.com" \
        --preferred-challenges http \
        certonly 2>/dev/null
```

Stdout:

```json
{"cmd": "perform", "type": "http-01", "domain": "bristol3.pki.enigmabridge.com", "token": "oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY", "validation": "oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "uri": "http://bristol3.pki.enigmabridge.com/.well-known/acme-challenge/oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY", "command": "mkdir -p /tmp/certbot/public_html/.well-known/acme-challenge\ncd /tmp/certbot/public_html\nprintf \"%s\" oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0 > .well-known/acme-challenge/oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY\n# run only once per server:\n$(command -v python2 || command -v python2.7 || command -v python2.6) -c \\\n\"import BaseHTTPServer, SimpleHTTPServer; \\\ns = BaseHTTPServer.HTTPServer(('', 80), SimpleHTTPServer.SimpleHTTPRequestHandler); \\\ns.serve_forever()\" ", "key_auth": "oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0"}

{"cmd": "perform", "type": "http-01", "domain": "bs3.pki.enigmabridge.com", "token": "L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0", "validation": "L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "uri": "http://bs3.pki.enigmabridge.com/.well-known/acme-challenge/L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0", "command": "mkdir -p /tmp/certbot/public_html/.well-known/acme-challenge\ncd /tmp/certbot/public_html\nprintf \"%s\" L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0 > .well-known/acme-challenge/L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0\n# run only once per server:\n$(command -v python2 || command -v python2.7 || command -v python2.6) -c \\\n\"import BaseHTTPServer, SimpleHTTPServer; \\\ns = BaseHTTPServer.HTTPServer(('', 80), SimpleHTTPServer.SimpleHTTPRequestHandler); \\\ns.serve_forever()\" ", "key_auth": "L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0"}

{"cmd": "cleanup", "type": "http-01", "status": "pending", "domain": "bristol3.pki.enigmabridge.com", "token": "oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY", "validation": "oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "key_auth": "oRezdno4N00Cfp2bLqJe45Ad3mwJ0q3xqIr7HML7RcY.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "validated": null, "error": null}
{"cmd": "cleanup", "type": "http-01", "status": "pending", "domain": "bs3.pki.enigmabridge.com", "token": "L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0", "validation": "L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "key_auth": "L1xK8bOfybszr3MSJpf0oNZkxCDLLY1qzCKUwSwDYj0.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "validated": null, "error": null}
{"cmd": "report", "messages": [{"priority": 1, "on_crash": true, "lines": ["Congratulations! Your certificate and chain have been saved at /etc/letsencrypt/live/bristol3.pki.enigmabridge.com/fullchain.pem. Your cert will expire on 2017-01-25. To obtain a new or tweaked version of this certificate in the future, simply run certbot again. To non-interactively renew *all* of your certificates, run \"certbot renew\""]}]}
```

### Example - TLS-SNI

Run the certbot with the following command (just `preferred-challenges` changed):

```bash
certbot --staging \
        --text --agree-tos --email you@example.com \
        --expand --renew-by-default \
        --configurator certbot-external-auth:out \
        --certbot-external-auth:out-public-ip-logging-ok \
        -d "stoke2.pki.enigmabridge.com" \
        -d "st2.pki.enigmabridge.com" \
        --preferred-challenges tls-sni \
        certonly 2>/dev/null
```

Stdout:

```json
{"cmd": "perform", "type": "tls-sni-01", "domain": "bristol3.pki.enigmabridge.com", "token": "xgg9AwsMl8Rtdwh_ZkHozmDEr9G4Z1noCqnbRXp3zyA", "z_domain": "9e18429925564832b4acea536aeb30e8.c06f4638a973d2756ab3ff17b8ed68b8.acme.invalid", "validation": "9e18429925564832b4acea536aeb30e8.c06f4638a973d2756ab3ff17b8ed68b8.acme.invalid", "cert_path": "/var/lib/letsencrypt/xgg9AwsMl8Rtdwh_ZkHozmDEr9G4Z1noCqnbRXp3zyA.crt", "key_path": "/var/lib/letsencrypt/xgg9AwsMl8Rtdwh_ZkHozmDEr9G4Z1noCqnbRXp3zyA.pem", "port": "443", "key_auth": "xgg9AwsMl8Rtdwh_ZkHozmDEr9G4Z1noCqnbRXp3zyA.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "cert_pem": "-----BEGIN CERTIFICATE-----\nMIIDIzCCAgugAwIBAgIRAKlpRT1rCUNQ02c/1ydKaegwDQYJKoZIhvcNAQELBQAw\nEDEOMAwGA1UEAwwFZHVtbXkwHhcNMTYxMDI3MTUyMTQ1WhcNMTYxMTAzMTUyMTQ1\nWjAQMQ4wDAYDVQQDDAVkdW1teTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoC\nggEBAKlZxWiP1LHEd5CP8tL8ymeeE/Yz5S3CB0/JmFY5vx6wZuqJE7TJ4175BiZ6\n8PxmnMt+5NhRLfY6PfXvpy7ypsDbMItCSWpxRfo9BKsgxdczWsyKMVqPwnWnD+Zv\nXHeTqYrzh/I+J/iLxTtEie48GOeE4xhJLlzUATxGonXrtg5IOJevmu/pp3tQ31MC\nBSKSUcw96yzcRytO9HNLNqpjTrtjXb58ztphlBcqgjtTXWbT+pxJef1W8ReMTTXQ\nyNQz77fH0q7CMBiqyDfriPoP2u0ilKrAgLw+pYi35Cs1KwK6Z+LoYvADpe9JDG2t\nl1kdghG5PT12OeTTxUevZqSzkVUCAwEAAaN4MHYwEgYDVR0TAQH/BAgwBgEB/wIB\nADBgBgNVHREEWTBXggVkdW1teYJOOWUxODQyOTkyNTU2NDgzMmI0YWNlYTUzNmFl\nYjMwZTguYzA2ZjQ2MzhhOTczZDI3NTZhYjNmZjE3YjhlZDY4YjguYWNtZS5pbnZh\nbGlkMA0GCSqGSIb3DQEBCwUAA4IBAQCNSKUr8Yf+w2HtcgiA6VEvGTgAmUZGdFGg\niM/5tefansWvyroneK93a7XsPC/IUYwAsnGz/l36qKvFUHtSpbo0mdUk7X3xPN4q\naDPa1zhGIXKCBBuP4GbKesgjMr1RZEYgJ1sRR3LArFLsd2ZdRqlYi1tKkryUOs1+\njVDHGpiUEx0IIOPFMPsnR/83bJ9UkOChwnlBxy8C/MriETKRVczPUYVut1KJ9On0\n4Lebi/4lAt2kknPlMi+Fl1gutcg0d27MIEXKKnyj4ZZVElJ78gbAKYO7S6NK1EyB\ns9U9DJoCATaCNSjDJXaH9oqbliP1s7USrTEh7TTnY75dI0i40/OT\n-----END CERTIFICATE-----\n", "key_pem": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCpWcVoj9SxxHeQ\nj/LS/MpnnhP2M+UtwgdPyZhWOb8esGbqiRO0yeNe+QYmevD8ZpzLfuTYUS32Oj31\n76cu8qbA2zCLQklqcUX6PQSrIMXXM1rMijFaj8J1pw/mb1x3k6mK84fyPif4i8U7\nRInuPBjnhOMYSS5c1AE8RqJ167YOSDiXr5rv6ad7UN9TAgUiklHMPess3EcrTvRz\nSzaqY067Y12+fM7aYZQXKoI7U11m0/qcSXn9VvEXjE010MjUM++3x9KuwjAYqsg3\n64j6D9rtIpSqwIC8PqWIt+QrNSsCumfi6GLwA6XvSQxtrZdZHYIRuT09djnk08VH\nr2aks5FVAgMBAAECggEALQzegPRSJoAXNnO0qv/ocCwTL1may9Nj0ovUZIu0Fdvj\nZNzWSy+xtqAUTMRDu0Eo0NGO2yStT2Uq+nOoS8rtJTyp60HU+eXsMadtyIBNYPQe\nYW8ZtfesSVQJ3MkfFghH/9jM/1odk/bKnvuana+LCHvHVbySAsu7EGfR7ACqS53n\ny1OmLaj1lNx8RGdMgpHB3ItoI1Yb0Mkvd9nLtK6wR13ODEG89YjjZI5MrSot+ZjJ\nr3dt0hix3aZuLop8wWOBty5atDm0ThPMT8tl12Boi8FK0UuF4zGVQp+02SjyBmgx\nUq+JDLEV0uCwuMpuALUT83bAEoI73rVAcxLbrhw5uQKBgQDcTh/BWw6w1oH0t8Gt\norOl2hZDPJtqcfxnGoO46O5gAbOyEWUzpFqqMA2U/hNbkO9/bc+7agArbV1at7dL\nVO7cn4qz0SuQZtFk6MdieHVEl/8IykDPeMF6SdBMKxkrEXgCPqgkjf5H9c+/ffnS\nu3LmizwAV92VaCvD9V69gG4EdwKBgQDEyiSMAGnKaxlvgzSUytARyhQWQ0XWfBrl\nb27G/gHxbSb4vJJ+PFBg6OEsn4ChElIIs6SDuq8zDh41wprlQXnVHkmahnoolOuX\nHr9G6sRC7OKbBaxuh3vAqqQsPKPADCC3TQQDlcPmAdYM3PpbWDmPkI1WmsquDAsT\nUbzmVIZHkwKBgD1Z+Ff1jsrKghhvkB1V4Se/61FAMJvdMIhaBvLY04GjF7LwSzmt\nfJ5GkZG7jBKE812ObDpqE7AEXeoknYP6HCcOuybGipZFO+0ZMmWG3EmE9r4w7Qma\nPG9c3QhJPFIVJFGjt1muvXC20OsoHwmDsETp44TI82lnQEDrNT4a5QiTAoGAGglg\nwoE/ff+jkuR6LYGT+/aPp85ozBMJf/e5YWy0FxxI/rn8a+VRATFusXe9DhKddfdG\nugMWMRwaFSTVV6XNF8x1EpPeT8Y8UXdI+XoQU4aCCN68TLdyQTCSniO7yqoQHhB7\ninnjPGhbyMHoAfPvUbZfbOj4DgUb5gd3hcYDKi8CgYBCdM0XgwxoY6P0znIws6Ka\ngRXivDqHAD1dO5F84rAwpaUVIBXmUBhKZkJ0GbuEc5zV5OLs9mzm81oa8CYBEGnz\nyD0YR12341234123443645457muA6L+DC/vriFC37ueuMLoTWZEbURjIm71+TrCagdJ\nPcobS+a762mUxguRIeiNxQ==\n-----END PRIVATE KEY-----\n"}

{"cmd": "perform", "type": "tls-sni-01", "domain": "bs3.pki.enigmabridge.com", "token": "CES4DhcXqr4lxuoae0qINKSndCnRUIE6SegCP6hJBdE", "z_domain": "73453e19da495a7d5fe15d7356bc5798.6422f3f5e556a8fc92699ef9b2fe1974.acme.invalid", "validation": "73453e19da495a7d5fe15d7356bc5798.6422f3f5e556a8fc92699ef9b2fe1974.acme.invalid", "cert_path": "/var/lib/letsencrypt/CES4DhcXqr4lxuoae0qINKSndCnRUIE6SegCP6hJBdE.crt", "key_path": "/var/lib/letsencrypt/CES4DhcXqr4lxuoae0qINKSndCnRUIE6SegCP6hJBdE.pem", "port": "443", "key_auth": "CES4DhcXqr4lxuoae0qINKSndCnRUIE6SegCP6hJBdE.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "cert_pem": "-----BEGIN CERTIFICATE-----\nMIIDIjCCAgqgAwIBAgIQGEaZihGes4PR9QWjLDB8/TANBgkqhkiG9w0BAQsFADAQ\nMQ4wDAYDVQQDDAVkdW1teTAeFw0xNjEwMjcxNTIxNDZaFw0xNjExMDMxNTIxNDZa\nMBAxDjAMBgNVBAMMBWR1bW15MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKC\nAQEAsV/srITsHg97SkqyN2Fr2gb06nXLUkF5SgV8/jzNwtltmrAuJWbf+yDWteoY\nc9ZH5kgiWwDUzxiai1kKKjPGso7d36r6mSn5NwJsxPyapNUKGQy4dkwvEjueClgn\ngQDIoIL5nX0EqqAYMrDpnbdHqeg605ZVc/nzbbRN5K/28nwBncg49MIfwuq2niHf\nXR+hcc3MA2cWexdtVxhT4vuB1JORP5BmXu5CQAxXuaC5Fk6WmAo78P6mhMsgGzfb\nIAIsiZxQaf+NftagwvT2dZLvuSpF2ipIGXOX/ooB6vwn+v5wNH0DSjWv1nJUdra7\n0xIDDwRN2ceJX1I24QJKUrYkowIDAQABo3gwdjASBgNVHRMBAf8ECDAGAQH/AgEA\nMGAGA1UdEQRZMFeCBWR1bW15gk43MzQ1M2UxOWRhNDk1YTdkNWZlMTVkNzM1NmJj\nNTc5OC42NDIyZjNmNWU1NTZhOGZjOTI2OTllZjliMmZlMTk3NC5hY21lLmludmFs\naWQwDQYJKoZIhvcNAQELBQADggEBAB1dKs/TLq7b7BEtnwiSr+0SxSWOUzyaYCKM\nh+2qlg6rrxzy2Rec41kGniQCPwOxrZBJJf/qvSQV1hasUG2gvuca2L7eWEbYrIRH\nOUq4kjbzYPIbAKSkaXR/21Rpn5J8TNSfPVMvm2hvTQFylODVnTRLcA0KQJlhkMGn\nuaXCrgQY3wKWCTGYU4KE0AQCyEf/M3wGEAfWjx6KuTfuRLfpXOL+gSEnf+y6n3BK\nE7lzTGZGvqKeRypL1SN7w5Zo6r2m/YKcZ9Sv1Z2f2hG8at0zYWdys/Zj0+xFBjlb\nMFIDwdEzG21AM4ZriRUbiaqpVECtbiBg2tpqK6V1Ga9Nolu9hbs=\n-----END CERTIFICATE-----\n", "key_pem": "-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCxX+yshOweD3tK\nSrI3YWvaBvTqdctSQXlKBXz+PM3C2W2asC4lZt/7INa16hhz1kfmSCJbANTPGJqL\nWQoqM8ayjt3fqvqZKfk3AmzE/Jqk1QoZDLh2TC8SO54KWCeBAMiggvmdfQSqoBgy\nsOmdt0ep6DrTllVz+fNttE3kr/byfAGdyDj0wh/C6raeId9dH6FxzcwDZxZ7F21X\nGFPi+4HUk5E/kGZe7kJADFe5oLkWTpaYCjvw/qaEyyAbN9sgAiyJnFBp/41+1qDC\n9PZ1ku+5KkXaKkgZc5f+igHq/Cf6/nA0fQNKNa/WclR2trvTEgMPBE3Zx4lfUjbh\nAkpStiSjAgMBAAECggEAWa3lLKib9Org7APuLT/tVrOzuqNJ5FHEMB+sPaKiacSi\nvNYczr4/umm1BQ7RxCdv/Mc1z4sRDZAj+xZOpF2/NWI0XbTFtRDatuxb8BDDY1lv\nHJEo5m7IUdCgrBw8BOZPiZAPAohGBrqg4Wg/BYW4DviiXX4hwFx8rle+FkS9d4VR\nXbVcFk6YreWfX+VXuiAxA6E+ej+Grrc7KVrn+PNxwCaiVEyCnXulp/ni2ZkHTWu8\nzOXhVd2q4J5gVTcyB1oDUx7s7jcvQw/8XowGTBbz0nRMfCPySi+4u0UK1OKqGdah\n/fa/7TMo6wbFLBjg0yzbhxQG/6yL8fkRbY9aG3iZKQKBgQDe5WLKPd6DZl8rVcom\no2CW4DcWKM7ejPFo+Zy/KYOOMeaFDm3CuO4ww/N0YQ/+R92LaYjqiF8ijA2sTyUr\n2LNizS4rejGgDDGsgcLfw+ePn7oAk8utTTuuNsctmJ3bNwLdddp9IBNxJBxncprU\nuFybkOejaG7vNgZDrapJIoB6JQKBgQDLt8uz5TN1cyAyhcwV19L3KZZikmU4SqEH\n6CfYKGkHBeXKiYOP7JE3CymbwN3rr2X4fNVf73rZnJ8RBBzzWwYslMFmIJvEUBeG\n47NeVgefyAlsR6gNWYLHSqn1bZdBfU6+naeZ09txdmhfuXvEZhvaWO4pn0vDuxH2\nqC111hyVJwKBgQCFa69HueMAqn2bFf4sRK1jgpDWzdSOeLVkjc2ay8G4kvwWdz2S\nSlohjJmk9xi4r9HYSnKvWLQBnO3uT23DojI2mPTjB4C++a2eQgohIUXxvb177PwF\nH27y6E0vaORMvNAVOh9vuIyKs//gmEQ/wp+EayeMs817mM4FIuYEYweelQKBgQCs\n6QHjXWWCCQeJGnuRBrEvzIKyg+OaFe38UhaPqC0NIvpaIMIkRP00pSrZ4qf6RdPd\nR8esOA4j6oYw4TbZb6cb698DmiXcSMbPXTF/nrG18wnceC2xtwoDseH0SOKbWYqe\nzB3XuTSHZ6NLrJnap3h4qgbsGSMrrPqgSzray7NS/QKBgEgMVMyVQZiDIWCIfhGT\nmN4F5jci5CelXs37x1AOIgWL6bVgACB0u8B0P9YZGejKI6uZ8xZYIbnCOvZqTrtS\nTJPGBf23456456234523564352345346577QVesr2yMLI6t7PqoQSqJpw\nIp70HxIrTO4pBys08WVCHbXx\n-----END PRIVATE KEY-----\n"}

{"cmd": "cleanup", "type": "tls-sni-01", "status": "valid", "domain": "bristol3.pki.enigmabridge.com", "token": "xgg9AwsMl8Rtdwh_ZkHozmDEr9G4Z1noCqnbRXp3zyA", "validation": null, "key_auth": "xgg9AwsMl8Rtdwh_ZkHozmDEr9G4Z1noCqnbRXp3zyA.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "validated": null, "error": null}
{"cmd": "cleanup", "type": "tls-sni-01", "status": "valid", "domain": "bs3.pki.enigmabridge.com", "token": "CES4DhcXqr4lxuoae0qINKSndCnRUIE6SegCP6hJBdE", "validation": null, "key_auth": "CES4DhcXqr4lxuoae0qINKSndCnRUIE6SegCP6hJBdE.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "validated": null, "error": null}
{"cmd": "report", "messages": [{"priority": 1, "on_crash": true, "lines": ["Congratulations! Your certificate and chain have been saved at /etc/letsencrypt/live/bristol3.pki.enigmabridge.com/fullchain.pem. Your cert will expire on 2017-01-25. To obtain a new or tweaked version of this certificate in the future, simply run certbot again. To non-interactively renew *all* of your certificates, run \"certbot renew\""]}]}
```

### Example - Handler, DNS

In this repository there is a default [handler-example.sh] which can be used as a handler.

```bash
certbot --staging \
        --text --agree-tos --email you@example.com \
        --expand --renew-by-default \
        --configurator certbot-external-auth:out \
        --certbot-external-auth:out-public-ip-logging-ok \
        -d "stoke2.pki.enigmabridge.com" \
        -d "st2.pki.enigmabridge.com" \
        --preferred-challenges dns \
        --certbot-external-auth:out-handler handler-example.sh \
        certonly 2>/dev/null
```

Stdout:

```json
{"cmd": "validate", "type": "dns-01", "validation": "qRd8tEFi1SjSLmx6TLnIwCfzVpITStphK3vxfBowP9w", "domain": "_acme-challenge.stoke2.pki.enigmabridge.com", "key_auth": "jFLsUgJjqtEb6vUVO8w_lI1uUnrVqCegndwwFGP83hA.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0"}
{"cmd": "validate", "type": "dns-01", "validation": "UfxAs6ZOlZKpg8Fr6lHiQ3JSckFQkMZf2SsDt85vf88", "domain": "_acme-challenge.st2.pki.enigmabridge.com", "key_auth": "Xy7oP1uDdEhDbEG2yeyDJK61iz9sJjO7x7BAoIxgftE.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0"}
{"cmd": "cleanup", "type": "dns-01", "status": "pending", "token": "jFLsUgJjqtEb6vUVO8w_lI1uUnrVqCegndwwFGP83hA", "domain": "stoke2.pki.enigmabridge.com", "validated": null, "error": null}
{"cmd": "cleanup", "type": "dns-01", "status": "pending", "token": "Xy7oP1uDdEhDbEG2yeyDJK61iz9sJjO7x7BAoIxgftE", "domain": "st2.pki.enigmabridge.com", "validated": null, "error": null}
{"cmd": "report", "messages": [{"priority": 1, "on_crash": true, "lines": ["The following errors were reported by the server:", "", "Domain: stoke2.pki.enigmabridge.com", "Type:   connection", "Detail: DNS problem: NXDOMAIN looking up TXT for _acme-challenge.stoke2.pki.enigmabridge.com", "", "Domain: st2.pki.enigmabridge.com", "Type:   connection", "Detail: DNS problem: NXDOMAIN looking up TXT for _acme-challenge.st2.pki.enigmabridge.com", "", "To fix these errors, please make sure that your domain name was entered correctly and the DNS A record(s) for that domain contain(s) the right IP address. Additionally, please check that your computer has a publicly routable IP address and that no firewalls are preventing the server from communicating with the client. If you're using the webroot plugin, you should also verify that you are serving files from the webroot path you provided."]}]}
```

Stderr: 

```
Saving debug log to /var/log/letsencrypt/letsencrypt.log
Starting new HTTPS connection (1): acme-staging.api.letsencrypt.org
Obtaining a new certificate
Performing the following challenges:
dns-01 challenge for stoke2.pki.enigmabridge.com
dns-01 challenge for st2.pki.enigmabridge.com
Handler output (pre-perform):

-----BEGIN PRE-PERFORM-----
-----END PRE-PERFORM-----

Handler output (perform):

-----BEGIN PERFORM-----
cmd: perform
type: dns-01
domain: _acme-challenge.stoke2.pki.enigmabridge.com
uri: 
validation: qRd8tEFi1SjSLmx6TLnIwCfzVpITStphK3vxfBowP9w
key-auth: jFLsUgJjqtEb6vUVO8w_lI1uUnrVqCegndwwFGP83hA.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0
z_domain: 
cert_path: 
key_path: 
port: 
json: {"cmd": "validate", "type": "dns-01", "validation": "qRd8tEFi1SjSLmx6TLnIwCfzVpITStphK3vxfBowP9w", "domain": "_acme-challenge.stoke2.pki.enigmabridge.com", "key_auth": "jFLsUgJjqtEb6vUVO8w_lI1uUnrVqCegndwwFGP83hA.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0"}
-----END PERFORM-----

Self-verify of challenge failed.
Handler output (perform):

-----BEGIN PERFORM-----
cmd: perform
type: dns-01
domain: _acme-challenge.st2.pki.enigmabridge.com
uri: 
validation: UfxAs6ZOlZKpg8Fr6lHiQ3JSckFQkMZf2SsDt85vf88
key-auth: Xy7oP1uDdEhDbEG2yeyDJK61iz9sJjO7x7BAoIxgftE.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0
z_domain: 
cert_path: 
key_path: 
port: 
json: {"cmd": "validate", "type": "dns-01", "validation": "UfxAs6ZOlZKpg8Fr6lHiQ3JSckFQkMZf2SsDt85vf88", "domain": "_acme-challenge.st2.pki.enigmabridge.com", "key_auth": "Xy7oP1uDdEhDbEG2yeyDJK61iz9sJjO7x7BAoIxgftE.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0"}
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
domain: stoke2.pki.enigmabridge.com
status: pending
token: jFLsUgJjqtEb6vUVO8w_lI1uUnrVqCegndwwFGP83hA
error: 
json: {"cmd": "cleanup", "type": "dns-01", "status": "pending", "token": "jFLsUgJjqtEb6vUVO8w_lI1uUnrVqCegndwwFGP83hA", "domain": "stoke2.pki.enigmabridge.com", "validated": null, "error": null}
-----END CLEANUP-----

Handler output (cleanup):

-----BEGIN CLEANUP-----
cmd: cleanup
type: dns-01
domain: st2.pki.enigmabridge.com
status: pending
token: Xy7oP1uDdEhDbEG2yeyDJK61iz9sJjO7x7BAoIxgftE
error: 
json: {"cmd": "cleanup", "type": "dns-01", "status": "pending", "token": "Xy7oP1uDdEhDbEG2yeyDJK61iz9sJjO7x7BAoIxgftE", "domain": "st2.pki.enigmabridge.com", "validated": null, "error": null}
-----END CLEANUP-----

Handler output (post-cleanup):

-----BEGIN POST-CLEANUP-----
-----END POST-CLEANUP-----

Failed authorization procedure. stoke2.pki.enigmabridge.com (dns-01): urn:acme:error:connection :: The server could not connect to the client to verify the domain :: DNS problem: NXDOMAIN looking up TXT for _acme-challenge.stoke2.pki.enigmabridge.com, st2.pki.enigmabridge.com (dns-01): urn:acme:error:connection :: The server could not connect to the client to verify the domain :: DNS problem: NXDOMAIN looking up TXT for _acme-challenge.st2.pki.enigmabridge.com
```

### Example - Handler, HTTP

Run the certbot with the following command (just `preferred-challenges` changed):

```bash
certbot --staging \
        --text --agree-tos --email you@example.com \
        --expand --renew-by-default \
        --configurator certbot-external-auth:out \
        --certbot-external-auth:out-public-ip-logging-ok \
        -d "stoke2.pki.enigmabridge.com" \
        -d "st2.pki.enigmabridge.com" \
        --preferred-challenges http \
        --certbot-external-auth:out-handler handler-example.sh \
        certonly 2>/dev/null
```

Stdout:

```json
{"cmd": "validate", "type": "http-01", "validation": "8UHf1Qzw1FoR6OdpySMAV8oNsE5vVRR-6W3xw6dRSn4.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "uri": "http://stoke2.pki.enigmabridge.com/.well-known/acme-challenge/8UHf1Qzw1FoR6OdpySMAV8oNsE5vVRR-6W3xw6dRSn4", "command": "mkdir -p /tmp/certbot/public_html/.well-known/acme-challenge\ncd /tmp/certbot/public_html\nprintf \"%s\" 8UHf1Qzw1FoR6OdpySMAV8oNsE5vVRR-6W3xw6dRSn4.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0 > .well-known/acme-challenge/8UHf1Qzw1FoR6OdpySMAV8oNsE5vVRR-6W3xw6dRSn4\n# run only once per server:\n$(command -v python2 || command -v python2.7 || command -v python2.6) -c \\\n\"import BaseHTTPServer, SimpleHTTPServer; \\\ns = BaseHTTPServer.HTTPServer(('', 80), SimpleHTTPServer.SimpleHTTPRequestHandler); \\\ns.serve_forever()\" ", "key_auth": "8UHf1Qzw1FoR6OdpySMAV8oNsE5vVRR-6W3xw6dRSn4.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0"}
{"cmd": "validate", "type": "http-01", "validation": "8ll4_J0LMiomoRtpqpneiPQHYwbxXg1XG5rS0JBXnLw.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "uri": "http://st2.pki.enigmabridge.com/.well-known/acme-challenge/8ll4_J0LMiomoRtpqpneiPQHYwbxXg1XG5rS0JBXnLw", "command": "mkdir -p /tmp/certbot/public_html/.well-known/acme-challenge\ncd /tmp/certbot/public_html\nprintf \"%s\" 8ll4_J0LMiomoRtpqpneiPQHYwbxXg1XG5rS0JBXnLw.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0 > .well-known/acme-challenge/8ll4_J0LMiomoRtpqpneiPQHYwbxXg1XG5rS0JBXnLw\n# run only once per server:\n$(command -v python2 || command -v python2.7 || command -v python2.6) -c \\\n\"import BaseHTTPServer, SimpleHTTPServer; \\\ns = BaseHTTPServer.HTTPServer(('', 80), SimpleHTTPServer.SimpleHTTPRequestHandler); \\\ns.serve_forever()\" ", "key_auth": "8ll4_J0LMiomoRtpqpneiPQHYwbxXg1XG5rS0JBXnLw.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0"}
{"cmd": "cleanup", "type": "http-01", "status": "pending", "token": "8UHf1Qzw1FoR6OdpySMAV8oNsE5vVRR-6W3xw6dRSn4", "domain": "stoke2.pki.enigmabridge.com", "validated": null, "error": null}
{"cmd": "cleanup", "type": "http-01", "status": "pending", "token": "8ll4_J0LMiomoRtpqpneiPQHYwbxXg1XG5rS0JBXnLw", "domain": "st2.pki.enigmabridge.com", "validated": null, "error": null}
{"cmd": "report", "messages": [{"priority": 1, "on_crash": true, "lines": ["The following errors were reported by the server:", "", "Domain: st2.pki.enigmabridge.com", "Type:   unknownHost", "Detail: No valid IP addresses found for st2.pki.enigmabridge.com", "", "Domain: stoke2.pki.enigmabridge.com", "Type:   unknownHost", "Detail: No valid IP addresses found for stoke2.pki.enigmabridge.com", "", "To fix these errors, please make sure that your domain name was entered correctly and the DNS A record(s) for that domain contain(s) the right IP address."]}]}
```

Stderr: 

```
Saving debug log to /var/log/letsencrypt/letsencrypt.log
Starting new HTTPS connection (1): acme-staging.api.letsencrypt.org
Obtaining a new certificate
Performing the following challenges:
http-01 challenge for stoke2.pki.enigmabridge.com
http-01 challenge for st2.pki.enigmabridge.com
Handler output (pre-perform):

-----BEGIN PRE-PERFORM-----
-----END PRE-PERFORM-----

Handler output (perform):

-----BEGIN PERFORM-----
cmd: perform
type: http-01
domain: 
uri: http://stoke2.pki.enigmabridge.com/.well-known/acme-challenge/8UHf1Qzw1FoR6OdpySMAV8oNsE5vVRR-6W3xw6dRSn4
validation: 8UHf1Qzw1FoR6OdpySMAV8oNsE5vVRR-6W3xw6dRSn4.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0
key-auth: 8UHf1Qzw1FoR6OdpySMAV8oNsE5vVRR-6W3xw6dRSn4.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0
z_domain: 
cert_path: 
key_path: 
port: 
json: {"cmd": "validate", "type": "http-01", "validation": "8UHf1Qzw1FoR6OdpySMAV8oNsE5vVRR-6W3xw6dRSn4.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "uri": "http://stoke2.pki.enigmabridge.com/.well-known/acme-challenge/8UHf1Qzw1FoR6OdpySMAV8oNsE5vVRR-6W3xw6dRSn4", "command": "mkdir -p /tmp/certbot/public_html/.well-known/acme-challenge\ncd /tmp/certbot/public_html\nprintf \"%s\" 8UHf1Qzw1FoR6OdpySMAV8oNsE5vVRR-6W3xw6dRSn4.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0 > .well-known/acme-challenge/8UHf1Qzw1FoR6OdpySMAV8oNsE5vVRR-6W3xw6dRSn4\n# run only once per server:\n$(command -v python2 || command -v python2.7 || command -v python2.6) -c \\\n\"import BaseHTTPServer, SimpleHTTPServer; \\\ns = BaseHTTPServer.HTTPServer(('', 80), SimpleHTTPServer.SimpleHTTPRequestHandler); \\\ns.serve_forever()\" ", "key_auth": "8UHf1Qzw1FoR6OdpySMAV8oNsE5vVRR-6W3xw6dRSn4.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0"}
-----END PERFORM-----

Starting new HTTP connection (1): stoke2.pki.enigmabridge.com
Unable to reach http://stoke2.pki.enigmabridge.com/.well-known/acme-challenge/8UHf1Qzw1FoR6OdpySMAV8oNsE5vVRR-6W3xw6dRSn4: HTTPConnectionPool(host='stoke2.pki.enigmabridge.com', port=80): Max retries exceeded with url: /.well-known/acme-challenge/8UHf1Qzw1FoR6OdpySMAV8oNsE5vVRR-6W3xw6dRSn4 (Caused by NewConnectionError('<requests.packages.urllib3.connection.HTTPConnection object at 0x7faa538ca550>: Failed to establish a new connection: [Errno 111] Connection refused',))
Self-verify of challenge failed.
Handler output (perform):

-----BEGIN PERFORM-----
cmd: perform
type: http-01
domain: 
uri: http://st2.pki.enigmabridge.com/.well-known/acme-challenge/8ll4_J0LMiomoRtpqpneiPQHYwbxXg1XG5rS0JBXnLw
validation: 8ll4_J0LMiomoRtpqpneiPQHYwbxXg1XG5rS0JBXnLw.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0
key-auth: 8ll4_J0LMiomoRtpqpneiPQHYwbxXg1XG5rS0JBXnLw.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0
z_domain: 
cert_path: 
key_path: 
port: 
json: {"cmd": "validate", "type": "http-01", "validation": "8ll4_J0LMiomoRtpqpneiPQHYwbxXg1XG5rS0JBXnLw.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "uri": "http://st2.pki.enigmabridge.com/.well-known/acme-challenge/8ll4_J0LMiomoRtpqpneiPQHYwbxXg1XG5rS0JBXnLw", "command": "mkdir -p /tmp/certbot/public_html/.well-known/acme-challenge\ncd /tmp/certbot/public_html\nprintf \"%s\" 8ll4_J0LMiomoRtpqpneiPQHYwbxXg1XG5rS0JBXnLw.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0 > .well-known/acme-challenge/8ll4_J0LMiomoRtpqpneiPQHYwbxXg1XG5rS0JBXnLw\n# run only once per server:\n$(command -v python2 || command -v python2.7 || command -v python2.6) -c \\\n\"import BaseHTTPServer, SimpleHTTPServer; \\\ns = BaseHTTPServer.HTTPServer(('', 80), SimpleHTTPServer.SimpleHTTPRequestHandler); \\\ns.serve_forever()\" ", "key_auth": "8ll4_J0LMiomoRtpqpneiPQHYwbxXg1XG5rS0JBXnLw.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0"}
-----END PERFORM-----

Starting new HTTP connection (1): st2.pki.enigmabridge.com
Unable to reach http://st2.pki.enigmabridge.com/.well-known/acme-challenge/8ll4_J0LMiomoRtpqpneiPQHYwbxXg1XG5rS0JBXnLw: HTTPConnectionPool(host='st2.pki.enigmabridge.com', port=80): Max retries exceeded with url: /.well-known/acme-challenge/8ll4_J0LMiomoRtpqpneiPQHYwbxXg1XG5rS0JBXnLw (Caused by NewConnectionError('<requests.packages.urllib3.connection.HTTPConnection object at 0x7faa538ca690>: Failed to establish a new connection: [Errno 111] Connection refused',))
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
domain: stoke2.pki.enigmabridge.com
status: pending
token: 8UHf1Qzw1FoR6OdpySMAV8oNsE5vVRR-6W3xw6dRSn4
error: 
json: {"cmd": "cleanup", "type": "http-01", "status": "pending", "token": "8UHf1Qzw1FoR6OdpySMAV8oNsE5vVRR-6W3xw6dRSn4", "domain": "stoke2.pki.enigmabridge.com", "validated": null, "error": null}
-----END CLEANUP-----

Handler output (cleanup):

-----BEGIN CLEANUP-----
cmd: cleanup
type: http-01
domain: st2.pki.enigmabridge.com
status: pending
token: 8ll4_J0LMiomoRtpqpneiPQHYwbxXg1XG5rS0JBXnLw
error: 
json: {"cmd": "cleanup", "type": "http-01", "status": "pending", "token": "8ll4_J0LMiomoRtpqpneiPQHYwbxXg1XG5rS0JBXnLw", "domain": "st2.pki.enigmabridge.com", "validated": null, "error": null}
-----END CLEANUP-----

Handler output (post-cleanup):

-----BEGIN POST-CLEANUP-----
-----END POST-CLEANUP-----

Failed authorization procedure. st2.pki.enigmabridge.com (http-01): urn:acme:error:unknownHost :: The server could not resolve a domain name :: No valid IP addresses found for st2.pki.enigmabridge.com, stoke2.pki.enigmabridge.com (http-01): urn:acme:error:unknownHost :: The server could not resolve a domain name :: No valid IP addresses found for stoke2.pki.enigmabridge.com
```

### Example - Handler, TLS-SNI

Run the certbot with the following command (just `preferred-challenges` changed):

```bash
certbot --staging \
        --text --agree-tos --email you@example.com \
        --expand --renew-by-default \
        --configurator certbot-external-auth:out \
        --certbot-external-auth:out-public-ip-logging-ok \
        -d "stoke2.pki.enigmabridge.com" \
        -d "st2.pki.enigmabridge.com" \
        --preferred-challenges tls-sni \
        --certbot-external-auth:out-handler handler-example.sh \
        certonly 2>/dev/null
```

Stdout:

```json
{"cmd": "validate", "type": "tls-sni-01", "domain": "stoke2.pki.enigmabridge.com", "z_domain": "5622ec18934aae89a99151c76c564e76.806248d277161f80d69ed6514efb083a.acme.invalid", "cert_path": "/var/lib/letsencrypt/HAiv_Hd2Tt3zd1t3m7AxQtFh6bffewWSICRN6jXsMpw.crt", "key_path": "/var/lib/letsencrypt/HAiv_Hd2Tt3zd1t3m7AxQtFh6bffewWSICRN6jXsMpw.pem", "port": "443", "key_auth": "HAiv_Hd2Tt3zd1t3m7AxQtFh6bffewWSICRN6jXsMpw.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "cert_pem": "-----BEGIN CERTIFICATE-----\nMIIDIjCCAgqgAwIBAgIQC6afBA93Xzb+UgPfmf6c9DANBgkqhkiG9w0BAQsFADAQ\nMQ4wDAYDVQQDDAVkdW1teTAeFw0xNjEwMjYyMzQ3MzRaFw0xNjExMDIyMzQ3MzRa\nMBAxDjAMBgNVBAMMBWR1bW15MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKC\nAQEAuKjflYNA3YUWfheBOWw0JNOlTcM4Wt5iHobLo6/x9T1fPMDL/pVAwLPQkOnn\niRo/tlwMU6Gv14NTw1S7YRHuGmHCKx8P6PqYrkJTFmcp8PQfVIW5QmYbWPX2GQNw\n36I4ljSeYWI5v+GuRwkg5r7Ya/Xcnt2lHqoD6smL7mChw/cMNulHnzp5GeA9QUhf\nm819nGCBaUYw/Dxg93bIeiCZEsyXiu1N2ARpJNnf2WqrUXsQhhcTRKkiIhkD8kJX\nL9wB+RaT/Ik+le6HGhrbqHWFT2hu2WqvdrGtTBi0jNLQpVcm389aUqE0vgpNSHLr\naIkHM+yuHErxoMM5JDFZb5drHQIDAQABo3gwdjASBgNVHRMBAf8ECDAGAQH/AgEA\nMGAGA1UdEQRZMFeCBWR1bW15gk41NjIyZWMxODkzNGFhZTg5YTk5MTUxYzc2YzU2\nNGU3Ni44MDYyNDhkMjc3MTYxZjgwZDY5ZWQ2NTE0ZWZiMDgzYS5hY21lLmludmFs\naWQwDQYJKoZIhvcNAQELBQADggEBALBJs1n0gthJyjQ4BOsy20y0vZSrtoPMAZLo\n9tAnxbfTyhIXLW4B+ZkF2h/+QjBksEZRQUsNEizhZ7s0+AQHGr+PAOwRI1XkUx43\nrdMg7pXBU5ViyE2qYbx8ZRC9XkCYmiZB6R9FWprD/gTsudgUMhteqguvOOfe9cm4\nHuM361+Y/96awwz1cYP9zMT2mUQEVRlM3/RtcxwQGAJLHuTH0lDZ521YuhlERuwu\nrW9w9FZzoDgCXwsrusmjf7/N5aUMXcZUIOC9vPqS3xL3EPn/cZQbOjjtARPioQgu\nu8lNcgYoPnS9VO/esgKMqV6+fB92fcOAFuONaCzzlmlLt1qZVBk=\n-----END CERTIFICATE-----\n", "key_pem": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQC4qN+Vg0DdhRZ+\nF4E5bDQk06VNwzha3mIehsujr/H1PV88wMv+lUDAs9CQ6eeJGj+2XAxToa/Xg1PD\nVLthEe4aYcIrHw/o+piuQlMWZynw9B9UhblCZhtY9fYZA3DfojiWNJ5hYjm/4a5H\nCSDmvthr9dye3aUeqgPqyYvuYKHD9ww26UefOnkZ4D1BSF+bzX2cYIFpRjD8PGD3\ndsh6IJkSzJeK7U3YBGkk2d/ZaqtRexCGFxNEqSIiGQPyQlcv3AH5FpP8iT6V7oca\nGtuodYVPaG7Zaq92sa1MGLSM0tClVybfz1pSoTS+Ck1IcutoiQcz7K4cSvGgwzkk\nMVlvl2sdAgMBAAECggEALjzKz0swQMeEXEpSZyh63gXIzHHneIlalD44W2JA+aFG\naZX0/mgs8JOV09Nd0GysK2NdCsvfld0iajSbPrEYp652yglbGIE3HdsppuBqFhVq\niuV4//FFQ79CwfyklLqv5JyEU+oef7doxgy5Gk4LLu0/MuBY6ha0KGQTD7tOhhy3\nG9sUTPJ0+z5vbLfJGTLCEFivBFWcfKz0AcnIxrgbHYMMgHVyqkufqBv3VOcqbP6B\nYL1MyAtT0/IM6uT2NFFit+FGZFscLFIVgd036NbylugzapMt1oMwB6YaBHscOwL8\nabEGz67exjsgnwbkbnczlgAoObQAmkJxrE5WDWSLAQKBgQDfV641bJXjcevDUDWT\nxTtP/KmQ6HZ1T6xixxh5U9L3tRZFSwfwflzlVsaiBbt1POGuna01JmK/By3vlgM9\nQrE6L4hQSfudBmwToXN9wNi1Q53tzciLIzV2/hV5g7pPztPnSXh5i8ILCZrZdj2v\nq82azMGDjCnbTXarRCatf0s6fQKBgQDTqTBF9YJj1WRZ0YLHFJGQ0v8dul3WqHPm\n3uBAGmbvv2X61WDWsWK38fYr34BrxiWHfCshhYQClQn0XXcWyVL7T4/Z9vvSrdUa\nlPj1qbqGQlktylpH3ke5dWK1lPsp6Va7+Rj/52M6OVHcbxdyAUEN6L+NYIuB3o/K\n1Edp1D01IQKBgHDyj5hW9KpUd22Lx7yWVvuJhFtTJG0JQN2nYDojaSJ6QuwCGN7H\nmMUmkEdp7LZKdrtu5CRn6DJBODrcu4CklKofVal88LEliUyYLqbe+vkYW+riUdQD\nl0s5DbUpJ/SqXUGvRyz4v8YDMntdL68CjHUHramQHa7ZSvUr/v9oy6ulAoGATLkr\ncnCID0Au3BAB48Ak8+ZH67K+iS0OtkVb7GClp4otoTrvm2M5cYwXu9eMaYSt3eq4\nh7IqI/V6YkXvASeBGO/CKTRKHBg/Ax+1DvezUS+DvAF5sEt2nFdcrI2QbaTTd9fX\npAtwAI7+iXULfpvNxQj1Rn4Uk8LlRJSmPkpc1YECgYB1pLvi6PXGKQrD4WrZNDLV\nTbJhgZXqnOfBMLlU4bBXHMNcxyHMcc2a8D5k1sQMbkmz+ACKprCrwCbChTNoO3d7\n4V13uhfZx58SwzxpPegLzlzJGpAnIN0top6jGbMYA+Y9xdQT/szd06psH2qF8ryq\nGvxKjvrib2Ozb8FyOmQPhw==\n-----END PRIVATE KEY-----\n"}
{"cmd": "validate", "type": "tls-sni-01", "domain": "st2.pki.enigmabridge.com", "z_domain": "61f21f3436004bf6d3943238bddf4bea.fef2bfabc3c2895f5aace483a5986b02.acme.invalid", "cert_path": "/var/lib/letsencrypt/D08c3AuKkWBV6xebn1lmSb4RxHYZ5l6agiu5OoEYaPc.crt", "key_path": "/var/lib/letsencrypt/D08c3AuKkWBV6xebn1lmSb4RxHYZ5l6agiu5OoEYaPc.pem", "port": "443", "key_auth": "D08c3AuKkWBV6xebn1lmSb4RxHYZ5l6agiu5OoEYaPc.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "cert_pem": "-----BEGIN CERTIFICATE-----\nMIIDIjCCAgqgAwIBAgIQBKl0xmWnQyv+BiIrTTUIODANBgkqhkiG9w0BAQsFADAQ\nMQ4wDAYDVQQDDAVkdW1teTAeFw0xNjEwMjYyMzQ3MzRaFw0xNjExMDIyMzQ3MzRa\nMBAxDjAMBgNVBAMMBWR1bW15MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKC\nAQEA1JBtAfRosRsTa91q5uuIX2hXcjFLyfoYnLxRtUymAzBdn4JkSJ9Wh9tEobnt\n9bmNnmmFPAxOOK7gBECqyTwd6s1549PcEDaYrsAsLcchpwAFX7Iu4AwIOzEP70k7\nBIefgJPlhRxfTycalkiV0Bg2qYLCEU0HXOnsXx0vQFVMZaeeDhZI16qcb+xDamBc\nTz3d2J4hiFmbxQKKdK+HZKtc+VdbXSW18u7sCwO11eHBcexyflF6CLgEB2sUUQ7e\n8WOJ7JxrcuUIp5qJneyasGDaKsnqr3izKhLwfr4ni3oyZ2uYPJA7/85c102+d/aF\nesJyQAOAUa/bwNFf1cvh2024JwIDAQABo3gwdjASBgNVHRMBAf8ECDAGAQH/AgEA\nMGAGA1UdEQRZMFeCBWR1bW15gk42MWYyMWYzNDM2MDA0YmY2ZDM5NDMyMzhiZGRm\nNGJlYS5mZWYyYmZhYmMzYzI4OTVmNWFhY2U0ODNhNTk4NmIwMi5hY21lLmludmFs\naWQwDQYJKoZIhvcNAQELBQADggEBAEy0Bqah+nFcUc3OtJ5KYEBw9vBRKrSCPX+J\n/vWHgKAQ4h8VzkrAjAZBRfLddzBwuJbyxkjteef+7sAbdjdp5PAWfu5u6nCxFJTc\nBSSZQ+kyj3kjoB5eQrY3Eq99e6LirqECKxKl1jE4eb5FyU7ItEFXOAiKwvAq5FnB\nMLCm3WgG3N72/SIvSf2upBMCMkHtnZmSQhr/XbbQcBk0oWhmgUkRnee+4/wAuxqf\nZ2SBcM+gAlbgEjWF07sjRDg2PGFjD5Xk3JX+EKz6wJ7eTFjBdhicyCxtxmFtLxgL\n+ljW8a8UzQ+9CJFxRtKDg+0esN3p9nc/G5kXqMM5kNaAqLp6BjA=\n-----END CERTIFICATE-----\n", "key_pem": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDUkG0B9GixGxNr\n3Wrm64hfaFdyMUvJ+hicvFG1TKYDMF2fgmRIn1aH20Shue31uY2eaYU8DE44ruAE\nQKrJPB3qzXnj09wQNpiuwCwtxyGnAAVfsi7gDAg7MQ/vSTsEh5+Ak+WFHF9PJxqW\nSJXQGDapgsIRTQdc6exfHS9AVUxlp54OFkjXqpxv7ENqYFxPPd3YniGIWZvFAop0\nr4dkq1z5V1tdJbXy7uwLA7XV4cFx7HJ+UXoIuAQHaxRRDt7xY4nsnGty5Qinmomd\n7JqwYNoqyeqveLMqEvB+vieLejJna5g8kDv/zlzXTb539oV6wnJAA4BRr9vA0V/V\ny+HbTbgnAgMBAAECggEBAI0L9LlKU7nJbJ6zgr8N5STh2Ly2R0MTyAcg0tsJrFML\nYeR5IlAqIsHtVmI2PNdDs9w8yqLoy3LDX3SS8ICtenCWvd3Wc/zyLWgvrmEF9Kea\n1PYGByK1+TRFvvwZzKaZ09X+zVsBU6DzIqo8KeS2XHcog9v1EACwXB9U/0iiERqV\n4zKcMM7R2A18Hbbh87lFcPZxg5UWo5hywKZTA7PVi5kEUzUcggPKv42vXH4xn0z2\nTLPbGDFxB8/lKM+19bv0JzgosMhT5bhla8WUsAv+K1wZmdIgpsNZ+cZHFgRc/VNj\nRBjoqKPScIMG0z1RbENKug1RIGqlu0TcpfLpYuJ3atkCgYEA/KkbmXiR79JbqOYn\nOxFbIY/aorqwlEtQkaSGswtblQqi/m1aHmFLbvh9YIw/iPP8bSQ4AZmUHmh2HLFf\nfhNcPOLoyoCu6nSAlLZ2f2wphh++xF2KxSE/M19v3HAIrw8yNrDRiqk7qshGTBrh\nmmH685HhdP6E95Eu6GiyvtEnnGUCgYEA11+mPflBqjk3mYEETcq3DExsJYa3iULy\nHTX61222wavjvqS9c4EmqxlNDCiIC4Ninx1cSpokYNCVO1Epg/QHOS+K6/SykKM6\nDPOn+FSA8NxHZtdVa7NJjQaHb1sG4Y+XkTde3qnxEKy9peVdDtBUjX8/08Q0kFqz\n/J40PC7f+5sCgYEAs+iOmId8EzLMxcWspajEJW/TlRAucEn4wtxOdeteeRAr49Nl\n2kAZgJk8XaVAEHr7gZPKtYjwKX7kq6W5g4KxqUFB1gAvjQ8MB9itJCqWnsS4CAc7\nqwbzg9cvRd4YsN63OK5LZtr+e6tEMyjpAA9IrGtyCOa7M7WTmzYCIVG5TOkCgYBl\n0oq98gHhgHuQzzZBsP0pi1f1xeMvub7NoJ+fCffFSIa7sxb+bKjja2rJvL/U8aDG\nqRLhEk7wlqx3BsAh6lUf7CI5u85QI1tmlCttdEYhmYMIU/XGnVTAn72YH+j46vI1\nbYAktSOLRp/CttVwE35mBysd6z0OolNFs2Xurhqm0QKBgQCzzI3yaTfahBV61cyQ\nAyXCDRqJeYNOwORnyfo5uHFdyqpbxCiHl8AWq072GB58wMUl6Xgl8cg0qENcRJmu\n53Ar3FDMgwe2azqpkX0kYqegG3DU3fMc2ICg+75kHp9phdP0SjtUNxDoU8aL3f1X\nGobGNYJ8QPFBqqb2J7+fmXCInw==\n-----END PRIVATE KEY-----\n"}
{"cmd": "cleanup", "type": "tls-sni-01", "status": "pending", "token": "HAiv_Hd2Tt3zd1t3m7AxQtFh6bffewWSICRN6jXsMpw", "domain": "stoke2.pki.enigmabridge.com", "validated": null, "error": null}
{"cmd": "cleanup", "type": "tls-sni-01", "status": "pending", "token": "D08c3AuKkWBV6xebn1lmSb4RxHYZ5l6agiu5OoEYaPc", "domain": "st2.pki.enigmabridge.com", "validated": null, "error": null}
{"cmd": "report", "messages": [{"priority": 1, "on_crash": true, "lines": ["The following errors were reported by the server:", "", "Domain: st2.pki.enigmabridge.com", "Type:   unknownHost", "Detail: No valid IP addresses found for st2.pki.enigmabridge.com", "", "Domain: stoke2.pki.enigmabridge.com", "Type:   unknownHost", "Detail: No valid IP addresses found for stoke2.pki.enigmabridge.com", "", "To fix these errors, please make sure that your domain name was entered correctly and the DNS A record(s) for that domain contain(s) the right IP address."]}]}
```

Stderr: 

```
Saving debug log to /var/log/letsencrypt/letsencrypt.log
Starting new HTTPS connection (1): acme-staging.api.letsencrypt.org
Obtaining a new certificate
Performing the following challenges:
tls-sni-01 challenge for stoke2.pki.enigmabridge.com
tls-sni-01 challenge for st2.pki.enigmabridge.com
Handler output (pre-perform):

-----BEGIN PRE-PERFORM-----
-----END PRE-PERFORM-----

Handler output (perform):

-----BEGIN PERFORM-----
cmd: perform
type: tls-sni-01
domain: stoke2.pki.enigmabridge.com
uri: 
validation: 
key-auth: HAiv_Hd2Tt3zd1t3m7AxQtFh6bffewWSICRN6jXsMpw.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0
z_domain: 5622ec18934aae89a99151c76c564e76.806248d277161f80d69ed6514efb083a.acme.invalid
cert_path: /var/lib/letsencrypt/HAiv_Hd2Tt3zd1t3m7AxQtFh6bffewWSICRN6jXsMpw.crt
key_path: /var/lib/letsencrypt/HAiv_Hd2Tt3zd1t3m7AxQtFh6bffewWSICRN6jXsMpw.pem
port: 443
json: {"cmd": "validate", "type": "tls-sni-01", "domain": "stoke2.pki.enigmabridge.com", "z_domain": "5622ec18934aae89a99151c76c564e76.806248d277161f80d69ed6514efb083a.acme.invalid", "cert_path": "/var/lib/letsencrypt/HAiv_Hd2Tt3zd1t3m7AxQtFh6bffewWSICRN6jXsMpw.crt", "key_path": "/var/lib/letsencrypt/HAiv_Hd2Tt3zd1t3m7AxQtFh6bffewWSICRN6jXsMpw.pem", "port": "443", "key_auth": "HAiv_Hd2Tt3zd1t3m7AxQtFh6bffewWSICRN6jXsMpw.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "cert_pem": "-----BEGIN CERTIFICATE-----\nMIIDIjCCAgqgAwIBAgIQC6afBA93Xzb+UgPfmf6c9DANBgkqhkiG9w0BAQsFADAQ\nMQ4wDAYDVQQDDAVkdW1teTAeFw0xNjEwMjYyMzQ3MzRaFw0xNjExMDIyMzQ3MzRa\nMBAxDjAMBgNVBAMMBWR1bW15MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKC\nAQEAuKjflYNA3YUWfheBOWw0JNOlTcM4Wt5iHobLo6/x9T1fPMDL/pVAwLPQkOnn\niRo/tlwMU6Gv14NTw1S7YRHuGmHCKx8P6PqYrkJTFmcp8PQfVIW5QmYbWPX2GQNw\n36I4ljSeYWI5v+GuRwkg5r7Ya/Xcnt2lHqoD6smL7mChw/cMNulHnzp5GeA9QUhf\nm819nGCBaUYw/Dxg93bIeiCZEsyXiu1N2ARpJNnf2WqrUXsQhhcTRKkiIhkD8kJX\nL9wB+RaT/Ik+le6HGhrbqHWFT2hu2WqvdrGtTBi0jNLQpVcm389aUqE0vgpNSHLr\naIkHM+yuHErxoMM5JDFZb5drHQIDAQABo3gwdjASBgNVHRMBAf8ECDAGAQH/AgEA\nMGAGA1UdEQRZMFeCBWR1bW15gk41NjIyZWMxODkzNGFhZTg5YTk5MTUxYzc2YzU2\nNGU3Ni44MDYyNDhkMjc3MTYxZjgwZDY5ZWQ2NTE0ZWZiMDgzYS5hY21lLmludmFs\naWQwDQYJKoZIhvcNAQELBQADggEBALBJs1n0gthJyjQ4BOsy20y0vZSrtoPMAZLo\n9tAnxbfTyhIXLW4B+ZkF2h/+QjBksEZRQUsNEizhZ7s0+AQHGr+PAOwRI1XkUx43\nrdMg7pXBU5ViyE2qYbx8ZRC9XkCYmiZB6R9FWprD/gTsudgUMhteqguvOOfe9cm4\nHuM361+Y/96awwz1cYP9zMT2mUQEVRlM3/RtcxwQGAJLHuTH0lDZ521YuhlERuwu\nrW9w9FZzoDgCXwsrusmjf7/N5aUMXcZUIOC9vPqS3xL3EPn/cZQbOjjtARPioQgu\nu8lNcgYoPnS9VO/esgKMqV6+fB92fcOAFuONaCzzlmlLt1qZVBk=\n-----END CERTIFICATE-----\n", "key_pem": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQC4qN+Vg0DdhRZ+\nF4E5bDQk06VNwzha3mIehsujr/H1PV88wMv+lUDAs9CQ6eeJGj+2XAxToa/Xg1PD\nVLthEe4aYcIrHw/o+piuQlMWZynw9B9UhblCZhtY9fYZA3DfojiWNJ5hYjm/4a5H\nCSDmvthr9dye3aUeqgPqyYvuYKHD9ww26UefOnkZ4D1BSF+bzX2cYIFpRjD8PGD3\ndsh6IJkSzJeK7U3YBGkk2d/ZaqtRexCGFxNEqSIiGQPyQlcv3AH5FpP8iT6V7oca\nGtuodYVPaG7Zaq92sa1MGLSM0tClVybfz1pSoTS+Ck1IcutoiQcz7K4cSvGgwzkk\nMVlvl2sdAgMBAAECggEALjzKz0swQMeEXEpSZyh63gXIzHHneIlalD44W2JA+aFG\naZX0/mgs8JOV09Nd0GysK2NdCsvfld0iajSbPrEYp652yglbGIE3HdsppuBqFhVq\niuV4//FFQ79CwfyklLqv5JyEU+oef7doxgy5Gk4LLu0/MuBY6ha0KGQTD7tOhhy3\nG9sUTPJ0+z5vbLfJGTLCEFivBFWcfKz0AcnIxrgbHYMMgHVyqkufqBv3VOcqbP6B\nYL1MyAtT0/IM6uT2NFFit+FGZFscLFIVgd036NbylugzapMt1oMwB6YaBHscOwL8\nabEGz67exjsgnwbkbnczlgAoObQAmkJxrE5WDWSLAQKBgQDfV641bJXjcevDUDWT\nxTtP/KmQ6HZ1T6xixxh5U9L3tRZFSwfwflzlVsaiBbt1POGuna01JmK/By3vlgM9\nQrE6L4hQSfudBmwToXN9wNi1Q53tzciLIzV2/hV5g7pPztPnSXh5i8ILCZrZdj2v\nq82azMGDjCnbTXarRCatf0s6fQKBgQDTqTBF9YJj1WRZ0YLHFJGQ0v8dul3WqHPm\n3uBAGmbvv2X61WDWsWK38fYr34BrxiWHfCshhYQClQn0XXcWyVL7T4/Z9vvSrdUa\nlPj1qbqGQlktylpH3ke5dWK1lPsp6Va7+Rj/52M6OVHcbxdyAUEN6L+NYIuB3o/K\n1Edp1D01IQKBgHDyj5hW9KpUd22Lx7yWVvuJhFtTJG0JQN2nYDojaSJ6QuwCGN7H\nmMUmkEdp7LZKdrtu5CRn6DJBODrcu4CklKofVal88LEliUyYLqbe+vkYW+riUdQD\nl0s5DbUpJ/SqXUGvRyz4v8YDMntdL68CjHUHramQHa7ZSvUr/v9oy6ulAoGATLkr\ncnCID0Au3BAB48Ak8+ZH67K+iS0OtkVb7GClp4otoTrvm2M5cYwXu9eMaYSt3eq4\nh7IqI/V6YkXvASeBGO/CKTRKHBg/Ax+1DvezUS+DvAF5sEt2nFdcrI2QbaTTd9fX\npAtwAI7+iXULfpvNxQj1Rn4Uk8LlRJSmPkpc1YECgYB1pLvi6PXGKQrD4WrZNDLV\nTbJhgZXqnOfBMLlU4bBXHMNcxyHMcc2a8D5k1sQMbkmz+ACKprCrwCbChTNoO3d7\n4V13uhfZx58SwzxpPegLzlzJGpAnIN0top6jGbMYA+Y9xdQT/szd06psH2qF8ryq\nGvxKjvrib2Ozb8FyOmQPhw==\n-----END PRIVATE KEY-----\n"}
-----END PERFORM-----

Self-verify of challenge failed.
Handler output (perform):

-----BEGIN PERFORM-----
cmd: perform
type: tls-sni-01
domain: st2.pki.enigmabridge.com
uri: 
validation: 
key-auth: D08c3AuKkWBV6xebn1lmSb4RxHYZ5l6agiu5OoEYaPc.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0
z_domain: 61f21f3436004bf6d3943238bddf4bea.fef2bfabc3c2895f5aace483a5986b02.acme.invalid
cert_path: /var/lib/letsencrypt/D08c3AuKkWBV6xebn1lmSb4RxHYZ5l6agiu5OoEYaPc.crt
key_path: /var/lib/letsencrypt/D08c3AuKkWBV6xebn1lmSb4RxHYZ5l6agiu5OoEYaPc.pem
port: 443
json: {"cmd": "validate", "type": "tls-sni-01", "domain": "st2.pki.enigmabridge.com", "z_domain": "61f21f3436004bf6d3943238bddf4bea.fef2bfabc3c2895f5aace483a5986b02.acme.invalid", "cert_path": "/var/lib/letsencrypt/D08c3AuKkWBV6xebn1lmSb4RxHYZ5l6agiu5OoEYaPc.crt", "key_path": "/var/lib/letsencrypt/D08c3AuKkWBV6xebn1lmSb4RxHYZ5l6agiu5OoEYaPc.pem", "port": "443", "key_auth": "D08c3AuKkWBV6xebn1lmSb4RxHYZ5l6agiu5OoEYaPc.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "cert_pem": "-----BEGIN CERTIFICATE-----\nMIIDIjCCAgqgAwIBAgIQBKl0xmWnQyv+BiIrTTUIODANBgkqhkiG9w0BAQsFADAQ\nMQ4wDAYDVQQDDAVkdW1teTAeFw0xNjEwMjYyMzQ3MzRaFw0xNjExMDIyMzQ3MzRa\nMBAxDjAMBgNVBAMMBWR1bW15MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKC\nAQEA1JBtAfRosRsTa91q5uuIX2hXcjFLyfoYnLxRtUymAzBdn4JkSJ9Wh9tEobnt\n9bmNnmmFPAxOOK7gBECqyTwd6s1549PcEDaYrsAsLcchpwAFX7Iu4AwIOzEP70k7\nBIefgJPlhRxfTycalkiV0Bg2qYLCEU0HXOnsXx0vQFVMZaeeDhZI16qcb+xDamBc\nTz3d2J4hiFmbxQKKdK+HZKtc+VdbXSW18u7sCwO11eHBcexyflF6CLgEB2sUUQ7e\n8WOJ7JxrcuUIp5qJneyasGDaKsnqr3izKhLwfr4ni3oyZ2uYPJA7/85c102+d/aF\nesJyQAOAUa/bwNFf1cvh2024JwIDAQABo3gwdjASBgNVHRMBAf8ECDAGAQH/AgEA\nMGAGA1UdEQRZMFeCBWR1bW15gk42MWYyMWYzNDM2MDA0YmY2ZDM5NDMyMzhiZGRm\nNGJlYS5mZWYyYmZhYmMzYzI4OTVmNWFhY2U0ODNhNTk4NmIwMi5hY21lLmludmFs\naWQwDQYJKoZIhvcNAQELBQADggEBAEy0Bqah+nFcUc3OtJ5KYEBw9vBRKrSCPX+J\n/vWHgKAQ4h8VzkrAjAZBRfLddzBwuJbyxkjteef+7sAbdjdp5PAWfu5u6nCxFJTc\nBSSZQ+kyj3kjoB5eQrY3Eq99e6LirqECKxKl1jE4eb5FyU7ItEFXOAiKwvAq5FnB\nMLCm3WgG3N72/SIvSf2upBMCMkHtnZmSQhr/XbbQcBk0oWhmgUkRnee+4/wAuxqf\nZ2SBcM+gAlbgEjWF07sjRDg2PGFjD5Xk3JX+EKz6wJ7eTFjBdhicyCxtxmFtLxgL\n+ljW8a8UzQ+9CJFxRtKDg+0esN3p9nc/G5kXqMM5kNaAqLp6BjA=\n-----END CERTIFICATE-----\n", "key_pem": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDUkG0B9GixGxNr\n3Wrm64hfaFdyMUvJ+hicvFG1TKYDMF2fgmRIn1aH20Shue31uY2eaYU8DE44ruAE\nQKrJPB3qzXnj09wQNpiuwCwtxyGnAAVfsi7gDAg7MQ/vSTsEh5+Ak+WFHF9PJxqW\nSJXQGDapgsIRTQdc6exfHS9AVUxlp54OFkjXqpxv7ENqYFxPPd3YniGIWZvFAop0\nr4dkq1z5V1tdJbXy7uwLA7XV4cFx7HJ+UXoIuAQHaxRRDt7xY4nsnGty5Qinmomd\n7JqwYNoqyeqveLMqEvB+vieLejJna5g8kDv/zlzXTb539oV6wnJAA4BRr9vA0V/V\ny+HbTbgnAgMBAAECggEBAI0L9LlKU7nJbJ6zgr8N5STh2Ly2R0MTyAcg0tsJrFML\nYeR5IlAqIsHtVmI2PNdDs9w8yqLoy3LDX3SS8ICtenCWvd3Wc/zyLWgvrmEF9Kea\n1PYGByK1+TRFvvwZzKaZ09X+zVsBU6DzIqo8KeS2XHcog9v1EACwXB9U/0iiERqV\n4zKcMM7R2A18Hbbh87lFcPZxg5UWo5hywKZTA7PVi5kEUzUcggPKv42vXH4xn0z2\nTLPbGDFxB8/lKM+19bv0JzgosMhT5bhla8WUsAv+K1wZmdIgpsNZ+cZHFgRc/VNj\nRBjoqKPScIMG0z1RbENKug1RIGqlu0TcpfLpYuJ3atkCgYEA/KkbmXiR79JbqOYn\nOxFbIY/aorqwlEtQkaSGswtblQqi/m1aHmFLbvh9YIw/iPP8bSQ4AZmUHmh2HLFf\nfhNcPOLoyoCu6nSAlLZ2f2wphh++xF2KxSE/M19v3HAIrw8yNrDRiqk7qshGTBrh\nmmH685HhdP6E95Eu6GiyvtEnnGUCgYEA11+mPflBqjk3mYEETcq3DExsJYa3iULy\nHTX61222wavjvqS9c4EmqxlNDCiIC4Ninx1cSpokYNCVO1Epg/QHOS+K6/SykKM6\nDPOn+FSA8NxHZtdVa7NJjQaHb1sG4Y+XkTde3qnxEKy9peVdDtBUjX8/08Q0kFqz\n/J40PC7f+5sCgYEAs+iOmId8EzLMxcWspajEJW/TlRAucEn4wtxOdeteeRAr49Nl\n2kAZgJk8XaVAEHr7gZPKtYjwKX7kq6W5g4KxqUFB1gAvjQ8MB9itJCqWnsS4CAc7\nqwbzg9cvRd4YsN63OK5LZtr+e6tEMyjpAA9IrGtyCOa7M7WTmzYCIVG5TOkCgYBl\n0oq98gHhgHuQzzZBsP0pi1f1xeMvub7NoJ+fCffFSIa7sxb+bKjja2rJvL/U8aDG\nqRLhEk7wlqx3BsAh6lUf7CI5u85QI1tmlCttdEYhmYMIU/XGnVTAn72YH+j46vI1\nbYAktSOLRp/CttVwE35mBysd6z0OolNFs2Xurhqm0QKBgQCzzI3yaTfahBV61cyQ\nAyXCDRqJeYNOwORnyfo5uHFdyqpbxCiHl8AWq072GB58wMUl6Xgl8cg0qENcRJmu\n53Ar3FDMgwe2azqpkX0kYqegG3DU3fMc2ICg+75kHp9phdP0SjtUNxDoU8aL3f1X\nGobGNYJ8QPFBqqb2J7+fmXCInw==\n-----END PRIVATE KEY-----\n"}
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
domain: stoke2.pki.enigmabridge.com
status: pending
token: HAiv_Hd2Tt3zd1t3m7AxQtFh6bffewWSICRN6jXsMpw
error: 
json: {"cmd": "cleanup", "type": "tls-sni-01", "status": "pending", "token": "HAiv_Hd2Tt3zd1t3m7AxQtFh6bffewWSICRN6jXsMpw", "domain": "stoke2.pki.enigmabridge.com", "validated": null, "error": null}
-----END CLEANUP-----

Handler output (cleanup):

-----BEGIN CLEANUP-----
cmd: cleanup
type: tls-sni-01
domain: st2.pki.enigmabridge.com
status: pending
token: D08c3AuKkWBV6xebn1lmSb4RxHYZ5l6agiu5OoEYaPc
error: 
json: {"cmd": "cleanup", "type": "tls-sni-01", "status": "pending", "token": "D08c3AuKkWBV6xebn1lmSb4RxHYZ5l6agiu5OoEYaPc", "domain": "st2.pki.enigmabridge.com", "validated": null, "error": null}
-----END CLEANUP-----

Handler output (post-cleanup):

-----BEGIN POST-CLEANUP-----
-----END POST-CLEANUP-----

Failed authorization procedure. st2.pki.enigmabridge.com (tls-sni-01): urn:acme:error:unknownHost :: The server could not resolve a domain name :: No valid IP addresses found for st2.pki.enigmabridge.com, stoke2.pki.enigmabridge.com (tls-sni-01): urn:acme:error:unknownHost :: The server could not resolve a domain name :: No valid IP addresses found for stoke2.pki.enigmabridge.com
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
[Dehydrated]: https://github.com/lukas2511/dehydrated
