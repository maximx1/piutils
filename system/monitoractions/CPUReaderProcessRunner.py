from system.monitoractions.ProcessRunnerBase import ProcessRunnerBase

class CPUReaderProcessRunner(ProcessRunnerBase):
    """Impl of a CPU reading process runner

    Reads the 15 minute average cpu load
    """

    command = ["/bin/cat", "/proc/loadavg"]

    def parse_output(self, output):
        """To Parse the resultant output"""
        load_avgs = output.split(" ")
        return load_avgs[2]