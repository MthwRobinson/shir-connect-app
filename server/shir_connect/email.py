"""Class for managing connections to the SMTP server and sending emails."""
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import smtplib

import daiquiri

import shir_connect.configuration as conf
import socket
socket.setdefaulttimeout(30)

class Email:
    """Handles connections to the SMTP server and sends e-mails
    on behalf of info@fiddleranalytics.com"""
    def __init__(self):
        daiquiri.setup(level=logging.INFO)
        self.logger = daiquiri.getLogger(__name__)

        self.server = smtplib.SMTP(host=conf.SMTP_HOST,
                                   port=str(conf.SMTP_PORT))

        self.from_address = conf.SMTP_USER

    def send_email(self, to_address, subject, content, text_format='plain'):
        """Sends an email on behalf of info@fiddleranalytics.com

        Parameters
        ----------
        to_address: str, the recipient of the e-mail
        subject: str, the subject line for the e-mail
        content: str, the content of the e-mail
        text_format: str, 'plain' or 'html'. Determines how the content
            of the message is parsed and dispalyed in the e-mail

        Returns
        -------
        Sends an e-mail to the appropriate addresses.
        """
        self._connect()
        msg = MIMEMultipart()
        msg['From'] = self.from_address
        msg['To'] = to_address
        msg['Subject'] = subject
        msg.attach(MIMEText(content, text_format))

        try:
            self.server.sendmail(msg['From'], msg['To'], msg.as_string())
            email_sent = True
        except smtplib.SMTPRecipientsRefused:
            self.logger.warning('E-mail failed. Check recipient e-mail addresses.')
            email_sent = False

        return email_sent

    def _connect(self):
        self.server.starttls()
        self.server.login(conf.SMTP_USER, conf.SMTP_PASSWORD)
