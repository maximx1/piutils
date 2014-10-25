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

config = FileSystemManager().loadProperties("config.json")
print(SystemReader().readRam())
