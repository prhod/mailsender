from smtplib import SMTP, SMTPAuthenticationError
from email.base64mime import body_encode as encode_base64
import base64

class mySMTP(SMTP):
    def auth(self, mechanism, authobject, *, initial_response_ok=True):
        """Authentication command - requires response processing.
        'mechanism' specifies which authentication mechanism is to
        be used - the valid values are those listed in the 'auth'
        element of 'esmtp_features'.
        'authobject' must be a callable object taking a single argument:
                data = authobject(challenge)
        It will be called to process the server's challenge response; the
        challenge argument it is passed will be a bytes.  It should return
        bytes data that will be base64 encoded and sent to the server.
        Keyword arguments:
            - initial_response_ok: Allow sending the RFC 4954 initial-response
              to the AUTH command, if the authentication methods supports it.
        """
        # RFC 4954 allows auth methods to provide an initial response.  Not all
        # methods support it.  By definition, if they return something other
        # than None when challenge is None, then they do.  See issue #15014.
        mechanism = mechanism.upper()
        initial_response = (authobject() if initial_response_ok else None)
        if initial_response is not None:
            response = encode_base64(initial_response.encode('utf-8'), eol='')
            (code, resp) = self.docmd("AUTH", mechanism + " " + response)
        else:
            (code, resp) = self.docmd("AUTH", mechanism)
        # If server responds with a challenge, send the response.
        if code == 334:
            challenge = base64.decodebytes(resp)
            response = encode_base64(
                authobject(challenge).encode('utf-8'), eol='')
            (code, resp) = self.docmd(response)
        if code in (235, 503):
            return (code, resp)
        raise SMTPAuthenticationError(code, resp)    