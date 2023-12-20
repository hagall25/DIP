import graphviz

#Literal class, basicaly string
class Literal:
    def __init__(self, value):
        if isinstance(value, Literal):
            self.value = value.value
        self.value = value

    def isEmpty(self):
        if len(self.value) == 0:
            return True
        else:
            return False
        
    def toString(self):
        return self.value
    
    def getPrefix(self):
        return self.value
    
    def getPosfix(self):
        return self.value

#Concatenation class     
class Concatenation:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def toString(self):
        a_str = None
        b_str = None
        if type(self.a) == str:
            a_str = self.a
        else:
            a_str = self.a.toString()
        if type(self.b) == str:
            b_str = self.b
        else:
            b_str = self.b.toString()
        return a_str + b_str
    
    def getPrefix(self):
        if isinstance(self.a, Literal) or isinstance(self.a, Concatenation):
            return self.a.getPrefix()
        
    def getPosfix(self):
        if isinstance(self.b, Literal) or isinstance(self.b, Concatenation):
            return self.b.getPosfix()

#Repetition class
# value* = 0 to n
# value? = 0 to 1
class Repetition:
    def __init__(self, value, opt = '*'):
        self.value = value
        self.opt = opt

    def toString(self):
        return "(" + self.value.toString() + ")" + self.opt
    
    def isOpt(self):
        if self.opt == '*':
            return False
        else:
            return True

#Alternation class
class Alternation:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def toString(self):
        a_str = None
        b_str = None
        if type(self.a) == str:
            a_str = self.a
        else:
            a_str = self.a.toString()
        if type(self.b) == str:
            b_str = self.b
        else:
            b_str = self.b.toString()
        return "(" + a_str +"+"+ b_str + ")"

#Unused
def print_regex(regex):
      if isinstance(regex, str):
          print(regex)
      elif isinstance(regex, Literal):
          print(regex.toString())
      elif isinstance(regex, Repetition):
          print_regex(regex.value)
      elif isinstance(regex, Concatenation) or isinstance(regex, Alternation):
          print_regex(regex.a)
          print_regex(regex.b)

#Removes given prefix from regex unused
def remove_prefix(regex, prefix):
    if isinstance(regex, Literal):
        if prefix == regex.value:
            return Literal('')
        else:
            return Literal(regex.value[len(prefix):])
    elif isinstance(regex, Concatenation):
        a = remove_prefix(regex.a, prefix)
        if isinstance(a, Literal) and a.isEmpty():
            return regex.b
        return Concatenation(a, regex.b)
    
#Removes given posfix from regex unused
def remove_posfix(regex, posfix):
    if isinstance(regex, Literal):
        if posfix == regex.value:
            return Literal('')
        else:
            return Literal(regex.value[:-len(posfix)])
    elif isinstance(regex, Concatenation):
        b = remove_posfix(regex.b, posfix)
        if isinstance(b, Literal) and b.isEmpty():
            return regex.a
        return Concatenation(regex.a, b)

#Gets literal prefix, unused
def get_common_prefix(a, b):
    a_str = None
    if isinstance(a, Literal) or isinstance(a, Concatenation):
        a_str = a.getPrefix()
    b_str = None
    if isinstance(b, Literal) or isinstance(b, Concatenation):
        b_str = b.getPrefix()
    if a_str == None or b_str == None:
        return None
    i = 0
    ret = ''
    for letter in a_str:
        if i < len(b_str):
            if letter == b_str[i]:
                ret += letter
                i+=1
            else:
                break
        
    if ret == '':
        return None
    else:
        a = remove_prefix(a, ret)
        b = remove_prefix(b, ret)
        return (a, b, ret)
    
#Are regexes a and b identical?
def is_identical(a, b):
    if (isinstance(a, Literal) and isinstance(b, Literal)) :
        return a.value == b.value
    elif(isinstance(a, str) and isinstance(b, str)):
        return a == b
    elif (isinstance(a, Repetition) and isinstance(b, Repetition)):
        return is_identical(a.value, b.value)
    elif (isinstance(a, Concatenation) and isinstance(b, Concatenation)) or (isinstance(a, Alternation) and isinstance(b, Alternation)):
        return is_identical(a.a, b.a) and is_identical(a.b,b.b)
    else:
        return False

#Returns deepest left/right node(leaf) of concatenation tree
def get_deepest(regex, side = "left"):
    if isinstance(regex, Literal) or isinstance(regex, Repetition) or isinstance(regex, Alternation) or isinstance(regex, str):
        if(isinstance(regex, str)):
            return Literal(regex)
        return regex
    else:
        if(side == "left"):
            return get_deepest(regex.a, side)
        else:
            return get_deepest(regex.b, side)

#Removes deepest left/right node(leaf) of concatenation tree   
def remove_deepest(regex, side = "left"):
    if isinstance(regex, Literal) or isinstance(regex, Repetition) or isinstance(regex, Alternation):
        return Literal('')
    else:
        if(side == "left"):
            if isinstance(regex.a, Literal) or isinstance(regex.a, Repetition) or isinstance(regex.a, Alternation):
                return regex.b
            else:
                return concat(remove_deepest(regex.a, side), regex.b)
        else:
            if isinstance(regex.b, Literal) or isinstance(regex.b, Repetition) or isinstance(regex.b, Alternation):
                return regex.a
            else:
                return concat(regex.a,remove_deepest(regex.b, side))

#For two regexes a,b in form of aa.x and bb.x returns (aa, bb, x)  
def get_posfix(a, b):
    deepest_a = get_deepest(a, "right")
    deepest_b = get_deepest(b, "right")
    ret = None
    if is_identical(deepest_a, deepest_b):
        a = remove_deepest(a, "right")
        b = remove_deepest(b, "right")
        (a, b, ret) = get_posfix(a, b)
        if ret != None:
            ret = Concatenation(ret, deepest_a)
        else:
            ret = deepest_a
    return (a,b,ret)

#For two regexes a,b in form of x.aa and x.bb returns (aa, bb, x)  
def get_prefix(a, b):
    deepest_a = get_deepest(a)
    deepest_b = get_deepest(b)
    # print("deepest a: " + deepest_a.toString())
    # print("deepest b: " + deepest_b.toString())
    ret = None
    if is_identical(deepest_a, deepest_b):
        a = remove_deepest(a)
        b = remove_deepest(b)
        (a, b, ret) = get_prefix(a, b)
        if ret != None:
            ret = Concatenation(deepest_a, ret)
        else:
            ret = deepest_a
    return (a,b,ret)
    

#unused
def get_common_posfix(a, b):
    a_str = None
    if isinstance(a, Literal) or isinstance(a, Concatenation):
        a_str = a.getPosfix()
    b_str = None
    if isinstance(b, Literal) or isinstance(b, Concatenation):
        b_str = b.getPosfix()
    if a_str == None or b_str == None:
        return None
    i = len(b_str)-1
    ret = ''
    rev_a = a_str[::-1]
    for letter in rev_a:
        if letter == b_str[i]:
            ret += letter
            i = i-1
        else:
            break
    i+=1
    if ret == '':
        return None
    else:
        a = remove_posfix(a, ret[::-1])
        b = remove_posfix(b, ret[::-1])
        return (a, b, ret[::-1])

#Simplify union 
def union(a, b):
    if a != None and b!= None and a!=b:
        
        # print("a : " + a.toString())
        # print("b : " + b.toString())
        (a,b,start) = get_prefix(a,b)
        (a,b,end) = get_posfix(a, b)   #Get common prefix and sufix

        if isinstance(a, Literal) and a.isEmpty() and isinstance(b, Literal) and b.isEmpty():  #a and b identical
            string = ''
            if start != None:
                string += start
            if end != None:
                string += end
            res = Literal(string)
        elif isinstance(a, Literal) and a.isEmpty():  #Whole a prefix or sufix of b
            if isinstance(b,Repetition) and not b.isOpt():
                res = b
            else:
                res =  Repetition(b, '?')
        elif isinstance(b, Literal) and b.isEmpty():  #Whole b prefix or sufix of a
            if isinstance(a,Repetition) and not a.isOpt():
                res = a
            else:
                res =  Repetition(a, '?')
            res = Repetition(a, '?')
        elif isinstance(a, Repetition) and a.isOpt:
            res = Repetition(union(a.value, b), '?')
        elif isinstance(b, Repetition) and b.isOpt:
            res = Repetition(union(a, b.value), '?')
        else:
            res = Alternation(a,b)
        
        if(start!= None):
            res = Concatenation(start, res)
        if(end != None):
            res = Concatenation(res, end)
        return res
    
    elif a == None:
        return b
    else:
        return a
    
#Simplify conacatenation
def concat(a, b):
    if a == None or b == None:
        return None
    if isinstance(a, Literal) and a.isEmpty():
        return b
    if isinstance(b, Literal) and b.isEmpty():
        return a
    
    if isinstance(get_deepest(a, "right"), Repetition): 
        if is_identical(get_deepest(a, "right").value, b):  #(xy)*xy -> xy*
            return a
    if isinstance(get_deepest(b), Repetition):   
        if is_identical(get_deepest(b).value, a):   #  xy(xy)* -> xy*
            return b
        
    if isinstance(b, Repetition) and isinstance(b.value, Alternation):  #(x+y)*y = (x+y)*
        if is_identical(b.value.a, a) or is_identical(b.value.b, a):
            return b
        
    if isinstance(a, Repetition) and isinstance(a.value, Alternation):
        if is_identical(a.value.a, b) or is_identical(a.value.b, b):
            return a

    if isinstance(a, Literal) and isinstance(b, Literal):
        return Literal(a.value+' '+b.value)
    if isinstance(a, Literal) and isinstance(b, Concatenation) and isinstance(b.a, Literal):
        return Concatenation(a.value+' '+b.a.value, b.b)
    if isinstance(b, Literal) and isinstance(a, Concatenation) and isinstance(a.b, Literal):
        return Concatenation(a.a, a.b.value+' '+b.value)
    return Concatenation(a, b)

#Repetition
def star(exp):
    if exp == None or (isinstance(exp, Literal) and exp.isEmpty()):
        return exp
    else:
        return Repetition(exp)
        

def add_nodes(dot, regex):
    global label
    if isinstance(regex, Literal):
        if regex.isEmpty():
            dot.node(str(label),'ε')
        else:
            dot.node(str(label),regex.toString())
    if isinstance(regex, str):
        dot.node(str(label),regex)
    if isinstance(regex, Repetition):
        if regex.isOpt:
            dot.node(str(label), '+')
        else:
            dot.node(str(label), '*')
        lab = label
        label +=1
        add_nodes(dot, regex.value)
        dot.edge(str(lab), str(lab+1))
    if isinstance(regex, Alternation):
        dot.node(str(label), 'OR')
        lab = label
        label +=1
        add_nodes(dot, regex.a)
        dot.edge(str(lab), str(lab+1))
        label +=1
        lab2 = label
        add_nodes(dot, regex.b)
        dot.edge(str(lab), str(lab2))
    if isinstance(regex, Concatenation):
        dot.node(str(label), 'AND')
        lab = label
        label +=1
        add_nodes(dot, regex.a)
        dot.edge(str(lab), str(lab+1))
        label +=1
        lab2 = label
        add_nodes(dot, regex.b)
        dot.edge(str(lab), str(lab2))

def substitude(regex):
    if isinstance(regex, Literal):
        return regex
    if isinstance(regex, str):
        return Literal(regex)
    if isinstance(regex, Alternation):
        return Alternation(substitude(regex.a), substitude(regex.b))
    if isinstance(regex, Concatenation):
        return Concatenation(substitude(regex.a), substitude(regex.b))
    if isinstance(regex, Repetition):
        return Alternation(Literal(''), Repetition(substitude(regex.value), '+'))

def visualize(regex):
    global label
    label = 0
    dot = graphviz.Digraph('alg', comment='regex viz')
    add_nodes(dot, regex)
    dot.render()
    #print(dot.source)

if __name__ == "__main__":
    one = Literal('1')
    two = Literal ('2')
    three = Literal ('3')
    four = Literal ('4 5')
    rep = Repetition(two, '+')
    con = Concatenation(one, rep)
    alt = Alternation(three, four)
    root = Concatenation(con, alt)
    visualize(root)