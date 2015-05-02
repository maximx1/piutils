from system.monitoractions.ProcessRunnerBase import ProcessRunnerBase

class TEMPReaderProcessRunner(ProcessRunnerBase):
    """Impl of a TEMP reading process runner

    Reads the current temperature
    """

    command = ["/usr/bin/awk", '{printf "%3.1f", $1/1000}', "/sys/class/thermal/thermal_zone0/temp"]

    def parse_output(self, output):
        """To Parse the resultant output"""
        return output