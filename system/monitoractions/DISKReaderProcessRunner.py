from system.monitoractions.ProcessRunnerBase import ProcessRunnerBase

class DISKReaderProcessRunner(ProcessRunnerBase):
    """Impl of a DISK reading process runner

    Reads the current disk space usage
    """

    command = ["/bin/df", "-h"]

    def parse_output(self, raw_output):
        """To Parse the resultant output"""
        output = raw_output.split("\n")
        disk_usage = {}
        usage_line_data = list(filter(lambda x: x != '', output[1].split(" ")))
        disk_usage["total"] = usage_line_data[1][:-1]
        disk_usage["used"] = usage_line_data[2][:-1]
        disk_usage["free"] = usage_line_data[3][:-1]
        return disk_usage