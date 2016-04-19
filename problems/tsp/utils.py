def read_data(path):
    lines = open(path).readlines()

    firstLine = lines[0].split()
    n = int(firstLine[0])

    xs = []
    ys = []
    for i in range(1, n + 1):
        parts = lines[i].split()
        xs.append(float(parts[0]))
        ys.append(float(parts[1]))

    return {"x": xs, "y": ys}
