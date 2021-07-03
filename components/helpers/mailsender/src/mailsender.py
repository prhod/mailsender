import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage

DEFAULT_SMTP_PORT = 587
DEFAULT_TIMEOUT = '10'
SMTP_OK_STATUS_CODE = 250
STANDARD_SMTP_PORTS = (25, 465, 587, 2525)
DEFAULT_HOST = "localhost"
DEFAULT_USE_TLS = False 

DEFAULT_FROM = "from@example.com"
DEFAULT_SUBJECT = "mailsender - default suject"
DEFAULT_TEXT_MESSAGE = ""
DEFAULT_HTML_MESSAGE = "Email sent from <b>mailsender</b>"
BASE_SUCCESS_MESSAGE = 'The mail has been sent successfully'
BASE_FAILED_MESSAGE = 'Failed to send email'

USERNAME = os.getenv('USERNAME', '')
PASSWORD = os.getenv('PASSWORD', '')
FROM = os.getenv('FROM', DEFAULT_FROM)
TO = os.getenv('TO', '')
SUBJECT = os.getenv('SUBJECT', DEFAULT_SUBJECT)
BODY_PLAIN = os.getenv('BODY_PLAIN', DEFAULT_TEXT_MESSAGE)
BODY_HTML = os.getenv('BODY_HTML', DEFAULT_HTML_MESSAGE)
BODY_HTML_FILE = os.getenv('BODY_HTML_FILE', None)
ATTACHMENTS = os.getenv('ATTACHMENTS', None)
IMAGE_ATTACHMENTS = os.getenv('IMAGE_ATTACHMENTS', None)
PORT = int(os.getenv('PORT', DEFAULT_SMTP_PORT))
TIMEOUT = os.getenv('TIMEOUT', DEFAULT_TIMEOUT)
DEBUG_LEVEL = int(os.getenv('DEBUG_LEVEL', 0))
HOST = os.getenv('HOST', DEFAULT_HOST)
USE_TLS = bool(os.getenv('USE_TLS', DEFAULT_USE_TLS))

logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
steam_handler = logging.StreamHandler()
steam_handler.setFormatter(formatter)
logger.addHandler(steam_handler)
logger.setLevel(logging.WARN)


if BODY_HTML_FILE is not None:
    logger.info("Using HTML file as html content")
    try:
        with open(BODY_HTML_FILE, 'r') as f:
            BODY_HTML = f.read()
    except FileNotFoundError as e:
        logger.error(f"Error opening HTML file {BODY_HTML_FILE}")
        logger.error("Continuing with provided BODY_HTML if any.")


class EmailNotify():
    
    def add_attachments(self, message, attachments=None):
        for attachment in attachments or []:
            base_name = os.path.basename(attachment)
            try:
                with open(attachment, "rb") as f:
                    part = MIMEApplication(
                        f.read(),
                        Name=base_name
                    )
                part['Content-Disposition'] = f'attachment; filename="{base_name}"'
                logger.info(f'attaching {base_name}')
                message.attach(part)
            except FileNotFoundError:
                logger.error(f'Failed to add an attachment. No such file {base_name}')
                exit(1)

    def add_image_attachments(self, message, attachments=None):
        for attachment in attachments or []:
            base_name = os.path.basename(attachment)
            try:
                with open(attachment, "rb") as f:
                    msgImage = MIMEImage(f.read())
                msgImage.add_header('Content-ID', f'<{base_name}>')
                logger.info(f'attaching {base_name}')
                message.attach(msgImage)
            except FileNotFoundError:
                logger.error(f'Failed to add an attachment. No such file {base_name}')
                exit(1)
    def run(self):
        if PORT not in STANDARD_SMTP_PORTS:
            logger.warning((
                f'Non standard SMTP PORT using: {PORT}. '
                f'SMTP standard ports are '
                f'{(", ".join(str(i) for i in STANDARD_SMTP_PORTS))}.'
            ))

        if not TO:
            logger.error("'TO' environment variable is requested")
            raise 

        if TIMEOUT is not None and is_valid_timeout(TIMEOUT):
            timeout = float(TIMEOUT)


        # create a message
        msgRoot = MIMEMultipart('related')
        msgRoot['FROM'] = FROM
        msgRoot['TO'] = TO
        msgRoot['Subject'] = SUBJECT
        msgRoot.preamble = '====================================================='

        # send both html and text
        if BODY_PLAIN:
            msgAlternative = MIMEMultipart('alternative')
            msgText = MIMEText(BODY_PLAIN, 'plain', _charset='utf-8')
            msgAlternative.attach(msgText)
            msgRoot.attach(msgAlternative)
        if BODY_HTML:
            msgText = MIMEText(BODY_HTML, 'html', _charset='utf-8')
            msgAlternative.attach(msgText)

        if ATTACHMENTS is not None:
            self.add_attachments(msgRoot, ATTACHMENTS.split(','))

        if IMAGE_ATTACHMENTS is not None:
            self.add_image_attachments(msgRoot, IMAGE_ATTACHMENTS.split(','))

        logger.info('Sending email...')

        result = None

        try:
            smtp = smtplib.SMTP(HOST, PORT, timeout=timeout)
            smtp.set_debuglevel(DEBUG_LEVEL)
            if USE_TLS or PASSWORD:
                logger.info("using TLS")
                smtp.starttls()
            else:
                logger.debug("not using TLS")
            smtp.login(USERNAME, PASSWORD)
            smtp.send_message(msgRoot)
            result = smtp.noop()
            smtp.quit()
        # connection error or timeout
        except OSError as e:
            logger.error(e)
            exit(1)

        if result is None or result[0] != SMTP_OK_STATUS_CODE:
            logger.error(BASE_FAILED_MESSAGE)
            exit(1)
        else:
            logger.info(f'{BASE_SUCCESS_MESSAGE} to {TO}')

def is_valid_timeout(str_value):
    if is_positive_number(str_value):
        return True
    else:
        raise Exception(
            'Wrong TIMEOUT value. '
            'TIMEOUT must be greater than 0.')


def is_positive_number(str_value):
    try:
        return float(str_value) > 0
    except ValueError:
        return False


if __name__ == '__main__':
    sender = EmailNotify()
    sender.run()
