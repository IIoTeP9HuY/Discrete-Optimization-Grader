def parse_testcase(lines):
    firstLine = lines[0].split()
    items = int(firstLine[0])
    capacity = int(firstLine[1])

    profits = []
    weights = []
    for i in range(1, items + 1):
        parts = lines[i].split()
        profits.append(int(parts[0]))
        weights.append(int(parts[1]))

    return {"capacity": capacity, "profits": profits, "weights": weights}

def parse_submission(submission):
    lines = map(str.rstrip, submission.split('\n'))
    profit = int(lines[0])
    taken = map(int, lines[1].split(' '))

    return {"profit": profit, "taken": taken}

def evaluate(testcase, submission):
    capacity = testcase["capacity"]
    weights = testcase["weights"]
    profits = testcase["profits"]

    submission_total_profit = submission["profit"]
    taken = submission["taken"]

    total_profit = 0
    total_weight = 0
    for item in taken:
        if item < 1 or item > len(weights):
            raise Exception("Incorrect item %s" % item)

        total_weight += weights[item - 1]
        total_profit += profits[item - 1]

    if total_weight > capacity:
        raise Exception("Weight overflow: {} > {}".format(total_weight, capacity))

    if total_profit != submission_total_profit:
        raise Exception("Wrong profit reported: got {}, actual {}".format(profit, total_profit))

    return total_profit
