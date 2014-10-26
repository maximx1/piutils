#!/usr/bin/python

"""
	Author: Justin Walrath (walrathjaw@gmail.com)
	Description: 
		System script that will read the system information in order to keep track of things like 
		temperature, disk space, cpu load, and ram for the raspberry pi and submit an email alert.
"""

import json
import subprocess

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
	Main utility to read the system information.
"""
class SystemReader:
	"""
		System reader main function to call the others.
	"""
	def readSystem(self):
		results = {}
		results["CPU"] = self.readCPU()
		results["RAM"] = self.readRam()
		results["TEMP"] = self.readTemp()
		results["DISK"] = self.readDiskSpace()
		return results

	"""
		Reads the 15 minute average cpu load
	"""
	def readCPU(self):
		output = subprocess.check_output(["/bin/cat", "/proc/loadavg"])
		loadavgs = output.split(" ")
		return loadavgs[2]

	"""
		Reads the current ram usage.
	"""
	def readRam(self):
		output = subprocess.check_output(["/usr/bin/free", "-m"]).split("\n")
		ramUsage = {}
		usageLineData = filter(lambda x: x != '', output[1].split(" "))
		ramUsage["total"] = usageLineData[1]
		usageLineData = filter(lambda x: x != '', output[2].split(" "))
		ramUsage["used"] = usageLineData[2]
		ramUsage["free"] = usageLineData[3]
		return ramUsage

	"""
		Reads the current temperature.
	"""
	def readTemp(self):
		 return subprocess.check_output(["/bin/awk", '{printf "%3.1f", $1/1000}', "/sys/class/thermal/thermal_zone0/temp"])

	"""
		Reads the current disk space usage.
	"""
	def readDiskSpace(self):
		output = subprocess.check_output(["/bin/df", "-h"]).split("\n")
		diskUsage = {}
		usageLineData = filter(lambda x: x != '', output[1].split(" "))
		diskUsage["total"] = usageLineData[1][:-1]
		diskUsage["used"] = usageLineData[2][:-1]
		diskUsage["free"] = usageLineData[3][:-1]	
		return diskUsage

	"""
		Determines the thresholds and creates error messages.
	"""
	def determineThresholds(self, thresholds, systemStats):
		errorMessages = []
		if float(systemStats["CPU"]) >= float(thresholds["cpu"]):
			errorMessages.append("CPU average over the last 15 minutes has met the threshold(" + str(thresholds["cpu"]) + "%): " + str(systemStats["CPU"]) + "%")
		if float(systemStats["RAM"]["used"]) >=float( thresholds["ram"]):
			errorMessages.append("Current ram usage is above threshold(" + str(thresholds["ram"]) + "MB): " + str(systemStats["RAM"]["used"]) + "MB / " + str(systemStats["RAM"]["total"]) + "MB. Only " + str(systemStats["RAM"]["free"]) + "MB free")
		if float(systemStats["TEMP"]) >= float(thresholds["temp"]):
			errorMessages.append("Temperature is over threshold(" + str(thresholds["temp"]) + "C): " + str(systemStats["TEMP"]) + "C")
		if float(systemStats["DISK"]["used"]) >= float(thresholds["disk"]):
			errorMessages.append("Current disk usage is above threshold(" + str(thresholds["disk"]) + "GB): " + str(systemStats["DISK"]["used"]) + "GB / " + str(systemStats["DISK"]["total"]) + "GB. Only " + str(systemStats["DISK"]["free"]) + "GB free")
		return errorMessages

config = FileSystemManager().loadProperties("config.json")
systemReader = SystemReader()
systemStats = systemReader.readSystem()
print(systemReader.determineThresholds(config["thresholds"], systemStats))
