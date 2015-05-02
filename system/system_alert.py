#!/usr/bin/python

"""
    Author: Justin Walrath (walrathjaw@gmail.com)
    Description:
        System script that will read the system information in order to keep track of things like
        temperature, disk space, cpu load, and ram for the raspberry pi and submit an email alert.
"""

import json
import os.path
import time
import sys

from system.monitoractions.CPUReaderProcessRunner import CPUReaderProcessRunner
from system.monitoractions.RAMReaderProcessRunner import RAMReaderProcessRunner
from system.monitoractions.TEMPReaderProcessRunner import TEMPReaderProcessRunner
from system.monitoractions.DISKReaderProcessRunner import DISKReaderProcessRunner
from pimailframework.EmailManager import EmailManager
from pimailframework.containers.MailMan import MailMan


class FileSystemManager:
    """Filesystem controller"""

    def load_properties(self, file_name):
        """Parses a JSON config file"""
        with open(file_name) as data_stream:
            return json.load(data_stream)

    def load_pause_data(self, filename):
        """Returns the pause config"""
        if os.path.isfile(filename):
            return self.load_properties(filename)
        return None


class SystemReader:
    """Main utility to read the system information"""

    CPU_ERROR = "CPU average over the last 15 minutes has met the threshold({}%): {}%"
    RAM_ERROR = "Current RAM usage is above threshold({}MB): {}MB / {}MB. Only {}MB free"
    TEMP_ERROR = "Temperature is over threshold({}C): {}C"
    DISK_ERROR = "Current disk usage is above threshold({}GB): {}GB / {}GB. Only {}GB free"

    def __init__(self):
        """Sets up the object."""
        self.options = ["CPU", "RAM", "TEMP", "DISK"]
        self.readers = [CPUReaderProcessRunner(),
                        RAMReaderProcessRunner(),
                        TEMPReaderProcessRunner(),
                        DISKReaderProcessRunner()]

    def read_system(self):
        """System reader main function to call the others"""
        return dict(zip(self.options, map(lambda x: x.read_process(), self.readers)))

    def determine_thresholds(self, thresholds, system_stats):
        """Determines the thresholds and creates error messages"""
        error_messages = []
        if float(system_stats["CPU"]) >= float(thresholds["cpu"]):
            error_messages.append(self.CPU_ERROR.format(thresholds["cpu"], system_stats["CPU"]))
        if float(system_stats["RAM"]["used"]) >= float(thresholds["ram"]):
            error_messages.append(self.RAM_ERROR.format(thresholds["ram"],
                                                        system_stats["RAM"]["used"],
                                                        system_stats["RAM"]["total"],
                                                        system_stats["RAM"]["free"]))
        if float(system_stats["TEMP"]) >= float(thresholds["temp"]):
            error_messages.append(self.TEMP_ERROR.format(thresholds["temp"], system_stats["TEMP"]))
        if float(system_stats["DISK"]["used"]) >= float(thresholds["disk"]):
            error_messages.append(self.DISK_ERROR.format(thresholds["disk"],
                                                         system_stats["DISK"]["used"],
                                                         system_stats["DISK"]["total"],
                                                         system_stats["DISK"]["free"]))
        return error_messages


def send_email_notification(email_data, messages):
    """Sends out an email alert"""
    if len(messages):
        content = "<h1>The following issues are occurring with the pi:</h1><br><br>\n"
        for message in messages:
            content += message + "<br><br>\n"

        mailman = MailMan(email_data["host"], email_data["port"], email_data["username"], email_data["password"])

        email_manager = EmailManager()
        envelope = email_manager.prepare_mail(email_data["username"],
                                              email_data["receivers"],
                                              "Raspberry Pi Server Warnings",
                                              content, mailman)
        return email_manager.send_mail(envelope)
    return False


def alert(config, error_messages):
    EmailManager().prepare_and_send_mail(config["email"], error_messages)

epoch_milli = lambda: int(round(time.time() * 1000))

if len(sys.argv) > 1:
    new_pause_config = {"pause_until": int(sys.argv) * 1000 * 60}
    with open('pause.json', 'w') as fp:
        json.dump(new_pause_config, fp)
else:
    file_system_manager = FileSystemManager()
    app_config = file_system_manager.load_properties("config.json")
    pause_config = file_system_manager.load_pause_data("pause.json")
    system_reader = SystemReader()
    system_stats = system_reader.read_system()
    errors = system_reader.determine_thresholds(app_config["thresholds"], system_stats)
    print(errors)

    if pause_config:
        if epoch_milli > int(pause_config["pause_until"]):
            alert(app_config, errors)
    else:
        alert(app_config, errors)
