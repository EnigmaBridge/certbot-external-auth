"""Tests for certbot.auth_handler."""
import functools
import logging
import unittest
import os
import tempfile
import shutil

import mock
import six
import zope.component

from acme import challenges
from acme import client as acme_client
from acme import messages

from certbot import achallenges, configuration
from certbot import errors
from certbot import interfaces
from certbot import util
from certbot import constants

from certbot.tests import acme_util
from certbot.tests import util as test_util

@unittest.skip
class ChallengeFactoryTest(unittest.TestCase):
    # pylint: disable=protected-access

    def setUp(self):
        from certbot.auth_handler import AuthHandler

        # Account is mocked...
        self.handler = AuthHandler(None, None, mock.Mock(key="mock_key"), [])

        self.dom = "test"
        self.handler.authzr[self.dom] = acme_util.gen_authzr(
            messages.STATUS_PENDING, self.dom, acme_util.CHALLENGES,
            [messages.STATUS_PENDING] * 6, False)

    def test_all(self):
        achalls = self.handler._challenge_factory(
            self.dom, range(0, len(acme_util.CHALLENGES)))

        self.assertEqual(
            [achall.chall for achall in achalls], acme_util.CHALLENGES)

    def test_one_tls_sni(self):
        achalls = self.handler._challenge_factory(self.dom, [1])

        self.assertEqual(
            [achall.chall for achall in achalls], [acme_util.TLSSNI01])

    def test_unrecognized(self):
        self.handler.authzr["failure.com"] = acme_util.gen_authzr(
            messages.STATUS_PENDING, "failure.com",
            [mock.Mock(chall="chall", typ="unrecognized")],
            [messages.STATUS_PENDING])

        self.assertRaises(
            errors.Error, self.handler._challenge_factory, "failure.com", [0])


class GetAuthorizationsTest(unittest.TestCase):
    """get_authorizations test.

    This tests everything except for all functions under _poll_challenges.

    """

    def setUp(self):
        from certbot.auth_handler import AuthHandler
        from certbot_external_auth.plugin import AuthenticatorOut

        self.name = 'certbot-external-auth'
        self.name_cfg = self.name.replace('-', '_') + '_'
        self.tempdir = tempfile.mkdtemp(dir=tempfile.gettempdir())
        self.config = configuration.NamespaceConfig(
            mock.MagicMock(**constants.CLI_DEFAULTS)
        )

        self.patch_tls = mock.patch('acme.challenges.TLSSNI01Response.simple_verify')
        self.patch_http = mock.patch('acme.challenges.HTTP01Response.simple_verify')
        self.patch_dns = mock.patch('acme.challenges.DNS01Response.simple_verify')

        self.patch_tls.start()
        self.patch_http.start()
        self.patch_dns.start()

        self.config.verb = "certonly"
        self.config.config_dir = os.path.join(self.tempdir, 'config')
        self.config.work_dir = os.path.join(self.tempdir, 'work')
        self.config.logs_dir = os.path.join(self.tempdir, 'logs')
        self.config.cert_path = constants.CLI_DEFAULTS['auth_cert_path']
        self.config.fullchain_path = constants.CLI_DEFAULTS['auth_chain_path']
        self.config.chain_path = constants.CLI_DEFAULTS['auth_chain_path']
        self.config.server = "example.com"
        self.config.__setattr__(self.name_cfg + 'handler', None)
        self.config.__setattr__(self.name_cfg + 'public_ip_logging_ok', True)
        self.config.__setattr__(self.name_cfg + 'test_mode', False)
        self.config.__setattr__(self.name_cfg + 'text_mode', False)
        self.config.__setattr__(self.name_cfg + 'dehydrated_dns', False)

        self.mock_display = mock.Mock()
        zope.component.provideUtility(
            self.mock_display, interfaces.IDisplay)
        zope.component.provideUtility(
            mock.Mock(debug_challenges=False), interfaces.IConfig)

        self.mock_auth = AuthenticatorOut(self.config, self.name)

        self.mock_auth.get_chall_pref = mock.MagicMock()
        self.mock_auth.get_chall_pref.return_value = [challenges.TLSSNI01]

        self.mock_data = []
        self.mock_json_out = mock.MagicMock(side_effect=self._update_data)
        self.mock_auth._json_out_and_wait = self.mock_json_out

        self.mock_auth.cleanup = mock.Mock()

        self.key_mock = mock.Mock()
        self.key_mock.key = mock.Mock()
        self.key_mock.key.file_path = 'PEM'
        self.key_mock.thumbprint = mock.MagicMock(return_value=b'00001234567890000')

        self.mock_account = mock.Mock(key=self.key_mock)
        self.mock_net = mock.MagicMock(spec=acme_client.Client)

        self.handler = AuthHandler(
            self.mock_auth, self.mock_net, self.mock_account, [])

        self.input_patch = mock.patch('six.moves.input')
        self.input_patch.start()

        logging.disable(logging.CRITICAL)

    def tearDown(self):
        shutil.rmtree(self.tempdir)
        logging.disable(logging.NOTSET)
        self.input_patch.stop()
        self.patch_tls.stop()
        self.patch_http.stop()
        self.patch_dns.stop()

    def _help_output(self, args):
        "Run a command, and return the output string for scrutiny"

        output = six.StringIO()

        def write_msg(message, *args, **kwargs): # pylint: disable=missing-docstring,unused-argument
            output.write(message)

        with mock.patch('certbot.main.sys.stdout', new=output):
            with test_util.patch_get_utility() as mock_get_utility:
                mock_get_utility().notification.side_effect = write_msg
                with mock.patch('certbot.main.sys.stderr'):
                    self.assertRaises(SystemExit, self._unmocked_parse, args, output)

        return output.getvalue()

    @mock.patch("certbot.auth_handler.AuthHandler._poll_challenges")
    def test_name1_tls_sni_01_1(self, mock_poll):
        self.mock_net.request_domain_challenges.side_effect = functools.partial(
            gen_dom_authzr, challs=acme_util.CHALLENGES)

        mock_poll.side_effect = self._validate_all

        authzr = self.handler.get_authorizations(["0"])

        self.assertEqual(self.mock_net.answer_challenge.call_count, 1)

        self.assertEqual(mock_poll.call_count, 1)
        chall_update = mock_poll.call_args[0][0]
        self.assertEqual(list(six.iterkeys(chall_update)), ["0"])
        self.assertEqual(len(chall_update.values()), 1)

        self.assertEqual(self.mock_auth.cleanup.call_count, 1)
        # Test if list first element is TLSSNI01, use typ because it is an achall
        self.assertEqual(
            self.mock_auth.cleanup.call_args[0][0][0].typ, "tls-sni-01")

        self.assertEqual(len(authzr), 1)
        self.assertEqual(self.mock_json_out.call_count, 1)
        self.assertEqual(len(self.mock_data), 1)
        self.assertIn('cmd', self.mock_data[0])
        self.assertIn('token', self.mock_data[0])
        self.assertIn('validation', self.mock_data[0])
        self.assertTrue(len(self.mock_data[0]['validation']) > 5)

    @mock.patch("certbot.auth_handler.AuthHandler._poll_challenges")
    def test_name1_tls_sni_01_1_http_01_1_dns_1(self, mock_poll):
        self.mock_net.request_domain_challenges.side_effect = functools.partial(
            gen_dom_authzr, challs=acme_util.CHALLENGES, combos=False)

        mock_poll.side_effect = self._validate_all
        self.mock_auth.get_chall_pref.return_value.append(challenges.HTTP01)
        self.mock_auth.get_chall_pref.return_value.append(challenges.DNS01)

        authzr = self.handler.get_authorizations(["0"])

        self.assertEqual(self.mock_net.answer_challenge.call_count, 3)

        self.assertEqual(mock_poll.call_count, 1)
        chall_update = mock_poll.call_args[0][0]
        self.assertEqual(list(six.iterkeys(chall_update)), ["0"])
        self.assertEqual(len(chall_update.values()), 1)

        self.assertEqual(self.mock_auth.cleanup.call_count, 1)
        # Test if list first element is TLSSNI01, use typ because it is an achall
        for achall in self.mock_auth.cleanup.call_args[0][0]:
            self.assertTrue(achall.typ in ["tls-sni-01", "http-01", "dns-01"])

        # Length of authorizations list
        self.assertEqual(len(authzr), 1)
        self.assertEqual(self.mock_json_out.call_count, 3)
        self.assertEqual(len(self.mock_data), 3)
        for msg in self.mock_data:
            self.assertIn('cmd', msg)
            self.assertIn('token', msg)
            self.assertIn('validation', msg)
            self.assertTrue(len(msg['validation']) > 5)

    @mock.patch("certbot.auth_handler.AuthHandler._poll_challenges")
    def test_name3_tls_sni_01_3(self, mock_poll):
        self.mock_net.request_domain_challenges.side_effect = functools.partial(
            gen_dom_authzr, challs=acme_util.CHALLENGES)

        mock_poll.side_effect = self._validate_all

        with mock.patch('certbot.util.safe_open') as mock_open:
            mock_open.return_value = mock.MagicMock()
            authzr = self.handler.get_authorizations(["0", "1", "2"])

        self.assertEqual(self.mock_net.answer_challenge.call_count, 3)

        # Check poll call
        self.assertEqual(mock_poll.call_count, 1)
        chall_update = mock_poll.call_args[0][0]
        self.assertEqual(len(list(six.iterkeys(chall_update))), 3)
        self.assertTrue("0" in list(six.iterkeys(chall_update)))
        self.assertEqual(len(chall_update["0"]), 1)
        self.assertTrue("1" in list(six.iterkeys(chall_update)))
        self.assertEqual(len(chall_update["1"]), 1)
        self.assertTrue("2" in list(six.iterkeys(chall_update)))
        self.assertEqual(len(chall_update["2"]), 1)

        self.assertEqual(self.mock_auth.cleanup.call_count, 1)

        self.assertEqual(len(authzr), 3)

        self.assertEqual(self.mock_json_out.call_count, 3)
        self.assertEqual(len(self.mock_data), 3)
        for msg in self.mock_data:
            self.assertIn('cmd', msg)
            self.assertIn('token', msg)
            self.assertIn('validation', msg)
            self.assertTrue(len(msg['validation']) > 5)

    @mock.patch("certbot.auth_handler.AuthHandler._poll_challenges")
    def test_debug_challenges(self, mock_poll):
        zope.component.provideUtility(
            mock.Mock(debug_challenges=True), interfaces.IConfig)
        self.mock_net.request_domain_challenges.side_effect = functools.partial(
            gen_dom_authzr, challs=acme_util.CHALLENGES)

        mock_poll.side_effect = self._validate_all

        self.handler.get_authorizations(["0"])

        self.assertEqual(self.mock_net.answer_challenge.call_count, 1)
        self.assertEqual(self.mock_display.notification.call_count, 1)

    def test_perform_failure(self):
        self.mock_net.request_domain_challenges.side_effect = functools.partial(
            gen_dom_authzr, challs=acme_util.CHALLENGES)

        self.mock_auth.perform = mock.Mock()
        self.mock_auth.perform.side_effect = errors.AuthorizationError

        self.assertRaises(
            errors.AuthorizationError, self.handler.get_authorizations, ["0"])

    def test_no_domains(self):
        self.assertRaises(errors.AuthorizationError, self.handler.get_authorizations, [])

    @mock.patch("certbot.auth_handler.AuthHandler._poll_challenges")
    def test_preferred_challenge_choice(self, mock_poll):
        self.mock_net.request_domain_challenges.side_effect = functools.partial(
            gen_dom_authzr, challs=acme_util.CHALLENGES)

        mock_poll.side_effect = self._validate_all
        self.mock_auth.get_chall_pref.return_value.append(challenges.HTTP01)

        self.handler.pref_challs.extend((challenges.HTTP01.typ,
                                         challenges.DNS01.typ,))

        self.handler.get_authorizations(["0"])

        self.assertEqual(self.mock_auth.cleanup.call_count, 1)
        self.assertEqual(
            self.mock_auth.cleanup.call_args[0][0][0].typ, "http-01")

    def test_preferred_challenges_not_supported(self):
        self.mock_net.request_domain_challenges.side_effect = functools.partial(
            gen_dom_authzr, challs=acme_util.CHALLENGES)
        self.handler.pref_challs.append(challenges.HTTP01.typ)
        self.assertRaises(
            errors.AuthorizationError, self.handler.get_authorizations, ["0"])

    def _validate_all(self, unused_1, unused_2):
        for dom in six.iterkeys(self.handler.authzr):
            azr = self.handler.authzr[dom]
            self.handler.authzr[dom] = acme_util.gen_authzr(
                messages.STATUS_VALID,
                dom,
                [challb.chall for challb in azr.body.challenges],
                [messages.STATUS_VALID] * len(azr.body.challenges),
                azr.body.combinations)

    def _update_data(self, x):
        self.mock_data.append(x)


class PollChallengesTest(unittest.TestCase):
    # pylint: disable=protected-access
    """Test poll challenges."""

    def setUp(self):
        from certbot.auth_handler import challb_to_achall
        from certbot.auth_handler import AuthHandler

        # Account and network are mocked...
        self.mock_net = mock.MagicMock()
        self.handler = AuthHandler(
            None, self.mock_net, mock.Mock(key="mock_key"), [])

        self.doms = ["0", "1", "2"]
        self.handler.authzr[self.doms[0]] = acme_util.gen_authzr(
            messages.STATUS_PENDING, self.doms[0],
            [acme_util.HTTP01, acme_util.TLSSNI01],
            [messages.STATUS_PENDING] * 2, False)

        self.handler.authzr[self.doms[1]] = acme_util.gen_authzr(
            messages.STATUS_PENDING, self.doms[1],
            acme_util.CHALLENGES, [messages.STATUS_PENDING] * 3, False)

        self.handler.authzr[self.doms[2]] = acme_util.gen_authzr(
            messages.STATUS_PENDING, self.doms[2],
            acme_util.CHALLENGES, [messages.STATUS_PENDING] * 3, False)

        self.chall_update = {}
        for dom in self.doms:
            self.chall_update[dom] = [
                challb_to_achall(challb, mock.Mock(key="dummy_key"), dom)
                for challb in self.handler.authzr[dom].body.challenges]

    @mock.patch("certbot.auth_handler.time")
    def test_poll_challenges(self, unused_mock_time):
        self.mock_net.poll.side_effect = self._mock_poll_solve_one_valid
        self.handler._poll_challenges(self.chall_update, False)

        for authzr in self.handler.authzr.values():
            self.assertEqual(authzr.body.status, messages.STATUS_VALID)

    @mock.patch("certbot.auth_handler.time")
    def test_poll_challenges_failure_best_effort(self, unused_mock_time):
        self.mock_net.poll.side_effect = self._mock_poll_solve_one_invalid
        self.handler._poll_challenges(self.chall_update, True)

        for authzr in self.handler.authzr.values():
            self.assertEqual(authzr.body.status, messages.STATUS_PENDING)

    @mock.patch("certbot.auth_handler.time")
    @test_util.patch_get_utility()
    def test_poll_challenges_failure(self, unused_mock_time, unused_mock_zope):
        self.mock_net.poll.side_effect = self._mock_poll_solve_one_invalid
        self.assertRaises(
            errors.AuthorizationError, self.handler._poll_challenges,
            self.chall_update, False)

    @mock.patch("certbot.auth_handler.time")
    def test_unable_to_find_challenge_status(self, unused_mock_time):
        from certbot.auth_handler import challb_to_achall
        self.mock_net.poll.side_effect = self._mock_poll_solve_one_valid
        self.chall_update[self.doms[0]].append(
            challb_to_achall(acme_util.DNS01_P, "key", self.doms[0]))
        self.assertRaises(
            errors.AuthorizationError, self.handler._poll_challenges,
            self.chall_update, False)

    def test_verify_authzr_failure(self):
        self.assertRaises(
            errors.AuthorizationError, self.handler.verify_authzr_complete)

    def _mock_poll_solve_one_valid(self, authzr):
        # Pending here because my dummy script won't change the full status.
        # Basically it didn't raise an error and it stopped earlier than
        # Making all challenges invalid which would make mock_poll_solve_one
        # change authzr to invalid
        return self._mock_poll_solve_one_chall(authzr, messages.STATUS_VALID)

    def _mock_poll_solve_one_invalid(self, authzr):
        return self._mock_poll_solve_one_chall(authzr, messages.STATUS_INVALID)

    def _mock_poll_solve_one_chall(self, authzr, desired_status):
        # pylint: disable=no-self-use
        """Dummy method that solves one chall at a time to desired_status.

        When all are solved.. it changes authzr.status to desired_status

        """
        new_challbs = authzr.body.challenges
        for challb in authzr.body.challenges:
            if challb.status != desired_status:
                new_challbs = tuple(
                    challb_temp if challb_temp != challb
                    else acme_util.chall_to_challb(challb.chall, desired_status)
                    for challb_temp in authzr.body.challenges
                )
                break

        if all(test_challb.status == desired_status
               for test_challb in new_challbs):
            status_ = desired_status
        else:
            status_ = authzr.body.status

        new_authzr = messages.AuthorizationResource(
            uri=authzr.uri,
            body=messages.Authorization(
                identifier=authzr.body.identifier,
                challenges=new_challbs,
                combinations=authzr.body.combinations,
                status=status_,
            ),
        )
        return new_authzr, "response"


def gen_auth_resp(chall_list):
    """Generate a dummy authorization response."""
    return ["%s%s" % (chall.__class__.__name__, chall.domain)
            for chall in chall_list]


def gen_dom_authzr(domain, challs, combos=True):
    """Generates new authzr for domains."""
    return acme_util.gen_authzr(
        messages.STATUS_PENDING, domain, challs,
        [messages.STATUS_PENDING] * len(challs), combos)


if __name__ == "__main__":
    unittest.main()  # pragma: no cover
