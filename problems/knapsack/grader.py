import utils

def grade(name, test, submission, leaderboard):
    data = utils.read_data(os.path.join(testset.path, test))

    try:
        lines = submission.split('\n')
        profit = int(lines[0].rstrip())
        taken = map(int, lines[1].rstrip().split(' '))
    except Exception as e:
        return "Failed to parse submission: " + str(e)

    total_profit = 0
    total_weight = 0
    for item in taken:
        if item < 1 or item > len(data["weights"]):
            return "Incorrect item %s" % item

        total_weight += data["weights"][item - 1]
        total_profit += data["profits"][item - 1]

    if total_weight > data["capacity"]:
        return "Weight overflow: {} > {}".format(total_weight, data["capacity"])

    if total_profit != profit:
        return "Wrong profit reported: got {}, actual {}".format(profit, total_profit)

    leaderboard.update_record(name, test, total_profit)
    leaderboard.save(leaderboard_path)

    return "Total profit: %s" % total_profit
