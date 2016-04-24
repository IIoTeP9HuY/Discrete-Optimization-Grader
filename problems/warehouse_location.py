from utils import parse_ints, parse_floats

def parse_testcase(lines):
    warehouse_count, customer_count = parse_ints(lines[0])

    warehouse_capacities = []
    warehouse_open_costs = []
    for i in range(warehouse_count):
        capacity, cost = parse_floats(lines[1 + i])
        warehouse_capacities.append(capacity)
        warehouse_open_costs.append(cost)

    customer_demands = parse_floats(lines[1 + warehouse_count])

    warehouse_serve_costs = []
    for j in range(warehouse_count):
        costs = parse_floats(lines[2 + warehouse_count + j])
        warehouse_serve_costs.append(costs)

    return {
        "warehouse_capacities": warehouse_capacities,
        "warehouse_open_costs": warehouse_open_costs,
        "warehouse_serve_costs": warehouse_serve_costs,
        "customer_demands": customer_demands,
    }

def parse_submission(submission):
    lines = submission.rstrip().split('\n')
    return [parse_floats(line) for line in lines]

def evaluate(testcase, submission):
    warehouse_capacities = testcase["warehouse_capacities"]
    customer_demands = testcase["customer_demands"]
    warehouse_open_costs = testcase["warehouse_open_costs"]
    warehouse_serve_costs = testcase["warehouse_serve_costs"]

    warehouse_count = len(warehouse_capacities)
    customer_count = len(customer_demands)
    residual_warehouse_capacities = warehouse_capacities[:]

    assignments = submission

    if len(assignments) != customer_count:
        raise Exception("Wrong number of customers, expected {}, found {}".format(customer_count, len(assignments)))

    open_cost = 0
    serve_cost = 0
    for i in range(customer_count):
        if len(assignments[i]) != warehouse_count:
            raise Exception("Wrong number of warehouses in customer assignment list, expected {}, found {}"
                            .format(warehouse_count, len(assignments[i])))

        residual_customer_demand = customer_demands[i]
        for j in range(warehouse_count):
            if assignments[i][j] < 0 or assignments[i][j] > 1:
                raise Exception("Wrong assignment value {}".format(assignments[i][j]))

            residual_warehouse_capacities[j] -= assignments[i][j] * customer_demands[i]
            residual_customer_demand -= assignments[i][j] * customer_demands[i]
            serve_cost += warehouse_serve_costs[j][i] * assignments[i][j]

        if residual_customer_demand > 1e-6:
            raise Exception("Customer {} demand is not fulfilled".format(i))

    for j in range(warehouse_count):
        if residual_warehouse_capacities[j] < -1e-6:
            raise Exception("Warehouse {} is overcrowded".format(j))

        if residual_warehouse_capacities[j] < warehouse_capacities[j]:
            open_cost += warehouse_open_costs[j]

    return open_cost + serve_cost
