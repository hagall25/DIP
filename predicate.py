class LogicalAnd:
    def __init__(self, left, right):
        self.l = left
        self.r = right

class LogicalOr:
    def __init__(self, left, right):
        self.l = left
        self.r = right

class LogicalNot:
    def __init__(self, op):
        self.op = op