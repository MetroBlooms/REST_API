
from threading import Thread
from flask_mail import Message
from email_config import EmailConfig
from app import app, mail
import uuid
import time
from datetime import datetime
from datetime import timedelta
from urlparse import urlparse, parse_qs

class SecureToken:
    def __init__(self, email_address, token):
        self.email_address = email_address
        self.token = token
        self.timestamp = time.time()

class EmailRecovery():

    MAX_MINUTES_TOKEN_LIFETIME = 20
    secureTokenList = []

    def __init__(self):
        self.email_config = EmailConfig()

    def async(f):
        def wrapper(*args, **kwargs):
            thr = Thread(target=f, args=args, kwargs=kwargs)
            thr.start()

        return wrapper

    def sendEmail(self, addressto, baseurl):

        subject = "EvaluateIt password recovery requested ..."

        msg = Message(
            subject,
            sender=self.email_config.get_account_recovery_username(),
            recipients=[addressto])

        msg.body = 'Hello, ' + 'Click on this link to recover your password: ' + self.generate_recovery_link(addressto, baseurl)

        self.send_email_async(msg)

    @async
    def send_email_async(self, msg):
        with app.app_context():
            mail.send(msg)

    def clean_secure_token_list(self):

        now = time.time()

        for security_token in EmailRecovery.secureTokenList:
            if self.istokenexpired(security_token):
                EmailRecovery.secureTokenList.remove(security_token)

    def istokenexpired(self, security_token):
        datetime_token = datetime.fromtimestamp(security_token.timestamp)
        fiveminutesago = datetime.now() - timedelta(minutes=EmailRecovery.MAX_MINUTES_TOKEN_LIFETIME)
        return datetime_token < fiveminutesago

    def append_security_token(self, email_address, token):

        self.clean_secure_token_list()

        security_token = SecureToken(email_address, token)

        EmailRecovery.secureTokenList.append(security_token)

        return security_token

    def generate_secure_token(self, email_address):

        token = None
        for security_token in EmailRecovery.secureTokenList:
            if security_token.email_address == email_address:
                security_token.timestamp = time.time()
                token = security_token.token

        if token is None:
            # Random uuid generation; most secure choice
            token = uuid.uuid4().urn[9:]
            self.append_security_token(email_address, token)

        return token

    def generate_recovery_link(self, email_address, base_url):
        return base_url + "&token=" + self.generate_secure_token(email_address)

    def validate_recovery_link(self, url):

        urlparsed = urlparse(url)
        querystringdictionary = parse_qs(urlparsed.query)
        token = querystringdictionary['token'][0]

        return self.is_token_valid(token)

    def is_token_valid(self, token):
        istokenvalid = False
        for security_token in EmailRecovery.secureTokenList:
            if self.istokenexpired(security_token) == False:
                istokenvalid = True
                break
        return istokenvalid
