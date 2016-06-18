import rest_api.tests.unit_test_fix
import unittest
from unittest import TestCase
import os
from datetime import datetime, timedelta
import time

from rest_api.security.email.email_config import EmailConfig
from rest_api.security.email.email_recovery import EmailRecovery

class TestEmailRecovery(TestCase):

    def setUp(self):
        self.emailRecovery = EmailRecovery()
        EmailRecovery.secureTokenList = []

    def tearDown(self):
        EmailRecovery.secureTokenList = []

    # Test to see if we can find the email_recovery.ini file.
    def test_config_file_path(self):
        emailConfig = EmailConfig()

        path = emailConfig.resolved_config_path()
        self.assertEqual(os.path.isfile(path), True)

    def test_can_read_config(self):
        emailConfig = EmailConfig()

        self.assertEqual(len(emailConfig.config.sections()), 1)

        sections = emailConfig.config.sections()

        self.assertTrue(sections[0] == 'main')

        self.assertTrue(emailConfig.get_account_recovery_password() != '')

    def test_send_mail(self):
        self.emailRecovery.sendEmail('chris@fletch22.com', 'http://bar21342134.com')

    def test_token_generation(self):
        token = self.emailRecovery.generate_secure_token('foo@bar.com')

        numInList = len(EmailRecovery.secureTokenList)

        self.assertIsNotNone(token)
        self.assertEqual(1, numInList)

    def test_multiple_generate_secure_token(self):
        email_address = 'foo@bar.com'
        token1 = self.emailRecovery.generate_secure_token(email_address)

        foundSecurityToken = self.findsecuritytoken(email_address)
        timestamporiginal = foundSecurityToken.timestamp

        token2 = self.emailRecovery.generate_secure_token(email_address)
        foundSecurityToken = self.findsecuritytoken(email_address)
        timestampUpdated = foundSecurityToken.timestamp

        numInList = len(EmailRecovery.secureTokenList)

        self.assertIsNotNone(foundSecurityToken)
        self.assertEquals(token1, token2)
        self.assertTrue(timestamporiginal < timestampUpdated)
        self.assertEqual(1, numInList)

    def findsecuritytoken(self, email_address):
        foundSecurityToken = None
        for securityToken in EmailRecovery.secureTokenList:
            if securityToken.email_address == email_address:
                foundSecurityToken = securityToken

        return foundSecurityToken

    # Removes stale tokens
    def test_clean_security_token_list(self):

        token1 = self.emailRecovery.append_security_token('foo@bar.com', 'asdf')
        token2 = self.emailRecovery.append_security_token('bar@foo.com', 'basdf')

        self.assertEqual(len(EmailRecovery.secureTokenList), 2)

        sixminutesago = datetime.fromtimestamp(token1.timestamp) - timedelta(minutes=EmailRecovery.MAX_MINUTES_TOKEN_LIFETIME + 1)

        token1.timestamp = time.mktime(sixminutesago.timetuple())

        token3 = self.emailRecovery.append_security_token('fiz@buzz.com', '123535231')

        self.assertEqual(len(EmailRecovery.secureTokenList), 2)
        self.assertFalse(EmailRecovery.secureTokenList.__contains__(token1))

    def test_create_and_validate_recovery_link(self):

        link = self.emailRecovery.generate_recovery_link('http://foo.com?test=value', 'bar@sadfifew,com')
        isvalid = self.emailRecovery.validate_recovery_link(link)

        self.assertTrue(isvalid)

if __name__ == '__main__' and __package__ is None:
    unittest.main()