"""Copyright 2019-2023 Kai D. Gonzalez"""

# contains the psi ECI (Extensive-Command-Interface)
# each python-based extension implements their own ECI, which is then read into
# PSI's global ECI storage.
# this system is an effective way to implement and manage a large number of plugins.

class PsiECI:
    """
    a psi extensive command interface contains a list of command names bound to
    functions, to easily be located in the main bot file
    """
    cmds: dict

    def __init__(self):
        """
        initialize the ECI
        """
        self.cmds = {}

    def add(self, cmdName: str, func):
        """
        add a command to the ECI
        """
        self.cmds[cmdName] = func

    def get(self, cmdName: str):
        return self.cmds[cmdName]

class PsiECIStorage:
    """
    a global psi eci (extensive command interface) storage
    """
    global_eci: list

    def __init__(self):
        self.global_eci = []

    def add(self, eci: PsiECI):
        """
        add an eci to the global eci list
        """
        self.global_eci.append( eci )
