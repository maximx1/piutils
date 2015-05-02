class MailMan:
    """Simple container for the email server"""

    def __init__(self, host, port, username, password):
        """Initializes the object"""
        self.host = host
        self.port = port
        self.username = username
        self.password = password