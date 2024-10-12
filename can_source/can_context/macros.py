class CanMacrosContext:
    """
    A class to hold macros in `compile-time`
    """

    def __init__(self):
        self.macros = {}

    def update(self, name, o):
        self.macros.update({name: o})

    def get(self, name):
        return self.macros.get(name)
