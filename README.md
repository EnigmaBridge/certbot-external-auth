## External authenticator for Certbot

This plugin helps with domain validation process either by calling an external 
program or by printing JSON challenge to stdout for invoker to solve.

Supported challenges:

* DNS
* HTTP
* TLS-SNI

This plugin only supports authentication, not installation.

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
        -a certbot-external-auth:out \
        --certbot-external-auth:out-public-ip-logging-ok \
        -d example.com certonly
```

There are 3 modes of operation:

* JSON mode (default)
* Text mode - fallback to the `manual.py` operation
* Handler mode - auth performed by an external program

### JSON Mode

JSON mode produces one-line JSON objects (`\n` separated) with a challenge to process by the invoker 
on the stdout. 

After the challenge is processed, the invoker is supposed
to send a new line `\n` character to the stdin to continue with the process.

Note JSON mode produces also another JSON objects besides challenges, 
e.g., cleanup and repots. The `\n` is expected only for challenges (perform/validate step).

Reporter was substituted to produce JSON logs so stdout is JSON only.

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
        -a certbot-external-auth:out \
        --certbot-external-auth:out-public-ip-logging-ok \
        -d "stoke2.pki.enigmabridge.com" \
        -d "st2.pki.enigmabridge.com" \
        --preferred-challenges dns \
        certonly 2>/dev/null
```

Stderr contains string log / report, not in JSON format.

Stdout:

```json
{"cmd": "validate", "type": "dns-01", "validation": "rwfX5jrRQXOiXLOgPL0RM4QtVx0oEIK_pA4Y4eSjqOI", "domain": "_acme-challenge.stoke2.pki.enigmabridge.com", "key_auth": "AfWfkObOD6vyCKXA1tE0Y2Eub9kvltKB7DH5zGxSG04.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0"}

{"cmd": "validate", "type": "dns-01", "validation": "BTDDPMZp8JSLTMfWHguVmdRv-BXVfEBWhfdDyQPCv_I", "domain": "_acme-challenge.st2.pki.enigmabridge.com", "key_auth": "he2pUhw6DWhhnqkxIaLrUAJPpswA_6OSXUUInw0uDkY.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0"}

{"cmd": "cleanup", "type": "dns-01", "status": "pending", "token": "AfWfkObOD6vyCKXA1tE0Y2Eub9kvltKB7DH5zGxSG04", "domain": "stoke2.pki.enigmabridge.com", "validated": null, "error": null}
{"cmd": "cleanup", "type": "dns-01", "status": "pending", "token": "he2pUhw6DWhhnqkxIaLrUAJPpswA_6OSXUUInw0uDkY", "domain": "st2.pki.enigmabridge.com", "validated": null, "error": null}
{"cmd": "report", "messages": [{"priority": 1, "on_crash": true, "lines": ["The following errors were reported by the server:", "", "Domain: stoke2.pki.enigmabridge.com", "Type:   connection", "Detail: DNS problem: NXDOMAIN looking up TXT for _acme-challenge.stoke2.pki.enigmabridge.com", "", "Domain: st2.pki.enigmabridge.com", "Type:   connection", "Detail: DNS problem: NXDOMAIN looking up TXT for _acme-challenge.st2.pki.enigmabridge.com", "", "To fix these errors, please make sure that your domain name was entered correctly and the DNS A record(s) for that domain contain(s) the right IP address. Additionally, please check that your computer has a publicly routable IP address and that no firewalls are preventing the server from communicating with the client. If you're using the webroot plugin, you should also verify that you are serving files from the webroot path you provided."]}]}
```

After `{"cmd": "validate"}` message the client waits on `\n` on the standard input to continue with the validation.

### Example - HTTP

Run the certbot with the following command (just `preferred-challenges` changed):

```bash
certbot --staging \
        --text --agree-tos --email you@example.com \
        --expand --renew-by-default \
        -a certbot-external-auth:out \
        --certbot-external-auth:out-public-ip-logging-ok \
        -d "stoke2.pki.enigmabridge.com" \
        -d "st2.pki.enigmabridge.com" \
        --preferred-challenges http \
        certonly 2>/dev/null
```

Stdout:

```json
{"cmd": "validate", "type": "http-01", "validation": "M7eaUb9BYXH8kb1IuTvjxcj5UmhZjbVrHfRHdhjatS4.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "uri": "http://stoke2.pki.enigmabridge.com/.well-known/acme-challenge/M7eaUb9BYXH8kb1IuTvjxcj5UmhZjbVrHfRHdhjatS4", "command": "mkdir -p /tmp/certbot/public_html/.well-known/acme-challenge\ncd /tmp/certbot/public_html\nprintf \"%s\" M7eaUb9BYXH8kb1IuTvjxcj5UmhZjbVrHfRHdhjatS4.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0 > .well-known/acme-challenge/M7eaUb9BYXH8kb1IuTvjxcj5UmhZjbVrHfRHdhjatS4\n# run only once per server:\n$(command -v python2 || command -v python2.7 || command -v python2.6) -c \\\n\"import BaseHTTPServer, SimpleHTTPServer; \\\ns = BaseHTTPServer.HTTPServer(('', 80), SimpleHTTPServer.SimpleHTTPRequestHandler); \\\ns.serve_forever()\" ", "key_auth": "M7eaUb9BYXH8kb1IuTvjxcj5UmhZjbVrHfRHdhjatS4.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0"}

{"cmd": "validate", "type": "http-01", "validation": "E2MeY_tgp6yPw9K8ivMb_TCMTSrOkF0zbjxIInu0yXQ.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "uri": "http://st2.pki.enigmabridge.com/.well-known/acme-challenge/E2MeY_tgp6yPw9K8ivMb_TCMTSrOkF0zbjxIInu0yXQ", "command": "mkdir -p /tmp/certbot/public_html/.well-known/acme-challenge\ncd /tmp/certbot/public_html\nprintf \"%s\" E2MeY_tgp6yPw9K8ivMb_TCMTSrOkF0zbjxIInu0yXQ.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0 > .well-known/acme-challenge/E2MeY_tgp6yPw9K8ivMb_TCMTSrOkF0zbjxIInu0yXQ\n# run only once per server:\n$(command -v python2 || command -v python2.7 || command -v python2.6) -c \\\n\"import BaseHTTPServer, SimpleHTTPServer; \\\ns = BaseHTTPServer.HTTPServer(('', 80), SimpleHTTPServer.SimpleHTTPRequestHandler); \\\ns.serve_forever()\" ", "key_auth": "E2MeY_tgp6yPw9K8ivMb_TCMTSrOkF0zbjxIInu0yXQ.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0"}

{"cmd": "cleanup", "type": "http-01", "status": "pending", "token": "M7eaUb9BYXH8kb1IuTvjxcj5UmhZjbVrHfRHdhjatS4", "domain": "stoke2.pki.enigmabridge.com", "validated": null, "error": null}
{"cmd": "cleanup", "type": "http-01", "status": "pending", "token": "E2MeY_tgp6yPw9K8ivMb_TCMTSrOkF0zbjxIInu0yXQ", "domain": "st2.pki.enigmabridge.com", "validated": null, "error": null}
{"cmd": "report", "messages": [{"priority": 1, "on_crash": true, "lines": ["The following errors were reported by the server:", "", "Domain: st2.pki.enigmabridge.com", "Type:   unknownHost", "Detail: No valid IP addresses found for st2.pki.enigmabridge.com", "", "Domain: stoke2.pki.enigmabridge.com", "Type:   unknownHost", "Detail: No valid IP addresses found for stoke2.pki.enigmabridge.com", "", "To fix these errors, please make sure that your domain name was entered correctly and the DNS A record(s) for that domain contain(s) the right IP address."]}]}
```

### Example - TLS-SNI

Run the certbot with the following command (just `preferred-challenges` changed):

```bash
certbot --staging \
        --text --agree-tos --email you@example.com \
        --expand --renew-by-default \
        -a certbot-external-auth:out \
        --certbot-external-auth:out-public-ip-logging-ok \
        -d "stoke2.pki.enigmabridge.com" \
        -d "st2.pki.enigmabridge.com" \
        --preferred-challenges tls-sni \
        certonly 2>/dev/null
```

Stdout:

```json
{"cmd": "validate", "type": "tls-sni-01", "domain": "stoke2.pki.enigmabridge.com", "z_domain": "271c1cc2d19ad0d19bc70e0de6b54478.26590d8a282d0ea1744a6e8acab92042.acme.invalid", "cert_path": "/var/lib/letsencrypt/kPGFQWIJr1HM07UgRLLp1FCeVrx3N60CwP_QV9c5hHs.crt", "key_path": "/var/lib/letsencrypt/kPGFQWIJr1HM07UgRLLp1FCeVrx3N60CwP_QV9c5hHs.pem", "port": "443", "key_auth": "kPGFQWIJr1HM07UgRLLp1FCeVrx3N60CwP_QV9c5hHs.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "cert_pem": "-----BEGIN CERTIFICATE-----\nMIIDIjCCAgqgAwIBAgIQDdQModuq16h2S98RWViUNTANBgkqhkiG9w0BAQsFADAQ\nMQ4wDAYDVQQDDAVkdW1teTAeFw0xNjEwMjYyMjI2MjNaFw0xNjExMDIyMjI2MjNa\nMBAxDjAMBgNVBAMMBWR1bW15MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKC\nAQEAk/Cd5YZQ06wlWD+wyzDK234/ZiTQeseJE1GfoPhWO3K3Vem8AVzvNxud85Ot\npurD1/GA+8BmhSYxSk+aI5mAE94d10uhFzrMMqFOCdkesq5f3PLcItQBz3xQmKHW\n/HEsQVRYwgTAOw+uARjDc12suBdVEHzn5OMrC7Om+gvn5Ibb9u23sDzzu2F2YVCw\nUO//izMNbjS24gHaKkvOa1Q3JHiNQSg0Cn9xWBgo0yNHQtWosTgUSBL6HmWlOiM/\nFqP+bZZLWg3h6dPWCIEsEkxcUOh3eKrMBSp8WEHVQpmRg+uBek+toZ7rWM+4jnZN\nGbqY56mLjZbmB57pphmpBix5WQIDAQABo3gwdjASBgNVHRMBAf8ECDAGAQH/AgEA\nMGAGA1UdEQRZMFeCBWR1bW15gk4yNzFjMWNjMmQxOWFkMGQxOWJjNzBlMGRlNmI1\nNDQ3OC4yNjU5MGQ4YTI4MmQwZWExNzQ0YTZlOGFjYWI5MjA0Mi5hY21lLmludmFs\naWQwDQYJKoZIhvcNAQELBQADggEBAGJqiKVuOOETaHrTgCmD/0B5A9EKlYQNiznw\nouG6DxQIG/egtpELSXiEmfT1D+VTtyx5vcm9HKCwXyckjED0WOOlFANvRp5XeKBe\nOfONcozSRK0+GUKan1N+UDGuMSUIYdgFDUo1uW/Qg39DeLOrhwYCxdiwKL/ioA+a\nh1FHr+oTniZ80LWtwWNcp++vZQUjqkcBt6pKTsCQ+uQ73dtgswIlHVUNiSQcjcD9\nMqpVjzWm2E2WwJkrdPrCvaA5kjGZj77ywLkBBMtAZju3MZGX3qoL/2AeQExcAawB\n3h80nLh30d1Lj95Gz92lvvEbstqqsRPK6ck3XmaDkCmAc36XOoU=\n-----END CERTIFICATE-----\n", "key_pem": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCT8J3lhlDTrCVY\nP7DLMMrbfj9mJNB6x4kTUZ+g+FY7crdV6bwBXO83G53zk62m6sPX8YD7wGaFJjFK\nT5ojmYAT3h3XS6EXOswyoU4J2R6yrl/c8twi1AHPfFCYodb8cSxBVFjCBMA7D64B\nGMNzXay4F1UQfOfk4ysLs6b6C+fkhtv27bewPPO7YXZhULBQ7/+LMw1uNLbiAdoq\nS85rVDckeI1BKDQKf3FYGCjTI0dC1aixOBRIEvoeZaU6Iz8Wo/5tlktaDeHp09YI\ngSwSTFxQ6Hd4qswFKnxYQdVCmZGD64F6T62hnutYz7iOdk0ZupjnqYuNluYHnumm\nGakGLHlZAgMBAAECggEAI9+xKjtL1khkNeYb5OnMBzWyAf7jXyKLptegMdSGdJv4\nwSiQonP6vg5AWxRwg41iODcj4+hf8+GzCiYLZp6OZEL0UYTRZ2Smp5Bd8B1qSEHo\nlRd/MiLe3YVztc9o5oY7CQx/CW1FgAzpUPLEUnFgtLNTuU/Qm7xKb+f8kZ3ZeZyr\n0DQwgzOo0NjmAnUDK/LDeCxNlNiJOQQ5p4lg3HhcE7XTtfDBmPY3G+9fB/3gbIVH\nrVT0acH/uvLlCZTYX6Ts0ARnqi+LKLb+r6zG9qTYOVWvgmHOYMpPxDjHPfocp0cf\njFrI3ZGSdaqzzN9huaxsjn+LEWHn+bmMS6t3rv/0AQKBgQDDaOjsD6ETK9NIpTty\n6kVs+4hH1ds0jGP8iQl8G0ESpaiLg6S7cR2CobbxLOvNxV08/Tv4p7WgpqFB2pe1\nRZ7bFkYiirMI6uFLp78azHgAeJgE0lUmZGUwPqxl+22Oz5SFRWopIv7gVBiPmkeS\nCzhqaRuZ4EK3BLgjvrna8HhBeQKBgQDBz62J+l0uhNTh1znQChtHUX20HV+pW2R5\nwnVpesaFRoe4Wka3ZUH4uskq5sQQnakQ30Zfj8QZZ3y8m6HuIkBpLGE9Yy5uKJol\nPI3lqN5+SFX5xMqFC+o1osHGSQTKsCe1dymbConggO1j+6uQUb508GjN5piG+JE8\nQExbKFTe4QKBgQCcx34hb4S3YfEZluA0mbtr7f9wSyedaIoMIlKGzUMPV/P7Q3qW\nnPGlTmP96iGirZfaB/7myH/Tzf0RXfVcDeifNKa+rfNo0zJBRevw713UWuz06WBB\n9kitRYuCIxDKhMdPidrb+GTvzOkLxidoCDKSRZRMh/5e4p1uqGZrP4XsWQKBgG8P\nhh+CI7GLlr4P6mYn1Hfq38C98FqJL6uCXmviWi53O0DOIqXnVYWl66806/elkQNF\nHvuV08bHAbjG6mUepZBfSR23XxzrEWHzMFEBkvYEl5f4SCEzsbOon6fzodZQWYDo\nVyQsRtQqrV5VEnwyC5TRSw1qbc8yU2+WXOsD0pahAoGAfbpouBLbqO+y661K/pFu\nuEviE27r+9mRascUt6OpGCzwDsFu/aaadVmPxaiyqM0758pt8SixvvWvBj3gKcfY\nJdrMGxE73JG0PdlcatX34tzQjtFPaA9NQwVtrj28HQaleGgCOwn2tW1wPndUZFGK\nGUcZuhu0c0WkD83bnYKw3v8=\n-----END PRIVATE KEY-----\n"}

{"cmd": "validate", "type": "tls-sni-01", "domain": "st2.pki.enigmabridge.com", "z_domain": "2b6de2ffbeafcf72fa2500fcb94d8f01.c063b3eb7cccc4101b9bebae3f93d233.acme.invalid", "cert_path": "/var/lib/letsencrypt/dbowNJLZiuxPO83RQv1egT12cgnFP_VPvbGmMKWWfQg.crt", "key_path": "/var/lib/letsencrypt/dbowNJLZiuxPO83RQv1egT12cgnFP_VPvbGmMKWWfQg.pem", "port": "443", "key_auth": "dbowNJLZiuxPO83RQv1egT12cgnFP_VPvbGmMKWWfQg.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "cert_pem": "-----BEGIN CERTIFICATE-----\nMIIDIzCCAgugAwIBAgIRAMIQsaVSIBl+KZTZrcHJRoUwDQYJKoZIhvcNAQELBQAw\nEDEOMAwGA1UEAwwFZHVtbXkwHhcNMTYxMDI2MjIyNjI0WhcNMTYxMTAyMjIyNjI0\nWjAQMQ4wDAYDVQQDDAVkdW1teTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoC\nggEBAKoXB5o1mY/BcUUEeYqvNBFl9CRUsgU8l5IYUvm4kyXPS7ieu9u9LJj3fHQD\no/Q2Wlwq8nQ4ZbmHuE11MdQvjxGarWk+zeJRZ7/JIVFdGkPCbYs1Q8UEbfHzUKU2\nwH0alT/REeJbiazRdRpzpLO9RmCT7WvH2Q911/N2WULKR1dkhmEUE0lsINhbt5ZM\na9UjzinW0arZKzIl6SZcut/30uhuDYkN/Y3KUEBBq530q2e2YdZafUGEyinjH8Df\nr4n+jmIG+Dxs+ymFCzsnAICIJwYx4iVr6HYenKcXvG9k6dDazpK5PbuzMJrv4MMP\nE/0hfqlhOjmvRp8TopIDt+eYZucCAwEAAaN4MHYwEgYDVR0TAQH/BAgwBgEB/wIB\nADBgBgNVHREEWTBXggVkdW1teYJOMmI2ZGUyZmZiZWFmY2Y3MmZhMjUwMGZjYjk0\nZDhmMDEuYzA2M2IzZWI3Y2NjYzQxMDFiOWJlYmFlM2Y5M2QyMzMuYWNtZS5pbnZh\nbGlkMA0GCSqGSIb3DQEBCwUAA4IBAQCUz5lKTe9P25XlB0Of50LWIRUxL/4+u7UH\n4EaAadkKofmKzSAQxLG9ORkWO8T0OrW5rqvOao2WYWnoEdtgu/XKXq3NJxp9RRK7\nxsF3TYhk04GNsH3ycbwoUOkD1rsAt5YW9ls+IDECTKKVc1FfVlMR0JUszpTzzvBW\nnUuCzlXylcgNVzzRSuckMZMsfIwkyT9v1XjviYK0auUv/eEryLqBXn9Qke6YyVWd\nDDOg0oLFo9hPLy5bVOr7XLa0Yd83r5GYg0IwtuE4emL56QkX7U7Uz+zTRo/tKQIR\nhKJIxzR7AxOBuv8OP5G8iPxzCEGTNVAuLKYoUikLtY61vLhfoBN8\n-----END CERTIFICATE-----\n", "key_pem": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQCqFweaNZmPwXFF\nBHmKrzQRZfQkVLIFPJeSGFL5uJMlz0u4nrvbvSyY93x0A6P0NlpcKvJ0OGW5h7hN\ndTHUL48Rmq1pPs3iUWe/ySFRXRpDwm2LNUPFBG3x81ClNsB9GpU/0RHiW4ms0XUa\nc6SzvUZgk+1rx9kPddfzdllCykdXZIZhFBNJbCDYW7eWTGvVI84p1tGq2SsyJekm\nXLrf99Lobg2JDf2NylBAQaud9KtntmHWWn1BhMop4x/A36+J/o5iBvg8bPsphQs7\nJwCAiCcGMeIla+h2HpynF7xvZOnQ2s6SuT27szCa7+DDDxP9IX6pYTo5r0afE6KS\nA7fnmGbnAgMBAAECggEBAJs0Anrjd+kmEY5xw9oZfwB1MK7KHdsLbB8iVOyLULIK\nksS3CyI6X2yBP624+K1Jv3AkvDHymFgQEMuVKc+9SeY9ZwkHBuUBdRMam21b8DBu\nRHjnNJydKxnA9RCcgk5lqFSgGJqc/maUhi+J4HsmNgbAVL+pj1Y9KL1+e3qniyuh\nEFtYcBnS0mYla8Pe295ImBnQsMYXnMVbESq1jQ5swmrAWhwtri5+/jRiDEBC5aJL\nwiYVwWqYWrpOYK1gy4aqQlvB+9QDkgTY1v7xU8OT0GLzmGFz0mRqQ5w+Dcwgg5yB\nqzDe/GC+hPQn6Sw0QV9AVUSIJLisqWMMLQ175DW4RWECgYEA3IU89mT8HP5eaoS0\ncJCr40BZWbKQ7AJyMgz+TGkfPYq7DMiYOO3o1cQ67DQgdtSLC62IeaQmMYZ7M57B\n9VTr7/VApPqsM/LvyZc8Ctr1/GRhwyxYF5WN158aWY6kqJHacdDEIgLIW8V7U+pY\n4KVx0Jx3DnLFyDKqHFte6FQBtvcCgYEAxXSrBJ5j3XCAS7+8kSCIahhFtTVj0PD8\n7+uDceJ/awJKeS7ffJxvFiKW5ho/PGqmMyNsL/RU/RTpofbLyJFRVnNdo3EVuSYW\n5y/Caq+etamo7aGqYhd5LX2e7t2f585Pi/pBHS3R0dAa0mSZmP5n4h6C+Jq0y89X\nMFueLCtEI5ECgYEAnu/9D02blD4VyMoazyLGcIUZoRedci0VJ1PMGUCO/qk1xbHy\nXN3EOgYzvbiYSW1JRkJtodaYnItj0sGy4+KwJoPqcr4lTU/kWbSB1wUX1DB5cdVN\nLLpiwCzxLeksbj6pZezk3+qHg/VivQmjw04bKRMMkEJSoMc7ajLExch+b+MCgYBR\nsQUYMheLBAJwVHFFcbo+erBMWjxjs3BSKpQFR/oDYb1CCbx4p5fmBoV7yZwj+NOu\nEJev91w6IK7QTXTeFBEcvToeZqjgIvwSxdWfoez9p6W2Os5tKtz9jx10IckIdHjA\nptbNpalLLtgJ94j8nTSJfqodBJSMRcoCvcTg7T2RoQKBgQCo4hIi2PshYncc+6gc\ncTqkPfS4IF59v2HMXGonyVC6eZcM7pwLTvWIFfYLlhr838F9uVZLnO1MKVoUPeBl\np/n3bUjlMSO7cuLOpdXWfK8bea9HU1X7Zl5KN4BVnsmJBnbvb34Dkf0td3HRRKVZ\n4GFDMzVLriGYPLas1QURwtpUjQ==\n-----END PRIVATE KEY-----\n"}

{"cmd": "cleanup", "type": "tls-sni-01", "status": "pending", "token": "kPGFQWIJr1HM07UgRLLp1FCeVrx3N60CwP_QV9c5hHs", "domain": "stoke2.pki.enigmabridge.com", "validated": null, "error": null}
{"cmd": "cleanup", "type": "tls-sni-01", "status": "pending", "token": "dbowNJLZiuxPO83RQv1egT12cgnFP_VPvbGmMKWWfQg", "domain": "st2.pki.enigmabridge.com", "validated": null, "error": null}
{"cmd": "report", "messages": [{"priority": 1, "on_crash": true, "lines": ["The following errors were reported by the server:", "", "Domain: stoke2.pki.enigmabridge.com", "Type:   unknownHost", "Detail: No valid IP addresses found for stoke2.pki.enigmabridge.com", "", "Domain: st2.pki.enigmabridge.com", "Type:   unknownHost", "Detail: No valid IP addresses found for st2.pki.enigmabridge.com", "", "To fix these errors, please make sure that your domain name was entered correctly and the DNS A record(s) for that domain contain(s) the right IP address."]}]}
```

### Example - Handler, DNS

In this repository there is a default [handler-example.sh] which can be used as a handler.

```bash
certbot --staging \
        --text --agree-tos --email you@example.com \
        --expand --renew-by-default \
        -a certbot-external-auth:out \
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
        -a certbot-external-auth:out \
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
        -a certbot-external-auth:out \
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

