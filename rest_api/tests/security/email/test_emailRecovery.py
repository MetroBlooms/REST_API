import rest_api.tests.unit_test_fix
import unittest
from unittest import TestCase
import os

from rest_api.security.email.email_config import EmailConfig
from rest_api.security.email.email_recovery import EmailRecovery

class TestEmailRecovery(TestCase):

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
        emailRecovery = EmailRecovery()
        emailRecovery.sendEmail('chris@fletch22.com')

if __name__ == '__main__' and __package__ is None:
    unittest.main()