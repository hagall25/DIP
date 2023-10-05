import json
from z3 import *
import parse

pprint = True

#Is subpath includen in path?
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
    
    def add_succ(self, node):
        self.succs.add(node)

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
            for subpath in prime:
                if is_subpath(path, subpath):
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
                    self.targets.append((node, self.get_node(succ)))
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
        solve(f)

    def solve (self, json, CC):
        self.load_from_json(json)
        self.get_targets(CC)
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


cfg = CFG()
cfg.solve("json_problem.json", "PPC")
