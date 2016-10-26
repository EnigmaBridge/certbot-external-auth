## External authenticator for Certbot

This plugin helps with domain validation process by calling external 
program or by printing JSON for the

The plugin is designed mainly to automate DNS validation.

## Installation - pip

```bash
pip install certbot
pip install certbot-external-auth
```

## Manual Installation

To install, first install certbot (either on the root or in a virtualenv),
then:

```bash
python setup.py install
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
{"cmd": "validate", "type": "dns", "validation": "rYIS1e4mFCsJXN43LMq_fnFptIfoLC4RhbJABfT2_78", "domain": "_acme-challenge.stoke2.pki.enigmabridge.com", "key-auth": "3R11yWg6DT6NECoroLK3J4p5ge770rBLym5ihSVEePU.SVZszZ-QbTXxaiRH9L6Z3RhEFnoRY-gghCmujuGnY5s"}

{"cmd": "validate", "type": "dns", "validation": "mZ3WMFp8thovIMqfMFdvm3Lzfv90hNAl3633Bm2-PrQ", "domain": "_acme-challenge.st2.pki.enigmabridge.com", "key-auth": "k5zcovdyhgPgZsmiQE2QMBJHFKMT5qRjVCCSawmycYY.SVZszZ-QbTXxaiRH9L6Z3RhEFnoRY-gghCmujuGnY5s"}

{"cmd": "report", "messages": [{"priority": 1, "on_crash": true, "lines": ["The following errors were reported by the server:", "", "Domain: st2.pki.enigmabridge.com", "Type:   connection", "Detail: DNS problem: NXDOMAIN looking up TXT for _acme-challenge.st2.pki.enigmabridge.com", "", "Domain: stoke2.pki.enigmabridge.com", "Type:   connection", "Detail: DNS problem: NXDOMAIN looking up TXT for _acme-challenge.stoke2.pki.enigmabridge.com", "", "To fix these errors, please make sure that your domain name was entered correctly and the DNS A record(s) for that domain contain(s) the right IP address. Additionally, please check that your computer has a publicly routable IP address and that no firewalls are preventing the server from communicating with the client. If you're using the webroot plugin, you should also verify that you are serving files from the webroot path you provided."]}]}
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
{"cmd": "validate", "type": "http", "validation": "oaWcu_EUAH9ZUQVyM2lHtNUK27DI0fvuckCEtGMKwcQ.SVZszZ-QbTXxaiRH9L6Z3RhEFnoRY-gghCmujuGnY5s", "uri": "http://stoke2.pki.enigmabridge.com/.well-known/acme-challenge/oaWcu_EUAH9ZUQVyM2lHtNUK27DI0fvuckCEtGMKwcQ", "command": "mkdir -p /tmp/certbot/public_html/.well-known/acme-challenge\ncd /tmp/certbot/public_html\nprintf \"%s\" oaWcu_EUAH9ZUQVyM2lHtNUK27DI0fvuckCEtGMKwcQ.SVZszZ-QbTXxaiRH9L6Z3RhEFnoRY-gghCmujuGnY5s > .well-known/acme-challenge/oaWcu_EUAH9ZUQVyM2lHtNUK27DI0fvuckCEtGMKwcQ\n# run only once per server:\n$(command -v python2 || command -v python2.7 || command -v python2.6) -c \\\n\"import BaseHTTPServer, SimpleHTTPServer; \\\ns = BaseHTTPServer.HTTPServer(('', 80), SimpleHTTPServer.SimpleHTTPRequestHandler); \\\ns.serve_forever()\" ", "key-auth": "oaWcu_EUAH9ZUQVyM2lHtNUK27DI0fvuckCEtGMKwcQ.SVZszZ-QbTXxaiRH9L6Z3RhEFnoRY-gghCmujuGnY5s"}

{"cmd": "validate", "type": "http", "validation": "p0yw7Xy5koErnMUjFTZFGCXD0wc778Q9QRj62-s6R5Q.SVZszZ-QbTXxaiRH9L6Z3RhEFnoRY-gghCmujuGnY5s", "uri": "http://st2.pki.enigmabridge.com/.well-known/acme-challenge/p0yw7Xy5koErnMUjFTZFGCXD0wc778Q9QRj62-s6R5Q", "command": "mkdir -p /tmp/certbot/public_html/.well-known/acme-challenge\ncd /tmp/certbot/public_html\nprintf \"%s\" p0yw7Xy5koErnMUjFTZFGCXD0wc778Q9QRj62-s6R5Q.SVZszZ-QbTXxaiRH9L6Z3RhEFnoRY-gghCmujuGnY5s > .well-known/acme-challenge/p0yw7Xy5koErnMUjFTZFGCXD0wc778Q9QRj62-s6R5Q\n# run only once per server:\n$(command -v python2 || command -v python2.7 || command -v python2.6) -c \\\n\"import BaseHTTPServer, SimpleHTTPServer; \\\ns = BaseHTTPServer.HTTPServer(('', 80), SimpleHTTPServer.SimpleHTTPRequestHandler); \\\ns.serve_forever()\" ", "key-auth": "p0yw7Xy5koErnMUjFTZFGCXD0wc778Q9QRj62-s6R5Q.SVZszZ-QbTXxaiRH9L6Z3RhEFnoRY-gghCmujuGnY5s"}

{"cmd": "report", "messages": [{"priority": 1, "on_crash": true, "lines": ["The following errors were reported by the server:", "", "Domain: stoke2.pki.enigmabridge.com", "Type:   unknownHost", "Detail: No valid IP addresses found for stoke2.pki.enigmabridge.com", "", "Domain: st2.pki.enigmabridge.com", "Type:   unknownHost", "Detail: No valid IP addresses found for st2.pki.enigmabridge.com", "", "To fix these errors, please make sure that your domain name was entered correctly and the DNS A record(s) for that domain contain(s) the right IP address."]}]}
```

## Future work

* Communicate challenges via named pipes
* Communicate challenges via sockets
* Call an external script with the challenges in parameter


## About

Loosely based on the Let's Encrypt nginx plugin, [certbot-external] and
`manual.py` plugin.

Once ticket [2782] is resolved this won't be needed. 

[certbot-external]: https://github.com/marcan/certbot-external
[2782]: https://github.com/certbot/certbot/issues/2782
