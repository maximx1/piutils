#!/usr/bin/python3

"""
    Author: Justin Walrath (walrathjaw@gmail.com)
    Description:
        Pinger system that will ping websites to verify their up status.
"""

import json
import httplib2
from pimailframework.EmailManager import EmailManager
from pimailframework.containers.MailMan import MailMan

def load_json_properties(self, file_name):
    """loads a json properties file"""
    data_stream = open(file_name)
    data = json.load(data_stream)
    data_stream.close()
    return data

def send_email_notification(email_data, messages):
    """Sends out an email alert"""
    if len(messages):
        content = "<h1>The following websites returned non-200 status codes:</h1><br><br>"
        for message in messages:
            content += message + "<br><br>\n"

        mailman = MailMan(email_data["host"], email_data["port"], email_data["username"], email_data["password"])

        email_manager = EmailManager()
        envelope = email_manager.prepare_mail(email_data["username"],
                                              email_data["recievers"],
                                              "Raspberry Pi Website Ping errors",
                                              content, mailman)
        return email_manager.send_mail()
    return False

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

config = load_json_properties("config.json")
error_messages = WebsitePinger().ping_websites(config["websites"])
print(error_messages)
send_email_notification(config["email"], error_messages)

