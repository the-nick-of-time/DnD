class Intermediary:
    """Handles the passing of data between the GUI and runtime."""
    def __init__(self):
        pass


class Packet:
    def __init__(self, path, data, operation):
        self.path = path
        self.data = data
        self.operation = operation
