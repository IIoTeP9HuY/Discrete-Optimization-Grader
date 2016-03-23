from flask import Flask, Blueprint
from flask import render_template, request, redirect, url_for
bp = Blueprint("grader", __name__, template_folder="templates")

from argparse import ArgumentParser
from collections import defaultdict

import knapsack_utils
import tsp_utils
import pickle
import os
import atexit
import signal
import sys
import math

class LeaderboardRecord(object):
    def __init__(self, minimization=False):
        self.scores = {}
        self.minimization = minimization

    def update_score(self, problem, score):
        if problem_name == "tsp":
            self.minimization = True
        else:
            self.minimization = False

        if self.minimization:
            self.scores[problem] = min(self.scores.get(problem, float('Inf')), score)
        else:
            self.scores[problem] = max(self.scores.get(problem, 0), score)

    def get_score(self, problem):
        return self.scores.get(problem, 0)

class Leaderboard(object):
    def __init__(self, minimization=False):
        self.records = {}
        self.minimization = minimization

    def set_minimization(self, minimization):
        self.minimization = minimization

    def update_record(self, name, problem, score):
        if not name in self.records:
            self.records[name] = LeaderboardRecord(self.minimization)
        self.records[name].update_score(problem, score)

    def get_sorted_records(self):
        def sorter(record):
            return sum(record[1].scores.values()) * (1 if self.minimization else -1)

        return sorted(self.records.items(), key=sorter)

    def save(self, path):
        open(path, "w").write(pickle.dumps(self.records))

    def load(self, path):
        if os.path.exists(path):
            self.records = pickle.loads(open(path, "r").read())

leaderboard = Leaderboard()
leaderboard_path = None
problem_name = None
is_frozen = False

class Testset(object):
    def __init__(self):
        self.tests = []

    def load(self, path):
        self.path = path
        for name in os.listdir(path):
            self.tests.append(name)

        def sorter(name):
            index, suite = name.split(".")
            return (suite == "private", int(index))

        self.tests = sorted(self.tests, key=sorter)

testset = Testset()

def knapsack_grader(name, problem, submission):
    data = knapsack_utils.read_data(os.path.join(testset.path, problem))

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

    leaderboard.update_record(name, problem, total_profit)
    leaderboard.save(leaderboard_path)

    return "Total profit: %s" % total_profit

def tsp_grader(name, problem, submission):
    data = tsp_utils.read_data(os.path.join(testset.path, problem))

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

    leaderboard.update_record(name, problem, total_length)
    leaderboard.save(leaderboard_path)

    return "Total length: %s" % total_length

def grade_submission(name, problem, submission):
    if problem not in testset.tests:
        return "Incorrect problem name"

    if problem_name == "knapsack":
        return knapsack_grader(name, problem, submission)
    if problem_name == "tsp":
        return tsp_grader(name, problem, submission)

@bp.route("/")
def main_page():
    return render_template("main.html", problem=problem_name.upper())

@bp.route("/submit", methods=["GET", "POST"])
def submit_page():
    if is_frozen:
        return redirect(url_for(".leaderboard_page", verdict="Leaderboard is frozen"))

    if request.method == "POST":
        submission = request.files["file"]
        name = request.form["name"]
        problem = request.form["problem"]
        verdict = grade_submission(name, problem, submission.read())
        print(verdict)
        return redirect(url_for(".leaderboard_page", verdict=verdict))

    problems = testset.tests
    return render_template("submit.html", problems=problems)

@bp.route("/submit_score")
def submit_score_page():
    if is_frozen:
        return redirect(url_for(".leaderboard_page", verdict="Leaderboard is frozen"))

    problem = request.args.get("problem")
    name = request.args.get("name")
    score = float(request.args.get("score"))

    print("Submitted {}, {}, {}".format(problem, name, score))
    leaderboard.update_record(name, problem, score)
    leaderboard.save(leaderboard_path)

    return redirect(url_for(".leaderboard_page", verdict="<OK>"))

@bp.route("/leaderboard")
def leaderboard_page():
    items = leaderboard.get_sorted_records()
    problems = testset.tests
    verdict = request.args.get("verdict")
    return render_template(
            "leaderboard.html",
            items=items,
            problems=problems,
            verdict=verdict)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port to run web server")

    parser.add_argument(
        "--leaderboard",
        type=str,
        default="leaderboard",
        help="Path to leaderboard file")

    parser.add_argument(
        "--data",
        type=str,
        default="data",
        help="Path to test data")

    parser.add_argument(
        "--problem",
        type=str,
        required=True,
        choices=["knapsack", "tsp"])

    parser.add_argument(
        "--frozen",
        dest="frozen",
        default=False,
        action="store_true")

    args = parser.parse_args()

    leaderboard_path = args.leaderboard
    leaderboard.load(args.leaderboard)
    testset.load(args.data)

    is_frozen = args.frozen

    problem_name = args.problem

    if problem_name == "knapsack":
        leaderboard.set_minimization(False)
    elif problem_name == "tsp":
        leaderboard.set_minimization(True)

    app = Flask(__name__)
    app.register_blueprint(bp, url_prefix="/" + args.problem)
    # app.debug = True

    if not app.debug:
        import logging
        from logging import FileHandler
        file_handler = FileHandler(problem_name + ".log")
        file_handler.setLevel(logging.DEBUG)
        app.logger.addHandler(file_handler)

    app.run(host="0.0.0.0", port=args.port)

