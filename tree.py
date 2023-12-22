import regex as re
import copy

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
        a= Possibility(self.value + " " + b.value)
        return a

    def set_used(self):
        self.used = True

    def get_next(self):
        return self

class AndNode:
    def __init__(self):
        self.l = []
        self.r = []
        self.leftExhausted = False
        self.rightExhausted = False
        self.lNode = None
        self.rNode = None
        self.last = None
        
    def get_next(self):
        if not self.leftExhausted:
            if len(self.l) == 0 or self.l[-1].used:
                val = self.lNode.get_next()
                if len(self.l) == 0 or val.value != self.l[-1].value:
                    self.l.append(val)
                else:
                    self.leftExhausted = True
        if not self.rightExhausted:
            if len(self.r) == 0 or self.r[-1].used:
                val = self.rNode.get_next()
                if len(self.r) == 0 or val.value != self.r[-1].value:
                    self.r.append(val)
                else:
                    self.rightExhausted = True
        if self.last == None:
            self.last = self.l[-1].concat(self.r[-1])
            self.l[-1].set_used()
            self.r[-1].set_used()
            ret = copy.deepcopy(self.last)
            ret.used = False
            return ret
        res = None
        to_set = None
        if not self.l[-1].used:
            for r in self.r:
                if self.l[-1].length + r.length >= self.last.length:
                    to_set = self.l[-1]
                    if res == None:
                        res = self.l[-1].concat(r)
                    elif res.length > self.l[-1].length + r.length:
                        res = self.l[-1].concat(r)
        if not self.r[-1].used:
            for l in self.l:
                if l.length + self.r[-1].length >= self.last.length:
                    to_set = self.r[-1]
                    if res == None:
                        res = l.concat(self.r[-1])
                    elif res.length > l.length + self.r[-1].length:
                        res = l.concat(self.r[-1])
        if not res == None:
            to_set.set_used()
            ret = copy.deepcopy(res)
            ret.used = False
            return ret
        else:
            return copy.deepcopy(self.l[-1].concat(self.r[-1]))

class OrNode:
    def __init__(self):
        self.l = []
        self.r = []
        self.lNode = None
        self.rNode = None
        self.leftExhausted = False
        self.rightExhausted = False
        
    def get_next(self):
        if not self.leftExhausted:
            if len(self.l) == 0 or self.l[-1].used:
                val = self.lNode.get_next()
                if len(self.l) == 0 or val != self.l[-1]:
                    self.l.append(val)
                else:
                    self.leftExhausted = True
        if not self.rightExhausted:
            if len(self.r) == 0 or self.r[-1].used:
                val = self.rNode.get_next()
                if len(self.r) == 0 or val != self.r[-1]:
                    self.r.append(val)
                else:
                    self.rightExhausted = True
        if (not self.l[-1].used) and (not self.r[-1].used):
            if self.l[-1].length <= self.r[-1].length:
                self.l[-1].set_used()
                ret = copy.deepcopy(self.l[-1])
                ret.used = False
                return copy.deepcopy(self.l[-1])
            else:
                self.r[-1].set_used()
                ret = copy.deepcopy(self.r[-1])
                ret.used = False
                return ret
        elif not self.l[-1].used:
            self.l[-1].set_used()
            ret = copy.deepcopy(self.r[-1])
            ret.used = False
            return ret
        elif not self.r[-1].used:
            self.r[-1].set_used()
            ret = copy.deepcopy(self.r[-1])
            ret.used = False
            return ret
        else:
            if self.r[-1].length > self.l[-1].length:
                return copy.deepcopy(self.r[-1])
            else:
                return copy.deepcopy(self.l[-1])
            
#TODO
# def get_perm(possibilities, min, max, forbiden, curr):
#     if curr.length >= min and curr.length < max and curr.value not in forbiden:
#         return curr
#     for pos in possibilities:
        
#         if pos 

class CycleNode:
    def __init__(self):
        self.arr = []
        self.last = []
        self.value = None
        self.exhausted = False
    
    def get_next(self):
        if not self.exhausted:
            if self.arr[-1].used:
                val = self.value.get_next()
                if len(self.arr) == 0 or val != self.arr[-1]:
                    self.arr.append(val)
                else:
                    self.leftExhausted = True

        
        
        self.last.append(self.arr[-1])
        return copy.deepcopy(self.arr[-1])


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
        
def print_node(node, indent = 0):
    print()
    for i in range(indent):
        print("    ", end= "")
    if(isinstance(node, AndNode)):
        print("And node with: L:", end=' ')
        for le in node.l:
            print(le.value, end = ',')
            print(le.used, end=";")
        print(" and R:", end = ' ')
        for le in node.r:
            print(le.value, end = ',')
            print(le.used, end=";")
        print_node(node.lNode, indent +1)
        print_node(node.rNode, indent+1)
    if(isinstance(node, OrNode)):
        print("Or node with: L[-1]:", end=' ')
        print(node.l[-1].value, end = ',')
        print(node.l[-1].used, end = ";")
        print("and R[-1]:", end=' ')
        print(node.r[-1].value, end = ' ')
        print(node.r[-1].used, end = ";")
        print_node(node.lNode, indent+1)
        print_node(node.rNode, indent+1)
    if(isinstance(node, CycleNode)):
        print("cycle node with:", end=' ')
        print(node.arr[-1].value, end = ' ')
        print_node(node.value, indent+1)
    if(isinstance(node, Possibility)):
        print("Posibility node with value: " + node.value)

if __name__ == "__main__":
    one = re.Literal('1')
    two = re.Literal ('2')
    three = re.Literal ('3')
    four = re.Literal ('4 5')
    five = re.Literal ('6 7 8')
    rep = re.Alternation(two, five)
    con = re.Concatenation(one, rep)
    alt = re.Alternation(three, four)
    root = re.Concatenation(con, alt)
    struct = make_structure(root)
    next = struct.get_next()
    print_node(struct)
    print(next.value)
    next = struct.get_next()
    print_node(struct)
    print(next.value)
    next = struct.get_next()
    print_node(struct)
    print(next.value)
    next = struct.get_next()
    print_node(struct)
    print(next.value)
    next = struct.get_next()
    print_node(struct)
    print(next.value)