#!/usr/bin/python3

"""
	Author: Justin Walrath (walrathjaw@gmail.com)
	Description: 
		Pinger system that will ping websites to verify their up status.
"""

import json
import subprocess
import smtplib
import httplib2

"""
	Filesystem controller.
"""
class FileSystemManager:
	"""
		Parses a JSON config file.
	"""
	def loadProperties(self, fileName):
		dataStream = open(fileName)
		data = json.load(dataStream)
		dataStream.close()
		return data

"""
	SMTP email sender.
"""
class EmailManager:
	"""
		Sends an email out with the error messages.
	"""
	def prepareAndSendMail(self, emailData, messages):
		if len(messages):	
			header = 'To: ' + ", ".join(emailData["recievers"]) + '\nFrom: ' + emailData["username"] + '\nMIME-Version: 1.0\nContent-Type: text/html\nSubject: Raspberry Pi Website Ping errors\n'
			emailMessage = header + "\n<h1>The following websites returned non-200 status codes:</h1><br><br>\n"
			for message in messages:
				emailMessage += message + "<br><br>\n"
			self.sendMail(emailData, emailMessage)
		return False
	
	"""
		Sends an email out.
	"""
	def sendMail(self, clientData, message):
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
	def pingWebsites(self, websites):
		errors = []
		for website in websites:
			connection = httplib2.Http(".cache")
			response, _ = connection.request(website, "GET")
			if response.status != 200 and response.status != 303:
				errors.append("Result: (" + website + ", " + str(response.status) + " - " + response.reason + ")")
		return errors

config = FileSystemManager().loadProperties("config.json")
websitePinger = WebsitePinger()
errorMessages = websitePinger.pingWebsites(config["websites"])
print(errorMessages)
EmailManager().prepareAndSendMail(config["email"], errorMessages)

