def read_data(path):
    lines = open(path).readlines()

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
