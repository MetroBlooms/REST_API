
from threading import Thread
from flask_mail import Message
from email_config import EmailConfig
from app import app, mail

class EmailRecovery():

    def __init__(self):
        self.email_config = EmailConfig()

    def async(f):
        def wrapper(*args, **kwargs):
            thr = Thread(target=f, args=args, kwargs=kwargs)
            thr.start()

        return wrapper

    def sendEmail(self, addressTo):
        msg = Message(
            'Hello',
            sender=self.email_config.get_account_recovery_username(),
            recipients=[addressTo])

        msg.body = "This is the email body"

        self.send_email_async(msg)

    @async
    def send_email_async(self, msg):
        with app.app_context():
            mail.send(msg)
