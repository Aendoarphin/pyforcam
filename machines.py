
class Machines:
    def __init__(self, id=None, toolNum=None, toolLife=None, initial=None, machine_name=None):
        if id is not None:
            self.id = id
        else:
            self.id = None

        if toolNum is not None:
            self.toolNum = toolNum
        else:
            self.toolNum = []

        if toolLife is not None:
            self.toolLife = toolLife
        else:
            self.toolLife = []

        if initial is not None:
            self.initial = initial
        else:
            self.initial = []
        if machine_name is not None:
            self.machine_name = machine_name
        else:
            self.machine_name = "NULL"
          