import sys
import regex as re
import copy

MAX = 1000000000

MODE = 1
CFG = None

def set_cfg(cfg):
    global CFG
    CFG = cfg

def get_node_len(node_name):
    if MODE == 1:
        return 1
    if MODE == 2 and CFG != None:
        l = CFG.get_node_length(node_name)
        if l == 0:
            return 1
        else:
            return l
    else:
        return 1
def compute_length(chain:str):
    if chain == '':
        return 0
    arr = chain.split(' ')
    res = 0
    for node_name in arr:
        res += get_node_len(node_name)
    return res

def num_of_nodes(chain:str):
    if chain == '':
        return 0
    arr = chain.split(' ')
    return len(arr)

class Possibility:
    def __init__(self, val: str):
        self.value = val
        self.length = compute_length(val)
        self.used = False

    def concat(self, b):
        if self.value == '' or b.value == '':
            a = Possibility(self.value + b.value)
        else :
            a = Possibility(self.value + " " + b.value)
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
        self.queue = []
        self.secondary = []
        
    def get_next(self):
        if len(self.queue) > 0:
            front = self.queue.pop(0)
            self.last = front
            ret = copy.deepcopy(front)
            ret.used = False
            return ret
        if not self.leftExhausted:
            if len(self.l) == 0 or self.l[-1].used:
                val = self.lNode.get_next()
                if len(self.l) == 0 or val.value not in [x.value for x in self.l]:
                    self.l.append(val)
                else:
                    self.leftExhausted = True
        if not self.rightExhausted:
            if len(self.r) == 0 or self.r[-1].used:
                val = self.rNode.get_next()
                if len(self.r) == 0 or val.value not in [x.value for x in self.r]:
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
        
        if not self.l[-1].used:
            if self.r[-1].used:
                rcopy = self.r
            else:
                rcopy = self.r[:-1]
            for r in rcopy:
                if self.l[-1].length + r.length >= self.last.length:
                    self.secondary.append(self.l[-1].concat(r))
        if not self.r[-1].used:
            for l in self.l:
                if l.length + self.r[-1].length >= self.last.length:
                    self.secondary.append(l.concat(self.r[-1]))
        if not self.secondary == []:
            to_pop = 0
            l = -1
            for elem in sorted(self.secondary, key=lambda x: x.length):
                if l == -1 or elem.length == l:
                    l = elem.length
                    to_pop += 1
                    self.queue.append(elem)
                else:
                    break
            self.secondary = sorted(self.secondary, key=lambda x: x.length)
            for i in range(to_pop):
                self.secondary.pop(0)
            self.l[-1].set_used()
            self.r[-1].set_used()
            front = self.queue.pop(0)
            self.last = front
            ret = copy.deepcopy(front)
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
                if len(self.l) == 0 or val.value not in [x.value for x in self.l]:
                    self.l.append(val)
                else:
                    self.leftExhausted = True
        if not self.rightExhausted:
            if len(self.r) == 0 or self.r[-1].used:
                val = self.rNode.get_next()
                if len(self.r) == 0 or val.value not in [x.value for x in self.r]:
                    self.r.append(val)
                else:
                    self.rightExhausted = True
        if (not self.l[-1].used) and (not self.r[-1].used):
            if self.l[-1].length <= self.r[-1].length:
                self.l[-1].set_used()
                ret = copy.deepcopy(self.l[-1])
                ret.used = False
                return ret
            else:
                self.r[-1].set_used()
                ret = copy.deepcopy(self.r[-1])
                ret.used = False
                return ret
        elif not self.l[-1].used:
            self.l[-1].set_used()
            ret = copy.deepcopy(self.l[-1])
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
            

def get_perm(possibilities, min, max, forbiden, curr = Possibility('')):
    forbiden_values = []
    for elem in forbiden:
        forbiden_values.append(elem.value)
    if curr.length >= min and curr.length < max and curr.value not in forbiden_values:
        return curr
    elif curr.length >= max:
        return None
    next = None
    for pos in possibilities:
        temp = get_perm(possibilities, min, max,forbiden ,curr.concat(pos))
        if next == None:
            next = temp
        elif temp == None:
            pass
        elif next.length > temp.length:
            next = temp
    return next

class CycleNode:
    def __init__(self):
        self.arr = []
        self.last = []
        self.value = None
        self.exhausted = False
    
    def get_next(self):
        if not self.exhausted:
            if len(self.arr) == 0 or self.arr[-1].used:
                val = self.value.get_next()
                if len(self.arr) == 0 or val.value not in [x.value for x in self.arr]:
                    self.arr.append(val)
                else:
                    self.exhausted = True
        max = sys.maxsize
        if not self.arr[-1].used:
            if not self.exhausted:
                max = self.arr[-1].length
        min = 1
        if len(self.last)>0:
            min = self.last[-1].length
        if self.arr[-1].used:
            a = get_perm(self.arr, min, max, self.last)
        else:
            a = get_perm(self.arr[:-1], min, max, self.last)
        if a == None:            
            self.last.append(self.arr[-1])
            self.arr[-1].used = True
        else:
            self.last.append(a)
        ret = copy.deepcopy(self.last[-1])
        ret.used = False
        return ret


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
    rep = re.Repetition(two, '+')
    con = re.Concatenation(one, rep)
    alt = re.Alternation(three, four)
    root = re.Concatenation(con, alt)
    struct = make_structure(root)
    for i in range(30):
        next = struct.get_next()
        print(next.value)
    # next = struct.get_next()
    # print(next.value)
    # next = struct.get_next()
    # print(next.value)
    # next = struct.get_next()
    # print(next.value)
    # next = struct.get_next()
    # print(next.value)