import copy

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

    
def num_clauses(predicate):
    if isinstance(predicate, LogicalAnd) or isinstance(predicate, LogicalOr):
        return num_clauses(predicate.l) + num_clauses(predicate.r)
    elif isinstance(predicate, LogicalNot):
        return num_clauses(predicate.op)
    else:
        return 1
    
def evaluate(predicate, queue):
    if isinstance(predicate, LogicalAnd):
        res, queue = evaluate(predicate.l, queue)
        res2, queue = evaluate(predicate.r, queue)
        return (res and res2, queue)
    if isinstance(predicate, LogicalOr):
        res, queue = evaluate(predicate.l, queue)
        res2, queue = evaluate(predicate.r, queue)
        return (res or res2, queue)
    if isinstance(predicate, LogicalNot):
        res, queue = evaluate(predicate.op, queue)
        return (not res, queue)
    else:
        return (queue.pop(0), queue)
    
def generate_combinations(n):
    num_bits = n
    combinations = []
    
    for i in range(2**num_bits):
        binary_str = bin(i)[2:].zfill(num_bits)
        combination = [bool(int(bit)) for bit in binary_str]
        combinations.append(combination)
    
    return combinations

def assign_vals(predicate, queue, map):
    if isinstance(predicate, LogicalAnd):
        queue, map = assign_vals(predicate.l, queue, map)
        queue, map = assign_vals(predicate.r, queue, map)
        return (queue, map)
    if isinstance(predicate, LogicalOr):
        queue, map = assign_vals(predicate.l, queue, map)
        queue, map = assign_vals(predicate.r, queue, map)
        return (queue, map)
    if isinstance(predicate, LogicalNot):
        queue, map = assign_vals(predicate.op, queue, map)
        return (queue, map)
    else:
        map[predicate] = queue.pop(0)
        return (queue, map)

def eval_combs(predicate):
    n = num_clauses(predicate)
    combinations = generate_combinations(n)
    res = []
    for comb in copy.deepcopy(combinations):
        for i in range(n):
            e1 = evaluate(predicate, copy.deepcopy(comb))[0]
            comb[i] = not comb[i]
            e2 = evaluate(predicate, copy.deepcopy(comb))[0]
            comb[i] = not comb[i]
            if e1 != e2:
                if comb not in res:
                    res.append(comb)
    #print(res)
    res2 = []
    for r in res:
        q, m = assign_vals(predicate, r, {})
        res2.append(m)
        #print(m)
    return res2
    print(comb, end="")
    print(evaluate(predicate, comb))

# # Example usage:
# input_number = 3
# combinations = generate_combinations(input_number)
# print(combinations)