import ConfigParser
import os

class EmailConfig():

    email_recovery_path = '../../configuration/email_recovery.ini'

    def __init__(self):
        self.config = ConfigParser.ConfigParser()
        path = self.resolved_config_path()
        self.config.read(path)

    def resolved_config_path(self):
        path = os.path.join(os.path.dirname(__file__), self.email_recovery_path)
        path = os.path.normpath(path)
        return path

    def get_account_recovery_password(self):
        return self.config.get('main', 'password')

    def get_account_recovery_username(self):
        return self.config.get('main', 'username')