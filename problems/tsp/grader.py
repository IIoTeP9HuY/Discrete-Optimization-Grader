import utils

def grade(name, test, submission, leaderboard):
    data = utils.read_data(os.path.join(testset.path, test))

    try:
        lines = submission.split('\n')
        length = float(lines[0].rstrip())
        route = map(int, lines[1].rstrip().split(' '))
    except Exception as e:
        return "Failed to parse submission: " + str(e)

    n = len(data["x"])
    if len(route) != n:
        return "Route is too short: {} < {}".format(len(route), n)

    counts = defaultdict(int)
    for v in route:
        if v <= 0 or v > n:
            return "Invalid vertex: " + str(v)

        counts[v] += 1
        if counts[v] > 1:
            return "Duplicate vertex found: " + str(v)

    def dist(x1, y1, x2, y2):
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

    xs = data["x"]
    ys = data["y"]

    total_length = 0
    route.append(route[0])
    for i in range(n):
        v = route[i] - 1
        nv = route[i + 1] - 1
        total_length += dist(xs[v], ys[v], xs[nv], ys[nv])

    if abs(length - total_length) > 1e-3:
        return "Wrong route length reported: got {}, actual {}".format(length, total_length)

    leaderboard.update_record(name, test, total_length)
    leaderboard.save(leaderboard_path)

    return "Total length: %s" % total_length
