import smtplib
from pimailframework.containers.Envelope import Envelope

class EmailManager:
    """SMTP email sender"""

    _HEADER_TEMPLATE = """To: {}\nFrom: {}\nMIME-Version: 1.0\nContent-Type: text/html\nSubject: {}\n\n"""

    def prepare_mail(self, sender, recipients, subject, content, mailman):
        """Prepares the mail"""
        header = self._HEADER_TEMPLATE.format(", ".join(recipients), sender, subject)
        mail = header + content
        return Envelope(mailman, sender, recipients, mail)

    def send_mail(self, envelope):
        """Sends an email out"""
        try:
            server = smtplib.SMTP(envelope.mailman.host, envelope.mailman.port)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(envelope.mailman.username, envelope.mailman.password)
            server.sendmail(envelope.sender, envelope.recipients, envelope.letter)
            server.close()
        except smtplib.SMTPException as er:
            return False
        return True