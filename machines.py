
class Machines:
    def __init__(self, id=None, toolNum=None, toolLife=None, initial=None):
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

        
    def __str__(self):
        return f"Machine: ID={self.id}, ToolNum={self.toolNum}, ToolLife={self.toolLife}, Initial={self.initial}"    