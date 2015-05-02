import subprocess
import locale
from abc import ABCMeta, abstractmethod

class ProcessRunnerBase:
    """Base Class to run the process and gather output"""
    __metaclass__ = ABCMeta

    _ENCODING = locale.getdefaultlocale()[1]

    @abstractmethod
    def parse_output(self, output):
        """To Parse the resultant output"""
        pass

    @property
    def command(self):
        """To get the command which to run.

        Needs to be an list like: ['cat', 'filename.txt']
        """
        raise NotImplementedError

    def read_process(self):
        """Coordinates reading the process and parsing the result"""
        output = subprocess.check_output(self.command).decode(self._ENCODING)
        return self.parse_output(output)