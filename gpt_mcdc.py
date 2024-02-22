import itertools

def evaluate_clause(input_clause, input_combination):
    # Evaluate the input clause with the given input combination
    locals().update(input_combination)  # Set local variables based on input combination
    return eval(input_clause)

def generate_input_combinations(num_conditions):
    # Generate all possible combinations of inputs for num_conditions conditions
    return list(itertools.product([True, False], repeat=num_conditions))

def mcdc_coverage(input_clause):
    conditions = set()
    num_conditions = 0

    # Parse the input clause string to identify conditions and decisions
    for token in input_clause.split():
        if token.isalpha():
            conditions.add(token)
            num_conditions += 1

    num_combinations = 2 ** num_conditions
    covered_combinations = set()

    input_combinations = generate_input_combinations(num_conditions)

    # Evaluate clause for each input combination
    for input_combination in input_combinations:
        result = evaluate_clause(input_clause, dict(zip(conditions, input_combination)))

        # Check if this combination covers a new set of conditions
        covered_conditions = set()
        for i, condition in enumerate(conditions):
            if input_combination[i]:
                covered_conditions.add(condition)
            else:
                covered_conditions.add('-' + condition)

        if covered_conditions not in covered_combinations:
            covered_combinations.add(covered_conditions)

    return covered_combinations

# Example input clause string
example_input_clause_str = "a and b or not c"

# Test the MC/DC coverage for the example input clause
coverage = mcdc_coverage(example_input_clause_str)
print("MC/DC Coverage:")
for combination in coverage:
    print(combination)
