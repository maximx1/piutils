class Envelope:
    """Simple container for the transported message as a whole"""

    def __init__(self, mailman, sender, recipients, letter):
        """Initializes the object"""
        self.mailman = mailman
        self.sender = sender
        self.recipients = recipients
        self.letter = letter