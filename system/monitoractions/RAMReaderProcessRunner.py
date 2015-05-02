from system.monitoractions.ProcessRunnerBase import ProcessRunnerBase

class RAMReaderProcessRunner(ProcessRunnerBase):
    """Impl of a RAM reading process runner

    Reads the current ram usage
    """

    command = ["/usr/bin/free", "-m"]

    def parse_output(self, raw_output):
        """To Parse the resultant output"""
        output = raw_output.split("\n")
        ram_usage = {}
        usage_line_data = list(filter(lambda x: x != '', output[1].split(" ")))
        ram_usage["total"] = usage_line_data[1]
        usage_line_data = list(filter(lambda x: x != '', output[2].split(" ")))
        ram_usage["used"] = usage_line_data[2]
        ram_usage["free"] = usage_line_data[3]
        return ram_usage
