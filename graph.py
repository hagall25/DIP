import json
from z3 import *
import parse
import copy
import networkx as nx
from typing import Type

pprint = True

#Is exactly subpath in this order included in path?
def is_subpath(path, subpath):
    i = 0
    for node in path:
        if (node == subpath[i]):
            i+=1
            if i == len(subpath):
                return True
        else:
            i = 0
            if (node == subpath[i]):
                i+=1
    return False

#Is subpath in any order included in path?
def is_included(path, subpath):
    for node in path:
        if node == subpath[0]:
            subpath.pop(0)
        if subpath == []:
            return True

    return False

def make_tuple(node_list):
        name_list = []
        for node in node_list:
            name_list.append(node.name)
        return tuple(name_list)

class Literal:
    def __init__(self, value):
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
        return Concatenation(remove_prefix(regex.a, prefix), regex.b)
    
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
        return Concatenation(regex.a, remove_posfix(regex.b, posfix))

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


def union(a, b):
    if a != None and b!= None and a!=b:
        print("a : " + a.toString())
        print("b : " + b.toString())
        starta = None
        endb = None
        res = None
        resa = get_common_prefix(a, b)
        if resa != None:
            (ap, bp , start) = resa
            a = ap
            b = bp
            starta = start
        resb = get_common_posfix(a, b)
        if resb != None:
            (ap, bp , end) = resb
            a = ap
            b = bp
            endb = end

        if isinstance(a, Literal) and a.isEmpty() and isinstance(b, Literal) and b.isEmpty():
            string = ''
            if starta != None:
                string += start
            if endb != None:
                string += end
            res = Literal(string)
        elif isinstance(a, Literal) and a.isEmpty():
            res =  Repetition(b, '?')
        elif isinstance(b, Literal) and b.isEmpty():
            res = Repetition(a, '?')
        elif isinstance(a, Repetition) and a.isOpt:
            res = Repetition(Alternation(a.value, b), '?')
        elif isinstance(b, Repetition) and b.isOpt:
            res = Repetition(Alternation(a, b.value), '?')
        else:
            res = Alternation(a,b)
        
        if(starta!= None):
            res = Concatenation(Literal(start), res)
        if(endb != None):
            res = Concatenation(res, Literal(endb))
        print("res : " + res.toString())
        return res
    
    elif a == None:
        return b
    else:
        return a
    #     res = get_common_posfix(a, b)
    #     if res!=None:
    #         (ap, bp , end) = res
    #         if isinstance(ap, Literal) and ap.isEmpty():
    #             return Concatenation(Repetition(bp, '?'), Literal(end))
    #         if isinstance(bp, Literal) and bp.isEmpty():
    #             return Concatenation(Repetition(ap, '?'), Literal(end))
    #         if isinstance(ap, Repetition) and ap.isOpt:
    #             return Concatenation(Repetition(Alternation(ap.value, bp), '?'), Literal(end))
    #         if isinstance(bp, Repetition) and bp.isOpt:
    #             return Concatenation(Repetition(Alternation(ap, bp.value), '?'), Literal(end))
    #         return Concatenation(Alternation(ap,bp),Literal(end))
    #     return Alternation(a, b)
    
    
def concat(a, b):
    if a == None or b == None:
        return None
    if isinstance(a, Literal) and a.isEmpty():
        return b
    if isinstance(b, Literal) and b.isEmpty():
        return a
    
    if isinstance(a, Literal) and isinstance(b, Literal):
        return Literal(a.value+b.value)
    if isinstance(a, Literal) and isinstance(b, Concatenation) and isinstance(b.a, Literal):
        return Concatenation(a.value+b.a.value, b.b)
    if isinstance(b, Literal) and isinstance(a, Concatenation) and isinstance(a.b, Literal):
        return Concatenation(a.a, a.b.value+b.value)
    return Concatenation(a, b)

def star(exp):
    if exp == None or (isinstance(exp, Literal) and exp.isEmpty()):
        return exp
    else:
        return Repetition(exp)
        

#Node class
#Parameters:
#name is for id of node
#initial if node is initial node
#terinal if node is terminal
#succs is set of successors
class Node:
    def __init__(self, name):
        self.name = name
        self.initial = False
        self.terminal = False
        self.succs = set()
        self.transition_label = {}

    def remove_succ(self, node_name):
        self.succs.remove(node_name)
        self.transition_label.pop(node_name)
    
    def add_succ(self, node):
        self.succs.add(node)
        self.transition_label[node] = node

    def set_initial(self):
        self.initial = True
    
    def set_terminal(self):
        self.terminal = True

#Control flow graph class
#Parameters:
#nodes is set of nodes in graph
#targets is list of nodes/subpaths defined by coverage criterion, that should be included in test paths
#conditions is dict storing pairs edge:condition
#actions is dict storing pairs node:assignment
#parameters is dict storing pairs id:type(id) for func parameters
#symbols is dict updating values of variables updated by assignments
class CFG:
    def __init__(self, nodes = None) -> None:
        if nodes != None:
            self.nodes = set(nodes)
        self.nodes = set()
        self.targets = []
        self.conditions = {}
        self.actions = []
        self.parameters = {}
        self.symbols = {}
    
    def add_node(self, node):
        self.nodes.add(node)

    def print_graph(self):
        for node in self.nodes:
            if node.initial:
                print("Intial node:")
            if node.terminal:
                print("Terminal node:")
            print(node.name)
            if len(node.succs) != 0:
                print("Successors:")
                for succ in node.succs:
                    print(succ)
            print()

    def get_predecessors(self, graph, target):
        predecessors = []
        for node in graph.nodes:
            for succ in node.succs:
                if succ == target.name:
                    predecessors.append(node.name)
        return predecessors
    
    def path_regex(self, p:Node, q:Node, k:Node):
        path_regex = ""
        if q.name in p.succs:
            path_regex = "(" + p.transition_label[q.name] + ")" + "+" + "("
        if k.name in p.succs:
            path_regex += (p.transition_label[k.name] + " ")
        if(k.name in k.succs):
            path_regex += ("(" + k.transition_label[k.name] + ")*")
        if q.name in k.succs:
            path_regex += (" " + k.transition_label[q.name])
        if q.name in p.succs:
            path_regex+=")"
        return path_regex
    
    def get_regex(self):
        graph = copy.deepcopy(self)
        while len(graph.nodes) > 2:
            for node in graph.nodes:
                if not node.initial and not node.terminal:
                    node_copy = copy.deepcopy(node)
                    preds = self.get_predecessors(graph, node)
                    node_succs = copy.deepcopy(node_copy.succs)
                    for pre in preds:
                        if pre != node.name:
                            for succ in node_succs:
                                pred = graph.get_node(pre)
                                path_reg = self.path_regex(pred, graph.get_node(succ), node_copy)
                                pred.add_succ(succ)
                                pred.transition_label[succ] = path_reg
                            pred.remove_succ(node_copy.name)
                    graph.nodes.remove(node)
                    break
        for node in graph.nodes:
            print()
            print(node.name + " ")
            print(node.transition_label)
            
    def brzozowski(self):
        b = {}
        a = {}
        for node in self.nodes:
            if node.terminal:
                b[node.name] = Literal('')
            else:
                b[node.name] = None
            for bnode in self.nodes:
                a[(node.name, bnode.name)] = None
            for succ in node.succs:
                a[(node.name, succ)] = Literal(succ)
        nodesList = []
        nodesList.append(self.get_init_node())
        for node in self.nodes:
            if not node.initial and not node.terminal:
                nodesList.append(node)
        nodesList.append(self.get_term_node())
        for n in range(len(nodesList)-1,-1,-1):
            node = nodesList[n]
            if a[(node.name, node.name)] != None:
                b[node.name] = concat(star(a[(node.name, node.name)]), b[node.name])
                for j in range(0, n):
                    jnode = nodesList[j]
                    a[(node.name, jnode.name)] = concat(star(a[(node.name, node.name)]), a[(node.name, jnode.name)])
            
            for i in range(0, n):
                inode = nodesList[i]
                if a[(inode.name, node.name)] != None:
                    b[inode.name] = union(b[inode.name], concat(a[(inode.name, node.name)], b[node.name]))
                    for j in range(0, n):
                        jnode = nodesList[j]
                        a[(inode.name, jnode.name)] = union(a[(inode.name, jnode.name)], concat(a[(inode.name, node.name)], a[(node.name, jnode.name)]))
        print(b[self.get_init_node().name].toString())
        #print_regex(b[self.get_init_node().name])
        return b[self.get_init_node().name]
                    

    #load cfg from input json
    def load_from_json(self, json_file):
        with open(json_file, "r") as read_file:
            data = json.load(read_file)
            if data["parameters"]!=None:
                for parameter in data["parameters"]:
                    id = parameter["id"]
                    type = parameter["type"]
                    if type == "Int":
                        self.parameters[id] = Int(id)
            if data["nodes"] != None:
                for node in data["nodes"]:
                    newNode = Node(node["name"])
                    if "succs" in node:
                        for succ in node["succs"]:
                            newNode.add_succ(succ["name"])
                            if succ.get("condition")!=None:
                                self.conditions[(node["name"], succ["name"])] = succ["condition"]
                    if node["name"] == data["initial_node"]:
                        newNode.set_initial()
                    if node["name"] in data["terminal_nodes"]:
                        newNode.set_terminal()
                    if node.get("actions") != None:
                        for action in node["actions"]:
                            self.actions.append((node["name"],action))
                    self.add_node(newNode)

    def get_init_node(self):
        for node in self.nodes:
            if node.initial:
                return node
            
    def get_term_node(self):
        for node in self.nodes:
            if node.terminal:
                return node
    
    def get_node(self, name):
        for node in self.nodes:
            if name == node.name:
                return node
                    
    #Gives shortest path between start node and end_node prforming BFS algorithm
    def BFS(self, start_node, end_node):
        queue = []
        queue.append((start_node,[start_node]))
        visited = []
        visited.append(start_node)
        while queue:
            node = queue.pop(0)
            if node[0] == end_node:
                return node[1]
            for succ_name in node[0].succs:
                succ = self.get_node(succ_name)
                if succ not in visited:
                    new_path = node[1].copy()
                    new_path.append(succ)
                    queue.append((succ,new_path))
                    visited.append(node[0])
        return None

    def reachable(self, start_node, end_node):
        if self.BFS(start_node, end_node) == None:
            return False
        else:
            return True

    #Returns prime paths
    def create_prime_paths(self):
        simple = []
        prime = []
        res = []
        for node in self.nodes:
            simple.append([node.name])
        while len(simple) > 0:
            path = simple.pop(0)
            if len(path) > 1 and path[0] == path[-1]:
                prime.append(path)
            if self.get_node(path[-1]).terminal:
                prime.append(path)
                continue
            added = False
            for succ in self.get_node(path[-1]).succs:
                if succ in path:
                    if path[0] == succ:
                        newPath = path.copy()
                        newPath.append(succ)
                        prime.append(newPath)
                        added = True
                else:
                    newPath = path.copy()
                    newPath.append(succ)
                    simple.append(newPath)
                    added = True
            if not added:
                prime.append(path)
        while prime != []:
            path = prime.pop(-1)
            res.append(path)
            to_remove = []
            for subpath in prime:
                if is_subpath(path, subpath):
                    to_remove.append(subpath)
            for subpath in to_remove:
                prime.remove(subpath)
        return res

    #Fills targets with subpaths given by CC
    def get_targets(self, cc = "NC"):
        if cc == "NC":
            if pprint:
                print("Using Node Coverage criterion")
            for node in self.nodes:
                self.targets.append(node)
        if cc == "EC":
            if pprint:
                print("Using Edge Coverage criterion")
            for node in self.nodes:
                for succ in node.succs:
                    self.targets.append([node, self.get_node(succ)])
        if cc == "PPC":
            paths = self.create_prime_paths()
            if pprint:
                print("Using Prime Path criterion")
                print(paths)
            for path in paths:
                newPath = []
                for name in path:
                    newPath.append(self.get_node(name))
                self.targets.append(newPath)

    #Finds path from initial node to first node in targets subpath
    #and from last node in targets subpath and terminal node and concatenates those parts into one path.
    #Removes all subpaths from targets covered by this path.
    #Gives one path to test for input
    def short_paths(self):
        ts = []
        while len(self.targets) > 0:
            t = list(self.targets[0]).copy()
            p1 = self.BFS(self.get_init_node(), t[0])
            p2 = self.BFS(t[-1], self.get_term_node())
            test_case = p1 + list(t)[1:-1] + p2
            ts.append(test_case)
            to_remove = []
            for subpath in self.targets:
                if is_subpath(test_case, subpath):
                    to_remove.append(subpath)
                    #self.targets.remove(subpath)
            for subpath in to_remove:
                self.targets.remove(subpath)
        return ts

    #Method for finding feasible paths with parameter max_iterations
    #which determines how many same decisions can it take.
    def bruteforce(self, max_iterations, max_repetition):
        target = self.targets.pop(0)    #Get target subpath for which feasible path is about to be found.
        if(pprint):
            print("Target is: ")
            for node in target:
                print(node.name, end= " ")
            print()
        start_node = self.get_init_node()
        found = False
        curr_decision = None
        checked = []
        decisions = {} #  {path : {succ : counter}} - dictionary for remembering number of took decisions
        number_of_takes = {}  # {node : {succ:counter}}
        for node in self.nodes:
            if len(node.succs) > 1:
                number_of_takes[node] = {}
                for succ in node.succs:
                    number_of_takes[node][succ] = 0
        curr_path = [start_node]
        curr_target = target.copy()
        while not found:
            if curr_target != []:       # If target node is reached, remove it from list
                if curr_target[0] == curr_path[-1]:
                    curr_target.pop(0)
            if curr_path[-1] == self.get_term_node() and curr_target == []: #If I reached terminal node and target is fullfiled
                formula = self.get_formula(curr_path)                       #Create formula and check feasibility
                res = self.solve_formula(formula)
                if res == 'sat':                                            #If feasible, return success
                    print(formula)
                    print("res is:", end = " ")
                    for node in curr_path:
                        print(node.name, end= " ")
                    print()
                    targets_copy = self.targets.copy()
                    for target_path in targets_copy:                        #Remove every subpath from target list
                        target_path_copy = target_path.copy()
                        if is_included(curr_path, target_path_copy):
                            self.targets.remove(target_path)
                    return True
                else:                                                       #Else if path is unfeasible
                    if pprint:
                        #print(formula)
                        print("for path: ", end = " ")
                        for node in curr_path:
                            print(node.name, end= " ")
                        print()
                    if curr_path in checked:                                #If I already checked this exact line
                        decisions[curr_decision[0]][curr_decision[1]] = max_iterations   #block the last decision I did
                    else:
                        checked.append(curr_path)                           #Else remember I failed here
                    curr_path = [start_node]                                #And start again
                    curr_target = target.copy()
                    curr_decision = None
                    continue
                                                                            #Starting to build path
            if len(curr_path[-1].succs) == 1:                               #If just one successor, automatically add it
                curr_path.append(self.get_node(tuple(curr_path[-1].succs)[0]))
            else:                                                           #Decision here
                min_count = max_iterations+1
                num_of_possibilities = 0
                if not make_tuple(curr_path) in decisions:                  #If I never saw this decision, remember it
                    decisions[make_tuple(curr_path)] = {}
                    for succ_name in curr_path[-1].succs:
                        if curr_target ==[] or self.reachable(self.get_node(succ_name), curr_target[0]):
                            decisions[make_tuple(curr_path)][succ_name] = 0
                            
                curr_node = None
                takes = float('inf')
                for node_name in decisions[make_tuple(curr_path)]:          #Iterate through all possible decisions and pick one with 
                    num_of_possibilities += 1                               #smallest number of visits
                    count = decisions[make_tuple(curr_path)][node_name]
                    if count <= min_count and count < max_iterations and curr_path.count(self.get_node(node_name)) < max_repetition:
                        if count == min_count:
                            if number_of_takes[curr_path[-1]][node_name] < takes:
                                min_count = count
                                curr_node = node_name
                                takes = number_of_takes[curr_path[-1]][node_name]
                        else:
                            min_count = count
                            curr_node = node_name
                            takes = number_of_takes[curr_path[-1]][node_name]
                if curr_node == None: 
                    to_continue = False
                    for val in decisions[make_tuple(curr_path)].values():
                        if val != max_iterations:
                            curr_path = [start_node]                                #And start again
                            curr_target = target.copy()
                            curr_decision = None
                            to_continue = True
                    if not to_continue:
                        if pprint:
                            print("Not found")
                        return False
                    else:
                        continue
                if num_of_possibilities > 1:                                #If just one option keeps possibility of reaching target,
                    curr_decision = (make_tuple(curr_path), curr_node)      # dont count it as decision
                    decisions[make_tuple(curr_path)][curr_node] += 1
                    number_of_takes[curr_path[-1]][curr_node] += 1
                curr_path.append(self.get_node(curr_node))


    def cycle_paths(self, max_iterations):
        #target = self.targets.pop(0)
        g =  nx.DiGraph()
        for node in self.nodes:
            g.add_node(node.name)
        for node in self.nodes:
            for succ in node.succs:
                g.add_edge(node.name, succ)
        cycles = list(nx.simple_cycles(g))
        print(cycles)
        return
        curr_path = [self.get_init_node()]
        curr_node = curr_path[-1]
        curr_target = target.copy()
        while True:
            if curr_target != [] and curr_node == curr_target[0]:
                curr_target.pop(0)
            if curr_target == [] and curr_node == self.get_term_node:
                for node in curr_path:
                    for cycle in cycles:
                        pass

    #From given path makes formula to check by Z3
    #For assignments update variables with values in symbols and update values in symbols.
    #For conditions update variables with values in symbols and add to formula
    def get_formula(self, path):
        formula = ""
        first = True
        for i in range(len(path)-1):
            for node, action in self.actions:
                if node == path[i].name:
                    expr, self.symbols = parse.parse(action, self.symbols)
                    #print(expr)
            edge = (path[i].name, path[i+1].name)
            if edge in self.conditions.keys():
                if not first:
                    formula += ", "
                expr, sym = parse.parse(self.conditions[edge], self.symbols)
                formula += expr
                first = False
        self.symbols.clear()
        return formula
    
    #Calls Z3 solve method
    def solve_formula(self, formula):
        for key in self.parameters:
            locals()[key] = self.parameters[key]
        f = eval(formula)
        s = Solver()
        s.add(f)
        sat = s.check()
        #print(sat)
        solve(f)
        return sat.__str__()

    #Loads CFG, list of targets, find paths, make formule and solve it using z3
    def solve (self, json, CC, method = "SP"):
        self.load_from_json(json)
        #self.print_graph()
        self.brzozowski()
        #self.get_regex()
        #self.print_graph()
        self.cycle_paths(0)
        self.get_targets(CC)
        if method == "BF":
            for i in range(len(self.targets)):
                if self.targets != []:
                    self.bruteforce(100,50)
                else:
                    break
        else:
            paths = self.short_paths()
            for path in paths:
                formula = self.get_formula(path)
                if pprint:
                    print("Path to check:")
                    for node in path:
                        print(node.name, end = ' ')
                    print()
                    print("Generated formula:")
                    print(formula)
                    print("Result:")
                self.solve_formula(formula)
                if pprint:
                    print()
    


if __name__ == "__main__":
    cfg = CFG()
    cfg.solve("json_problem2.json", "PPC", "BF")
