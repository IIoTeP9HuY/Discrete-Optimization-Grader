import math
from collections import defaultdict

def parse_testcase(lines):
    firstLine = lines[0].split()
    n = int(firstLine[0])

    xs = []
    ys = []
    for i in range(1, n + 1):
        parts = lines[i].split()
        xs.append(float(parts[0]))
        ys.append(float(parts[1]))

    return {"x": xs, "y": ys}

def parse_submission(submission):
    lines = map(str.rstrip, submission.split('\n'))
    print(lines)
    length = float(lines[0])
    route = map(int, lines[1].split(' '))

    return {"length": length, "route": route}

def evaluate(testcase, submission):
    length = submission["length"]
    route = submission["route"]

    xs = testcase["x"]
    ys = testcase["y"]

    n = len(xs)
    if len(route) != n:
        raise Exception("Route is too short: {} < {}".format(len(route), n))

    counts = defaultdict(int)
    for v in route:
        if v <= 0 or v > n:
            raise Exception("Invalid vertex: " + str(v))

        counts[v] += 1
        if counts[v] > 1:
            raise Exception("Duplicate vertex found: " + str(v))

    def dist(x1, y1, x2, y2):
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

    total_length = 0
    route.append(route[0])
    for i in range(n):
        v = route[i] - 1
        nv = route[i + 1] - 1
        total_length += dist(xs[v], ys[v], xs[nv], ys[nv])

    if abs(length - total_length) > 1e-3:
        raise Exception("Wrong route length reported: got {}, actual {}".format(length, total_length))

    return total_length
