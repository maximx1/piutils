#!/usr/bin/python3

"""
    Author: Justin Walrath (walrathjaw@gmail.com)
    Description:
        Pinger system that will ping websites to verify their up status.
"""

import json
import smtplib
import httplib2

"""
    Filesystem controller.r
"""
class FileSystemManager:
    """
        Parses a JSON config file.
    """
    def load_properties(self, fileName):
        data_stream = open(fileName)
        data = json.load(data_stream)
        data_stream.close()
        return data


"""
    SMTP email sender.
"""
class EmailManager:
    """
        Sends an email out with the error messages.
    """
    def prepare_and_send_mail(self, email_data, messages):
        if len(messages):
            header = 'To: ' + ", ".join(email_data["recievers"]) + '\nFrom: ' + email_data[
                "username"] + '\nMIME-Version: 1.0\nContent-Type: text/html\nSubject: Raspberry Pi Website Ping errors\n'
            email_message = header + "\n<h1>The following websites returned non-200 status codes:</h1><br><br>\n"
            for message in messages:
                email_message += message + "<br><br>\n"
            self.send_mail(email_data, email_message)
        return False

    """
        Sends an email out.
    """
    def send_mail(self, clientData, message):
        try:
            server = smtplib.SMTP(clientData["host"], clientData["port"])
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(clientData["username"], clientData["password"])
            server.sendmail(clientData["sender"], clientData["recievers"], message)
            server.close()
        except smtplib.SMTPException as er:
            return False
        return True


"""
    Website Pinger
"""
class WebsitePinger:
    def ping_websites(self, websites):
        errors = []
        for website in websites:
            connection = httplib2.Http(".cache")
            response, _ = connection.request(website, "GET")
            if response.status != 200 and response.status != 303:
                errors.append("Result: (" + website + ", " + str(response.status) + " - " + response.reason + ")")
        return errors


config = FileSystemManager().load_properties("config.json")
website_pinger = WebsitePinger()
error_messages = website_pinger.ping_websites(config["websites"])
print(error_messages)
EmailManager().prepare_and_send_mail(config["email"], error_messages)

