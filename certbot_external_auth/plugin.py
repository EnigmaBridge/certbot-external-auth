"""Manual plugin on stereoids."""
import os
import logging
import pipes
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
import json
import collections
from collections import OrderedDict
import atexit
from six.moves import queue  # pylint: disable=import-error

import six
import zope.component
import zope.interface

from acme import challenges
from acme import errors as acme_errors

from certbot import errors
from certbot import interfaces
from certbot import util
from certbot.plugins import common


logger = logging.getLogger(__name__)


INITIAL_PID = os.getpid()


@zope.interface.implementer(interfaces.IAuthenticator)
@zope.interface.provider(interfaces.IPluginFactory)
@zope.interface.implementer(interfaces.IReporter)
class AuthenticatorOut(common.Plugin):
    """Manual Authenticator.

    This plugin requires user's manual intervention in setting up a HTTP
    server for solving http-01 challenges and thus does not need to be
    run as a privileged process. Alternatively shows instructions on how
    to use Python's built-in HTTP server.

    .. todo:: Support for `~.challenges.TLSSNI01`.

    """
    hidden = False

    description = "Manual challenge solver"

    MESSAGE_TEMPLATE = {
        "dns-01": """\
Please deploy a DNS TXT record under the name
{domain} with the following value:

{validation}

Once this is deployed,
""",
        "http-01": """\
Make sure your web server displays the following content at
{uri} before continuing:

{validation}

If you don't have HTTP server configured, you can run the following
command on the target server (as root):

{command}
"""}

    # a disclaimer about your current IP being transmitted to Let's Encrypt's servers.
    IP_DISCLAIMER = """\
NOTE: The IP of this machine will be publicly logged as having requested this certificate. \
If you're running certbot in manual mode on a machine that is not your server, \
please ensure you're okay with that.

Are you OK with your IP being logged?
"""

    # "cd /tmp/certbot" makes sure user doesn't serve /root,
    # separate "public_html" ensures that cert.pem/key.pem are not
    # served and makes it more obvious that Python command will serve
    # anything recursively under the cwd

    CMD_TEMPLATE = """\
mkdir -p {root}/public_html/{achall.URI_ROOT_PATH}
cd {root}/public_html
printf "%s" {validation} > {achall.URI_ROOT_PATH}/{encoded_token}
# run only once per server:
$(command -v python2 || command -v python2.7 || command -v python2.6) -c \\
"import BaseHTTPServer, SimpleHTTPServer; \\
s = BaseHTTPServer.HTTPServer(('', {port}), SimpleHTTPServer.SimpleHTTPRequestHandler); \\
s.serve_forever()" """
    """Command template."""

    # Reporter stuff
    HIGH_PRIORITY = 0
    """High priority constant. See `add_message`."""
    MEDIUM_PRIORITY = 1
    """Medium priority constant. See `add_message`."""
    LOW_PRIORITY = 2
    """Low priority constant. See `add_message`."""

    _msg_type = collections.namedtuple('ReporterMsg', 'priority text on_crash')

    def __init__(self, *args, **kwargs):
        super(AuthenticatorOut, self).__init__(*args, **kwargs)
        self._root = (tempfile.mkdtemp() if self.conf("test-mode")
                      else "/tmp/certbot")
        self._httpd = None

        # Reporter
        self.orig_reporter = None
        self.messages = queue.PriorityQueue()

    @classmethod
    def add_parser_arguments(cls, add):
        add("test-mode", action="store_true",
            help="Test mode. Executes the manual command in subprocess.")
        add("public-ip-logging-ok", action="store_true",
            help="Automatically allows public IP logging.")
        add("text-mode", action="store_true",
            help="Original text mode, by default turned off, produces JSON challenges")

    def prepare(self):  # pylint: disable=missing-docstring,no-self-use
        # Re-register reporter
        self.orig_reporter = zope.component.getUtility(interfaces.IReporter)
        zope.component.provideUtility(self, provides=interfaces.IReporter)
        atexit.register(self.atexit_print_messages)

        # Non-interactive not yet supported
        if self.config.noninteractive_mode and not self.conf("test-mode"):
            raise errors.PluginError("Running manual mode non-interactively is not supported (yet)")

    def more_info(self):  # pylint: disable=missing-docstring,no-self-use
        return ("This plugin requires user's manual intervention in setting "
                "up challenges to prove control of a domain and does not need "
                "to be run as a privileged process. When solving "
                "http-01 challenges, the user is responsible for setting up "
                "an HTTP server. Alternatively, instructions are shown on how "
                "to use Python's built-in HTTP server. The user is "
                "responsible for configuration of a domain's DNS when solving "
                "dns-01 challenges. The type of challenges used can be "
                "controlled through the --preferred-challenges flag.")

    def get_chall_pref(self, domain):
        # pylint: disable=missing-docstring,no-self-use,unused-argument
        return [challenges.DNS01, challenges.HTTP01]

    def perform(self, achalls):
        # pylint: disable=missing-docstring
        self._get_ip_logging_permission()
        mapping = {"http-01": self._perform_http01_challenge,
                   "dns-01": self._perform_dns01_challenge}
        responses = []
        # TODO: group achalls by the same socket.gethostbyname(_ex)
        # and prompt only once per server (one "echo -n" per domain)
        for achall in achalls:
            responses.append(mapping[achall.typ](achall))
        return responses

    def add_message(self, msg, priority, on_crash=True):
        """Adds msg to the list of messages to be printed.

        :param str msg: Message to be displayed to the user.

        :param int priority: One of HIGH_PRIORITY, MEDIUM_PRIORITY, or
            LOW_PRIORITY.

        :param bool on_crash: Whether or not the message should be printed if
            the program exits abnormally.

        """
        if self._is_text_mode():
            self.orig_reporter.add_message(msg, priority, on_crash=on_crash)
            return

        assert self.HIGH_PRIORITY <= priority <= self.LOW_PRIORITY
        self.messages.put(self._msg_type(priority, msg, on_crash))
        logger.debug("Reporting to user: %s", msg)
        pass

    def print_messages(self):
        """Prints messages to the user and clears the message queue."""
        if self._is_text_mode():
            self.orig_reporter.print_messages()
            return
        no_exception = sys.exc_info()[0] is None
        print no_exception

        messages = []
        while not self.messages.empty():
            msg = self.messages.get()
            if self.config.quiet:
                # In --quiet mode, we only print high priority messages that
                # are flagged for crash cases
                if not (msg.priority == self.HIGH_PRIORITY and msg.on_crash):
                    continue
            if no_exception or msg.on_crash:
                cur_message = OrderedDict()
                cur_message['priority'] = msg.priority
                cur_message['on_crash'] = msg.on_crash
                cur_message['lines'] = msg.text.splitlines()
                messages.append(cur_message)

        data = OrderedDict()
        data['cmd'] = 'report'
        data['messages'] = messages
        self._json_out(data, True)
        pass

    def atexit_print_messages(self, pid=None):
        """Function to be registered with atexit to print messages.

        :param int pid: Process ID

        """
        if pid is None:
            pid = INITIAL_PID
        # This ensures that messages are only printed from the process that
        # created the Reporter.
        if pid == os.getpid():
            self.print_messages()

    @classmethod
    def _test_mode_busy_wait(cls, port):
        while True:
            time.sleep(1)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.connect(("localhost", port))
            except socket.error:  # pragma: no cover
                pass
            else:
                break
            finally:
                sock.close()

    def cleanup(self, achalls):
        # pylint: disable=missing-docstring
        for achall in achalls:
            if isinstance(achall.chall, challenges.HTTP01):
                self._cleanup_http01_challenge(achall)

    def _perform_http01_challenge(self, achall):
        # raise errors.PluginError("Not implemented yet")

        # same path for each challenge response would be easier for
        # users, but will not work if multiple domains point at the
        # same server: default command doesn't support virtual hosts
        response, validation = achall.response_and_validation()
        port = (response.port if self.config.http01_port is None
                else int(self.config.http01_port))
        command = self.CMD_TEMPLATE.format(
            root=self._root, achall=achall, response=response,
            # TODO(kuba): pipes still necessary?
            validation=pipes.quote(validation),
            encoded_token=achall.chall.encode("token"),
            port=port)
        if self.conf("test-mode"):
            logger.debug("Test mode. Executing the manual command: %s", command)
            # sh shipped with OS X does't support echo -n, but supports printf
            try:
                self._httpd = subprocess.Popen(
                    command,
                    # don't care about setting stdout and stderr,
                    # we're in test mode anyway
                    shell=True,
                    executable=None,
                    # "preexec_fn" is UNIX specific, but so is "command"
                    preexec_fn=os.setsid)
            except OSError as error:  # ValueError should not happen!
                logger.debug(
                    "Couldn't execute manual command: %s", error, exc_info=True)
                return False
            logger.debug("Manual command running as PID %s.", self._httpd.pid)
            # give it some time to bootstrap, before we try to verify
            # (cert generation in case of simpleHttpS might take time)
            self._test_mode_busy_wait(port)

            if self._httpd.poll() is not None:
                raise errors.Error("Couldn't execute manual command")
        else:
            if self._is_text_mode():
                self._notify_and_wait(
                    self._get_message(achall).format(
                        validation=validation,
                        response=response,
                        uri=achall.chall.uri(achall.domain),
                        command=command))
            else:
                data = OrderedDict()
                data['cmd'] = 'validate'
                data['type'] = 'http'
                data['validation'] = validation
                data['uri'] = achall.chall.uri(achall.domain)
                data['command'] = command
                data['key-auth'] = response.key_authorization
                self._json_out_and_wait(data)

        if not response.simple_verify(
                achall.chall, achall.domain,
                achall.account_key.public_key(), self.config.http01_port):
            logger.warning("Self-verify of challenge failed.")

        return response

    def _perform_dns01_challenge(self, achall):
        response, validation = achall.response_and_validation()

        if not self.conf("test-mode"):
            if self._is_text_mode():
                self._notify_and_wait(
                    self._get_message(achall).format(
                        validation=validation,
                        domain=achall.validation_domain_name(achall.domain),
                        response=response))
            else:
                data = OrderedDict()
                data['cmd'] = 'validate'
                data['type'] = 'dns'
                data['validation'] = validation
                data['domain'] = achall.validation_domain_name(achall.domain)
                data['key-auth'] = response.key_authorization
                self._json_out_and_wait(data)

        try:
            verification_status = response.simple_verify(
                achall.chall, achall.domain,
                achall.account_key.public_key())
        except acme_errors.DependencyError:
            logger.warning("Self verification requires optional "
                           "dependency `dnspython` to be installed.")
        else:
            if not verification_status:
                logger.warning("Self-verify of challenge failed.")

        return response

    def _cleanup_http01_challenge(self, achall):
        # pylint: disable=missing-docstring,unused-argument
        if self.conf("test-mode"):
            assert self._httpd is not None, (
                "cleanup() must be called after perform()")
            if self._httpd.poll() is None:
                logger.debug("Terminating manual command process")
                os.killpg(self._httpd.pid, signal.SIGTERM)
            else:
                logger.debug("Manual command process already terminated "
                             "with %s code", self._httpd.returncode)
            shutil.rmtree(self._root)

    def _is_text_mode(self):
        return self.conf("text-mode")

    def _json_out(self, data, new_line=False):
        # pylint: disable=no-self-use
        json_str = json.dumps(data)
        if new_line:
            json_str += '\n'
        sys.stdout.write(json_str)
        sys.stdout.flush()

    def _json_out_and_wait(self, data):
        # pylint: disable=no-self-use
        self._json_out(data, True)
        six.moves.input("")

    def _notify_and_wait(self, message):
        # pylint: disable=no-self-use
        sys.stdout.write(message)
        sys.stdout.write("Press ENTER to continue")
        sys.stdout.flush()
        six.moves.input("")

    def _get_ip_logging_permission(self):
        # pylint: disable=missing-docstring
        if self.config.noninteractive_mode and self.conf("public-ip-logging-ok"):
            self.config.namespace.certbot_external_auth_out_public_ip_logging_ok = True
            self.config.namespace.manual_public_ip_logging_ok = True
            return

        if self.config.noninteractive_mode:
            raise errors.PluginError("Must agree to IP logging to proceed")

        if not (self.conf("test-mode") or self.conf("public-ip-logging-ok")):
            if not zope.component.getUtility(interfaces.IDisplay).yesno(
                    self.IP_DISCLAIMER, "Yes", "No",
                    cli_flag="--certbot-external-auth:out-public-ip-logging-ok"):
                raise errors.PluginError("Must agree to IP logging to proceed")

            else:
                self.config.namespace.certbot_external_auth_out_public_ip_logging_ok = True
                self.config.namespace.manual_public_ip_logging_ok = True

    def _get_message(self, achall):
        # pylint: disable=missing-docstring,no-self-use,unused-argument
        return self.MESSAGE_TEMPLATE.get(achall.chall.typ, "")

