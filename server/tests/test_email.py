"""Tests the e-mail sending utility."""
import smtplib

from shir_connect.email import Email

class FakeSMTPServer:
    def __init__(self):
        pass

    def sendmail(self, from_address, to_address, message):
        if to_address == 'jabber@bigflock.birds':
            return True
        else:
            raise smtplib.SMTPRecipientsRefused([from_address])

    def starttls(self):
        pass

    def login(self, user, password):
        pass

def test_plain_email_sends_with_valid_address():
    email = Email()
    email.server = FakeSMTPServer()
    sent = email.send_email(to_address='jabber@bigflock.birds',
                            subject='Lots of birds',
                            content='Flap!',
                            text_format='plain')
    assert sent == True

def test_html_email_sends_with_valid_address():
    email = Email()
    email.server = FakeSMTPServer()
    sent = email.send_email(to_address='jabber@bigflock.birds',
                            subject='Lots of birds',
                            content='<html><p>Flap!</p></html>',
                            text_format='html')
    assert sent == True

def test_email_fails_with_invalid_address():
    email = Email()
    email.server = FakeSMTPServer()
    sent = email.send_email(to_address='chester@bigpack.dogs',
                            subject='Lots of birds',
                            content='Flap!',
                            text_format='plain')
    assert sent == False
