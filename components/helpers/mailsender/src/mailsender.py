import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

DEFAULT_SMTP_PORT = 587
DEFAULT_TIMEOUT = '10'
SMTP_OK_STATUS_CODE = 250
STANDARD_SMTP_PORTS = (25, 465, 587, 2525)
DEFAULT_HOST = "localhost"
DEFAULT_USE_TLS = False 

DEFAULT_FROM = "from@example.com"
DEFAULT_SUBJECT = "mailsender - default suject"
DEFAULT_TEXT_MESSAGE = "Email sent from mail sender"
BASE_SUCCESS_MESSAGE = 'The mail has been sent successfully'
BASE_FAILED_MESSAGE = 'Failed to send email'

USERNAME = os.getenv('USERNAME', '')
PASSWORD = os.getenv('PASSWORD', '')
FROM = os.getenv('FROM', DEFAULT_FROM)
TO = os.getenv('TO', '')
SUBJECT = os.getenv('SUBJECT', DEFAULT_SUBJECT)
BODY_PLAIN = os.getenv('BODY_PLAIN', DEFAULT_TEXT_MESSAGE)
BODY_HTML = os.getenv('BODY_HTML', DEFAULT_TEXT_MESSAGE)

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
logger.setLevel(logging.DEBUG)

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
                message.attach(part)
            except FileNotFoundError:
                self.fail(f'Failed to add an attachment. No such file {base_name}')

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

        # if body_html_filename is not None:
        #     try:
        #         with open(body_html_filename, 'r') as f:
        #             body_html = f.read()
        #     except FileNotFoundError as e:
        #         self.fail(message=f'{BASE_FAILED_MESSAGE}: {str(e)}')

        # create a message
        msg = MIMEMultipart('alternative')
        msg['FROM'] = FROM
        msg['TO'] = TO
        msg['Subject'] = SUBJECT

        # send both html and text
        part1 = MIMEText(BODY_PLAIN, 'plain', _charset='utf-8')
        part2 = MIMEText(BODY_HTML, 'html', _charset='utf-8')

        msg.attach(part1)
        msg.attach(part2)

        # if attachments is not None:
        #     self.add_attachments(msg, attachments.split(','))

        logger.info('Sending email...')

        result = None

        try:
            logger.debug('Creating SMTP')
            smtp = smtplib.SMTP(HOST, PORT, timeout=timeout)
            logger.debug('Set debug level')
            smtp.set_debuglevel(DEBUG_LEVEL)
            if USE_TLS or PASSWORD:
                logger.info("using TLS")
                logger.debug("USERNAME: " + USERNAME)
                smtp.starttls()
            else:
                logger.debug("not using TLS")
            smtp.login(USERNAME, PASSWORD)
            smtp.send_message(msg)
            result = smtp.noop()
            smtp.quit()
        # connection error or timeout
        except OSError as e:
            logger.error(e)
            # self.fail(message=(
            #     f'{BASE_FAILED_MESSAGE} to {TO}. '
            #     f'Check your configuration settings'
            #     f'{(f": {e}" if DEBUG else f".")}'
            # ))

        if result is None or result[0] != SMTP_OK_STATUS_CODE:
            logger.error(BASE_FAILED_MESSAGE)
            # self.fail(message=(
            #     f'{BASE_FAILED_MESSAGE} to {TO}. '
            #     f'{(f": response {result}" if DEBUG else f".")}'
            # ))
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
