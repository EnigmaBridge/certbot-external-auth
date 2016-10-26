## External authenticator for Certbot

This plugin helps with domain validation process by calling external 
program (TODO) or by printing JSON challenge to stdout for invoker to solve.

The plugin is designed mainly to automate the DNS validation, but supports also
HTTP and TLS-SNI.

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

This plugin only supports authentication, not installation.

Currently it produces one-line JSON with challenge to process by the script 
on the stdout. After the challenge is processed, external process is supposed
to send a new line `\n` character to the stdin to continue with the process.

Reporter was substituted to produce JSON logs so stdout is JSON only.

## Example 

In the examples below I did not solve the challenges so the reporter prints 
out an error. The error is indicated also by returning non-zero return code.

Run the certbot with the following command:

```bash
certbot --text --agree-tos --email you@example.com \
        --expand --renew-by-default \
        -a certbot-external-auth:out \
        --preferred-challenges dns \
        --certbot-external-auth:out-public-ip-logging-ok \
        -d "stoke2.pki.enigmabridge.com" \
        -d "st2.pki.enigmabridge.com" \
        certonly 2>/dev/null
```

Stderr contains string log / report, not in JSON format.

Stdout:

```json
{"cmd": "validate", "type": "dns-01", "validation": "rwfX5jrRQXOiXLOgPL0RM4QtVx0oEIK_pA4Y4eSjqOI", "domain": "_acme-challenge.stoke2.pki.enigmabridge.com", "key-auth": "AfWfkObOD6vyCKXA1tE0Y2Eub9kvltKB7DH5zGxSG04.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0"}

{"cmd": "validate", "type": "dns-01", "validation": "BTDDPMZp8JSLTMfWHguVmdRv-BXVfEBWhfdDyQPCv_I", "domain": "_acme-challenge.st2.pki.enigmabridge.com", "key-auth": "he2pUhw6DWhhnqkxIaLrUAJPpswA_6OSXUUInw0uDkY.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0"}

{"cmd": "cleanup", "type": "dns-01", "status": "pending", "token": "AfWfkObOD6vyCKXA1tE0Y2Eub9kvltKB7DH5zGxSG04", "domain": "stoke2.pki.enigmabridge.com", "validated": null, "error": null}
{"cmd": "cleanup", "type": "dns-01", "status": "pending", "token": "he2pUhw6DWhhnqkxIaLrUAJPpswA_6OSXUUInw0uDkY", "domain": "st2.pki.enigmabridge.com", "validated": null, "error": null}
{"cmd": "report", "messages": [{"priority": 1, "on_crash": true, "lines": ["The following errors were reported by the server:", "", "Domain: stoke2.pki.enigmabridge.com", "Type:   connection", "Detail: DNS problem: NXDOMAIN looking up TXT for _acme-challenge.stoke2.pki.enigmabridge.com", "", "Domain: st2.pki.enigmabridge.com", "Type:   connection", "Detail: DNS problem: NXDOMAIN looking up TXT for _acme-challenge.st2.pki.enigmabridge.com", "", "To fix these errors, please make sure that your domain name was entered correctly and the DNS A record(s) for that domain contain(s) the right IP address. Additionally, please check that your computer has a publicly routable IP address and that no firewalls are preventing the server from communicating with the client. If you're using the webroot plugin, you should also verify that you are serving files from the webroot path you provided."]}]}
```

After `{"cmd": "validate"}` message the client waits on `\n` on the standard input to continue with the validation.

## Example - HTTP

Run the certbot with the following command (just `preferred-challenges` changed):

```bash
certbot --text --agree-tos --email you@example.com \
        --expand --renew-by-default \
        -a certbot-external-auth:out \
        --preferred-challenges http \
        --certbot-external-auth:out-public-ip-logging-ok \
        -d "stoke2.pki.enigmabridge.com" \
        -d "st2.pki.enigmabridge.com" \
        certonly 2>/dev/null
```

Stdout:

```json
{"cmd": "validate", "type": "http-01", "validation": "M7eaUb9BYXH8kb1IuTvjxcj5UmhZjbVrHfRHdhjatS4.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "uri": "http://stoke2.pki.enigmabridge.com/.well-known/acme-challenge/M7eaUb9BYXH8kb1IuTvjxcj5UmhZjbVrHfRHdhjatS4", "command": "mkdir -p /tmp/certbot/public_html/.well-known/acme-challenge\ncd /tmp/certbot/public_html\nprintf \"%s\" M7eaUb9BYXH8kb1IuTvjxcj5UmhZjbVrHfRHdhjatS4.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0 > .well-known/acme-challenge/M7eaUb9BYXH8kb1IuTvjxcj5UmhZjbVrHfRHdhjatS4\n# run only once per server:\n$(command -v python2 || command -v python2.7 || command -v python2.6) -c \\\n\"import BaseHTTPServer, SimpleHTTPServer; \\\ns = BaseHTTPServer.HTTPServer(('', 80), SimpleHTTPServer.SimpleHTTPRequestHandler); \\\ns.serve_forever()\" ", "key-auth": "M7eaUb9BYXH8kb1IuTvjxcj5UmhZjbVrHfRHdhjatS4.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0"}

{"cmd": "validate", "type": "http-01", "validation": "E2MeY_tgp6yPw9K8ivMb_TCMTSrOkF0zbjxIInu0yXQ.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "uri": "http://st2.pki.enigmabridge.com/.well-known/acme-challenge/E2MeY_tgp6yPw9K8ivMb_TCMTSrOkF0zbjxIInu0yXQ", "command": "mkdir -p /tmp/certbot/public_html/.well-known/acme-challenge\ncd /tmp/certbot/public_html\nprintf \"%s\" E2MeY_tgp6yPw9K8ivMb_TCMTSrOkF0zbjxIInu0yXQ.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0 > .well-known/acme-challenge/E2MeY_tgp6yPw9K8ivMb_TCMTSrOkF0zbjxIInu0yXQ\n# run only once per server:\n$(command -v python2 || command -v python2.7 || command -v python2.6) -c \\\n\"import BaseHTTPServer, SimpleHTTPServer; \\\ns = BaseHTTPServer.HTTPServer(('', 80), SimpleHTTPServer.SimpleHTTPRequestHandler); \\\ns.serve_forever()\" ", "key-auth": "E2MeY_tgp6yPw9K8ivMb_TCMTSrOkF0zbjxIInu0yXQ.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0"}

{"cmd": "cleanup", "type": "http-01", "status": "pending", "token": "M7eaUb9BYXH8kb1IuTvjxcj5UmhZjbVrHfRHdhjatS4", "domain": "stoke2.pki.enigmabridge.com", "validated": null, "error": null}
{"cmd": "cleanup", "type": "http-01", "status": "pending", "token": "E2MeY_tgp6yPw9K8ivMb_TCMTSrOkF0zbjxIInu0yXQ", "domain": "st2.pki.enigmabridge.com", "validated": null, "error": null}
{"cmd": "report", "messages": [{"priority": 1, "on_crash": true, "lines": ["The following errors were reported by the server:", "", "Domain: st2.pki.enigmabridge.com", "Type:   unknownHost", "Detail: No valid IP addresses found for st2.pki.enigmabridge.com", "", "Domain: stoke2.pki.enigmabridge.com", "Type:   unknownHost", "Detail: No valid IP addresses found for stoke2.pki.enigmabridge.com", "", "To fix these errors, please make sure that your domain name was entered correctly and the DNS A record(s) for that domain contain(s) the right IP address."]}]}
```

## Example - TLS-SNI

Run the certbot with the following command (just `preferred-challenges` changed):

```bash
certbot --text --agree-tos --email you@example.com \
        --expand --renew-by-default \
        -a certbot-external-auth:out \
        --preferred-challenges tls-sni \
        --certbot-external-auth:out-public-ip-logging-ok \
        -d "stoke2.pki.enigmabridge.com" \
        -d "st2.pki.enigmabridge.com" \
        certonly 2>/dev/null
```

Stdout:

```json
{"cmd": "validate", "type": "tls-sni-01", "domain": "stoke2.pki.enigmabridge.com", "z_domain": "271c1cc2d19ad0d19bc70e0de6b54478.26590d8a282d0ea1744a6e8acab92042.acme.invalid", "cert_path": "/var/lib/letsencrypt/kPGFQWIJr1HM07UgRLLp1FCeVrx3N60CwP_QV9c5hHs.crt", "key_path": "/var/lib/letsencrypt/kPGFQWIJr1HM07UgRLLp1FCeVrx3N60CwP_QV9c5hHs.pem", "port": "443", "key-auth": "kPGFQWIJr1HM07UgRLLp1FCeVrx3N60CwP_QV9c5hHs.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "cert_pem": "-----BEGIN CERTIFICATE-----\nMIIDIjCCAgqgAwIBAgIQDdQModuq16h2S98RWViUNTANBgkqhkiG9w0BAQsFADAQ\nMQ4wDAYDVQQDDAVkdW1teTAeFw0xNjEwMjYyMjI2MjNaFw0xNjExMDIyMjI2MjNa\nMBAxDjAMBgNVBAMMBWR1bW15MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKC\nAQEAk/Cd5YZQ06wlWD+wyzDK234/ZiTQeseJE1GfoPhWO3K3Vem8AVzvNxud85Ot\npurD1/GA+8BmhSYxSk+aI5mAE94d10uhFzrMMqFOCdkesq5f3PLcItQBz3xQmKHW\n/HEsQVRYwgTAOw+uARjDc12suBdVEHzn5OMrC7Om+gvn5Ibb9u23sDzzu2F2YVCw\nUO//izMNbjS24gHaKkvOa1Q3JHiNQSg0Cn9xWBgo0yNHQtWosTgUSBL6HmWlOiM/\nFqP+bZZLWg3h6dPWCIEsEkxcUOh3eKrMBSp8WEHVQpmRg+uBek+toZ7rWM+4jnZN\nGbqY56mLjZbmB57pphmpBix5WQIDAQABo3gwdjASBgNVHRMBAf8ECDAGAQH/AgEA\nMGAGA1UdEQRZMFeCBWR1bW15gk4yNzFjMWNjMmQxOWFkMGQxOWJjNzBlMGRlNmI1\nNDQ3OC4yNjU5MGQ4YTI4MmQwZWExNzQ0YTZlOGFjYWI5MjA0Mi5hY21lLmludmFs\naWQwDQYJKoZIhvcNAQELBQADggEBAGJqiKVuOOETaHrTgCmD/0B5A9EKlYQNiznw\nouG6DxQIG/egtpELSXiEmfT1D+VTtyx5vcm9HKCwXyckjED0WOOlFANvRp5XeKBe\nOfONcozSRK0+GUKan1N+UDGuMSUIYdgFDUo1uW/Qg39DeLOrhwYCxdiwKL/ioA+a\nh1FHr+oTniZ80LWtwWNcp++vZQUjqkcBt6pKTsCQ+uQ73dtgswIlHVUNiSQcjcD9\nMqpVjzWm2E2WwJkrdPrCvaA5kjGZj77ywLkBBMtAZju3MZGX3qoL/2AeQExcAawB\n3h80nLh30d1Lj95Gz92lvvEbstqqsRPK6ck3XmaDkCmAc36XOoU=\n-----END CERTIFICATE-----\n", "key_pem": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCT8J3lhlDTrCVY\nP7DLMMrbfj9mJNB6x4kTUZ+g+FY7crdV6bwBXO83G53zk62m6sPX8YD7wGaFJjFK\nT5ojmYAT3h3XS6EXOswyoU4J2R6yrl/c8twi1AHPfFCYodb8cSxBVFjCBMA7D64B\nGMNzXay4F1UQfOfk4ysLs6b6C+fkhtv27bewPPO7YXZhULBQ7/+LMw1uNLbiAdoq\nS85rVDckeI1BKDQKf3FYGCjTI0dC1aixOBRIEvoeZaU6Iz8Wo/5tlktaDeHp09YI\ngSwSTFxQ6Hd4qswFKnxYQdVCmZGD64F6T62hnutYz7iOdk0ZupjnqYuNluYHnumm\nGakGLHlZAgMBAAECggEAI9+xKjtL1khkNeYb5OnMBzWyAf7jXyKLptegMdSGdJv4\nwSiQonP6vg5AWxRwg41iODcj4+hf8+GzCiYLZp6OZEL0UYTRZ2Smp5Bd8B1qSEHo\nlRd/MiLe3YVztc9o5oY7CQx/CW1FgAzpUPLEUnFgtLNTuU/Qm7xKb+f8kZ3ZeZyr\n0DQwgzOo0NjmAnUDK/LDeCxNlNiJOQQ5p4lg3HhcE7XTtfDBmPY3G+9fB/3gbIVH\nrVT0acH/uvLlCZTYX6Ts0ARnqi+LKLb+r6zG9qTYOVWvgmHOYMpPxDjHPfocp0cf\njFrI3ZGSdaqzzN9huaxsjn+LEWHn+bmMS6t3rv/0AQKBgQDDaOjsD6ETK9NIpTty\n6kVs+4hH1ds0jGP8iQl8G0ESpaiLg6S7cR2CobbxLOvNxV08/Tv4p7WgpqFB2pe1\nRZ7bFkYiirMI6uFLp78azHgAeJgE0lUmZGUwPqxl+22Oz5SFRWopIv7gVBiPmkeS\nCzhqaRuZ4EK3BLgjvrna8HhBeQKBgQDBz62J+l0uhNTh1znQChtHUX20HV+pW2R5\nwnVpesaFRoe4Wka3ZUH4uskq5sQQnakQ30Zfj8QZZ3y8m6HuIkBpLGE9Yy5uKJol\nPI3lqN5+SFX5xMqFC+o1osHGSQTKsCe1dymbConggO1j+6uQUb508GjN5piG+JE8\nQExbKFTe4QKBgQCcx34hb4S3YfEZluA0mbtr7f9wSyedaIoMIlKGzUMPV/P7Q3qW\nnPGlTmP96iGirZfaB/7myH/Tzf0RXfVcDeifNKa+rfNo0zJBRevw713UWuz06WBB\n9kitRYuCIxDKhMdPidrb+GTvzOkLxidoCDKSRZRMh/5e4p1uqGZrP4XsWQKBgG8P\nhh+CI7GLlr4P6mYn1Hfq38C98FqJL6uCXmviWi53O0DOIqXnVYWl66806/elkQNF\nHvuV08bHAbjG6mUepZBfSR23XxzrEWHzMFEBkvYEl5f4SCEzsbOon6fzodZQWYDo\nVyQsRtQqrV5VEnwyC5TRSw1qbc8yU2+WXOsD0pahAoGAfbpouBLbqO+y661K/pFu\nuEviE27r+9mRascUt6OpGCzwDsFu/aaadVmPxaiyqM0758pt8SixvvWvBj3gKcfY\nJdrMGxE73JG0PdlcatX34tzQjtFPaA9NQwVtrj28HQaleGgCOwn2tW1wPndUZFGK\nGUcZuhu0c0WkD83bnYKw3v8=\n-----END PRIVATE KEY-----\n"}

{"cmd": "validate", "type": "tls-sni-01", "domain": "st2.pki.enigmabridge.com", "z_domain": "2b6de2ffbeafcf72fa2500fcb94d8f01.c063b3eb7cccc4101b9bebae3f93d233.acme.invalid", "cert_path": "/var/lib/letsencrypt/dbowNJLZiuxPO83RQv1egT12cgnFP_VPvbGmMKWWfQg.crt", "key_path": "/var/lib/letsencrypt/dbowNJLZiuxPO83RQv1egT12cgnFP_VPvbGmMKWWfQg.pem", "port": "443", "key-auth": "dbowNJLZiuxPO83RQv1egT12cgnFP_VPvbGmMKWWfQg.tRQM98JsABZRm5-NiotcgD212RAUPPbyeDP30Ob_7-0", "cert_pem": "-----BEGIN CERTIFICATE-----\nMIIDIzCCAgugAwIBAgIRAMIQsaVSIBl+KZTZrcHJRoUwDQYJKoZIhvcNAQELBQAw\nEDEOMAwGA1UEAwwFZHVtbXkwHhcNMTYxMDI2MjIyNjI0WhcNMTYxMTAyMjIyNjI0\nWjAQMQ4wDAYDVQQDDAVkdW1teTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoC\nggEBAKoXB5o1mY/BcUUEeYqvNBFl9CRUsgU8l5IYUvm4kyXPS7ieu9u9LJj3fHQD\no/Q2Wlwq8nQ4ZbmHuE11MdQvjxGarWk+zeJRZ7/JIVFdGkPCbYs1Q8UEbfHzUKU2\nwH0alT/REeJbiazRdRpzpLO9RmCT7WvH2Q911/N2WULKR1dkhmEUE0lsINhbt5ZM\na9UjzinW0arZKzIl6SZcut/30uhuDYkN/Y3KUEBBq530q2e2YdZafUGEyinjH8Df\nr4n+jmIG+Dxs+ymFCzsnAICIJwYx4iVr6HYenKcXvG9k6dDazpK5PbuzMJrv4MMP\nE/0hfqlhOjmvRp8TopIDt+eYZucCAwEAAaN4MHYwEgYDVR0TAQH/BAgwBgEB/wIB\nADBgBgNVHREEWTBXggVkdW1teYJOMmI2ZGUyZmZiZWFmY2Y3MmZhMjUwMGZjYjk0\nZDhmMDEuYzA2M2IzZWI3Y2NjYzQxMDFiOWJlYmFlM2Y5M2QyMzMuYWNtZS5pbnZh\nbGlkMA0GCSqGSIb3DQEBCwUAA4IBAQCUz5lKTe9P25XlB0Of50LWIRUxL/4+u7UH\n4EaAadkKofmKzSAQxLG9ORkWO8T0OrW5rqvOao2WYWnoEdtgu/XKXq3NJxp9RRK7\nxsF3TYhk04GNsH3ycbwoUOkD1rsAt5YW9ls+IDECTKKVc1FfVlMR0JUszpTzzvBW\nnUuCzlXylcgNVzzRSuckMZMsfIwkyT9v1XjviYK0auUv/eEryLqBXn9Qke6YyVWd\nDDOg0oLFo9hPLy5bVOr7XLa0Yd83r5GYg0IwtuE4emL56QkX7U7Uz+zTRo/tKQIR\nhKJIxzR7AxOBuv8OP5G8iPxzCEGTNVAuLKYoUikLtY61vLhfoBN8\n-----END CERTIFICATE-----\n", "key_pem": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQCqFweaNZmPwXFF\nBHmKrzQRZfQkVLIFPJeSGFL5uJMlz0u4nrvbvSyY93x0A6P0NlpcKvJ0OGW5h7hN\ndTHUL48Rmq1pPs3iUWe/ySFRXRpDwm2LNUPFBG3x81ClNsB9GpU/0RHiW4ms0XUa\nc6SzvUZgk+1rx9kPddfzdllCykdXZIZhFBNJbCDYW7eWTGvVI84p1tGq2SsyJekm\nXLrf99Lobg2JDf2NylBAQaud9KtntmHWWn1BhMop4x/A36+J/o5iBvg8bPsphQs7\nJwCAiCcGMeIla+h2HpynF7xvZOnQ2s6SuT27szCa7+DDDxP9IX6pYTo5r0afE6KS\nA7fnmGbnAgMBAAECggEBAJs0Anrjd+kmEY5xw9oZfwB1MK7KHdsLbB8iVOyLULIK\nksS3CyI6X2yBP624+K1Jv3AkvDHymFgQEMuVKc+9SeY9ZwkHBuUBdRMam21b8DBu\nRHjnNJydKxnA9RCcgk5lqFSgGJqc/maUhi+J4HsmNgbAVL+pj1Y9KL1+e3qniyuh\nEFtYcBnS0mYla8Pe295ImBnQsMYXnMVbESq1jQ5swmrAWhwtri5+/jRiDEBC5aJL\nwiYVwWqYWrpOYK1gy4aqQlvB+9QDkgTY1v7xU8OT0GLzmGFz0mRqQ5w+Dcwgg5yB\nqzDe/GC+hPQn6Sw0QV9AVUSIJLisqWMMLQ175DW4RWECgYEA3IU89mT8HP5eaoS0\ncJCr40BZWbKQ7AJyMgz+TGkfPYq7DMiYOO3o1cQ67DQgdtSLC62IeaQmMYZ7M57B\n9VTr7/VApPqsM/LvyZc8Ctr1/GRhwyxYF5WN158aWY6kqJHacdDEIgLIW8V7U+pY\n4KVx0Jx3DnLFyDKqHFte6FQBtvcCgYEAxXSrBJ5j3XCAS7+8kSCIahhFtTVj0PD8\n7+uDceJ/awJKeS7ffJxvFiKW5ho/PGqmMyNsL/RU/RTpofbLyJFRVnNdo3EVuSYW\n5y/Caq+etamo7aGqYhd5LX2e7t2f585Pi/pBHS3R0dAa0mSZmP5n4h6C+Jq0y89X\nMFueLCtEI5ECgYEAnu/9D02blD4VyMoazyLGcIUZoRedci0VJ1PMGUCO/qk1xbHy\nXN3EOgYzvbiYSW1JRkJtodaYnItj0sGy4+KwJoPqcr4lTU/kWbSB1wUX1DB5cdVN\nLLpiwCzxLeksbj6pZezk3+qHg/VivQmjw04bKRMMkEJSoMc7ajLExch+b+MCgYBR\nsQUYMheLBAJwVHFFcbo+erBMWjxjs3BSKpQFR/oDYb1CCbx4p5fmBoV7yZwj+NOu\nEJev91w6IK7QTXTeFBEcvToeZqjgIvwSxdWfoez9p6W2Os5tKtz9jx10IckIdHjA\nptbNpalLLtgJ94j8nTSJfqodBJSMRcoCvcTg7T2RoQKBgQCo4hIi2PshYncc+6gc\ncTqkPfS4IF59v2HMXGonyVC6eZcM7pwLTvWIFfYLlhr838F9uVZLnO1MKVoUPeBl\np/n3bUjlMSO7cuLOpdXWfK8bea9HU1X7Zl5KN4BVnsmJBnbvb34Dkf0td3HRRKVZ\n4GFDMzVLriGYPLas1QURwtpUjQ==\n-----END PRIVATE KEY-----\n"}

{"cmd": "cleanup", "type": "tls-sni-01", "status": "pending", "token": "kPGFQWIJr1HM07UgRLLp1FCeVrx3N60CwP_QV9c5hHs", "domain": "stoke2.pki.enigmabridge.com", "validated": null, "error": null}
{"cmd": "cleanup", "type": "tls-sni-01", "status": "pending", "token": "dbowNJLZiuxPO83RQv1egT12cgnFP_VPvbGmMKWWfQg", "domain": "st2.pki.enigmabridge.com", "validated": null, "error": null}
{"cmd": "report", "messages": [{"priority": 1, "on_crash": true, "lines": ["The following errors were reported by the server:", "", "Domain: stoke2.pki.enigmabridge.com", "Type:   unknownHost", "Detail: No valid IP addresses found for stoke2.pki.enigmabridge.com", "", "Domain: st2.pki.enigmabridge.com", "Type:   unknownHost", "Detail: No valid IP addresses found for st2.pki.enigmabridge.com", "", "To fix these errors, please make sure that your domain name was entered correctly and the DNS A record(s) for that domain contain(s) the right IP address."]}]}
```

## Future work

* Communicate challenges via named pipes
* Communicate challenges via sockets
* Call an external script with the challenges in parameter

## Manual Installation

To install, first install certbot (either on the root or in a virtualenv),
then:

```bash
python setup.py install
```

## About

Loosely based on the Let's Encrypt nginx plugin, [certbot-external] and
`manual.py` plugin.

Once ticket [2782] is resolved this won't be needed. 

[certbot-external]: https://github.com/marcan/certbot-external
[2782]: https://github.com/certbot/certbot/issues/2782
