
class Machines:
    def __init__(self, address:int, toolNum:list, toolLife:list, initial:list):
        self.address = address
        self.toolNum = toolNum
        self.toolLife = toolLife
        self.initial = initial
    
    def __str__(self):
        return f"Machine: Address={self.address}, ToolNum={self.toolNum}, ToolLife={self.toolLife}, Initial={self.initial}"      