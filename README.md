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
to send a new line to continue with the process.

## Example 

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
