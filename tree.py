import regex as re

def num_of_nodes(chain:str):
    if chain == '':
        return 0
    arr = chain.split(' ')
    return len(arr)

class Possibility:
    def __init__(self, val: str):
        self.value = val
        self.length = num_of_nodes(val)
        self.used = False

    def concat(self, b):
        self.value = self.value + " " + b.value
        self.length+= b.length
        return self

    def set_used(self):
        self.used = True

    def prepare(self):
        return self

class AndNode:
    def __init__(self):
        self.l = []
        self.r = []
        self.lNode = None
        self.rNode = None

    def prepare(self):
        leftPos = self.lNode.prepare()
        rightPos = self.rNode.prepare()
        self.l.append(leftPos)
        self.r.append(rightPos)
        return leftPos.concat(rightPos)
        

class OrNode:
    def __init__(self):
        self.arr = []
        self.last = None
        self.lNode = None
        self.rNode = None
    
    def prepare(self):
        leftPos = self.lNode.prepare()
        rightPos = self.rNode.prepare()
        if leftPos.length < rightPos.length:
            self.arr.append(leftPos)
            return leftPos
        else:
            self.arr.append(rightPos)
            return rightPos

class CycleNode:
    def __init__(self):
        self.arr = []
        self.last = None
        self.value = None

    def prepare(self):
        pos = self.value.prepare()
        self.arr.append(pos)
        return pos


def make_structure(regex):
    if isinstance(regex, re.Concatenation):
        node = AndNode()
        node.lNode = make_structure(regex.a)
        node.rNode = make_structure(regex.b)
        return node
    if isinstance(regex, re.Alternation):
        node = OrNode()
        node.lNode = make_structure(regex.a)
        node.rNode = make_structure(regex.b)
        return node
    if isinstance(regex, re.Repetition):
        node = CycleNode()
        node.value = make_structure(regex.value)
        return node
    if isinstance(regex, re.Literal):
        node = Possibility(regex.value)
        return node
    if isinstance(regex, str):
        return Possibility(regex)


class Tree:
    def __init__(self, regex):
        self.l = []
        self.r = []
        self.curr = None
        self.tree = make_structure(regex)

    def prepare(self):
        pos = self.tree.prepare()
        self.tree.l[0].set_used()
        print("prepared")

        

if __name__ == "__main__":
    one = re.Literal('1')
    two = re.Literal ('2')
    three = re.Literal ('3')
    four = re.Literal ('4 5')
    rep = re.Repetition(two, '+')
    con = re.Concatenation(one, rep)
    alt = re.Alternation(three, four)
    root = re.Concatenation(con, alt)

    tree = Tree(root)
    tree.prepare()
    print(tree.tree)