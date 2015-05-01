#!/usr/bin/python

"""
    Author: Justin Walrath (walrathjaw@gmail.com)
    Description:
        System script that will read the system information in order to keep track of things like
        temperature, disk space, cpu load, and ram for the raspberry pi and submit an email alert.
"""

import json
import subprocess
import smtplib
import locale
import os.path
import time
import sys

"""
    Filesystem controller.
"""
class FileSystemManager:
    """
        Parses a JSON config file.
    """
    def load_properties(self, file_name):
        with open(file_name) as data_stream:
            return json.load(data_stream)

    """
        Returns the pause config.
    """
    def load_pause_data(self, filename):
        if os.path.isfile(filename):
            return self.load_properties(filename)
        return None


"""
    Main utility to read the system information.
"""
class SystemReader:
    """
        Error messages
    """
    CPU_ERROR = "CPU average over the last 15 minutes has met the threshold({}%): {}%"
    RAM_ERROR = "Current RAM usage is above threshold({}MB): {}MB / {}MB. Only {}MB free"
    TEMP_ERROR = "Temperature is over threshold({}C): {}C"
    DISK_ERROR = "Current disk usage is above threshold({}GB): {}GB / {}GB. Only {}GB free"

    """
        Sets up the object.
    """
    def __init__(self):
        self.encoding = locale.getdefaultlocale()[1]

    """
        System reader main function to call the others.
    """
    def read_system(self):
        results = {}
        results["CPU"] = self.read_cpu()
        results["RAM"] = self.read_ram()
        results["TEMP"] = self.read_temp()
        results["DISK"] = self.read_disk_space()
        return results

    """
        Reads the 15 minute average cpu load
    """
    def read_cpu(self):
        output = subprocess.check_output(["/bin/cat", "/proc/loadavg"]).decode(self.encoding)
        load_avgs = output.split(" ")
        return load_avgs[2]

    """
        Reads the current ram usage.
    """
    def read_ram(self):
        output = subprocess.check_output(["/usr/bin/free", "-m"]).decode(self.encoding).split("\n")
        ram_usage = {}
        usage_line_data = list(filter(lambda x: x != '', output[1].split(" ")))
        ram_usage["total"] = usage_line_data[1]
        usage_line_data = list(filter(lambda x: x != '', output[2].split(" ")))
        ram_usage["used"] = usage_line_data[2]
        ram_usage["free"] = usage_line_data[3]
        return ram_usage

    """
        Reads the current temperature.
    """
    def read_temp(self):
        return subprocess.check_output(
            ["/usr/bin/awk", '{printf "%3.1f", $1/1000}', "/sys/class/thermal/thermal_zone0/temp"]).decode(
            self.encoding)

    """
        Reads the current disk space usage.
    """
    def read_disk_space(self):
        output = subprocess.check_output(["/bin/df", "-h"]).decode(self.encoding).split("\n")
        disk_usage = {}
        usage_line_data = list(filter(lambda x: x != '', output[1].split(" ")))
        disk_usage["total"] = usage_line_data[1][:-1]
        disk_usage["used"] = usage_line_data[2][:-1]
        disk_usage["free"] = usage_line_data[3][:-1]
        return disk_usage

    """
        Determines the thresholds and creates error messages.
    """
    def determine_thresholds(self, thresholds, system_stats):
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
                "username"] + '\nMIME-Version: 1.0\nContent-Type: text/html\nSubject: Raspberry Pi Server Warnings\n'
            email_message = header + "\n<h1>The following issues are occuring with the pi:</h1><br><br>\n"
            for message in messages:
                email_message += message + "<br><br>\n"
            self.send_mail(email_data, email_message)
        return False

    """
        Sends an email out.
    """
    def send_mail(self, client_data, message):
        try:
            server = smtplib.SMTP(client_data["host"], client_data["port"])
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(client_data["username"], client_data["password"])
            server.sendmail(client_data["sender"], client_data["recievers"], message)
            server.close()
        except smtplib.SMTPException as er:
            return False
        return True


epoch_milli = lambda: int(round(time.time() * 1000))

if len(sys.argv) > 1:
    new_pause_config = {"pause_until": int(sys.argv) * 1000 * 60}
    with open('pause.json', 'w') as fp:
        json.dump(new_pause_config, fp)
else:
    file_system_manager = FileSystemManager()
    config = file_system_manager.load_properties("config.json")
    pause_config = file_system_manager.load_pause_data("pause.json")
    system_reader = SystemReader()
    system_stats = system_reader.read_system()
    error_messages = system_reader.determine_thresholds(config["thresholds"], system_stats)
    print(error_messages)

    def alert(config):
        EmailManager().prepare_and_send_mail(config["email"], error_messages)

    if pause_config:
        if epoch_milli > int(pause_config["pause_until"]):
            alert(config)
    else:
        alert(config)
