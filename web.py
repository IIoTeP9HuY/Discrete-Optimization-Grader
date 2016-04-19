from flask import Flask, Blueprint
from flask import render_template, request, redirect, url_for
bp = Blueprint("grader", __name__, template_folder="templates")

from argparse import ArgumentParser
from collections import defaultdict

import pickle
import os
import atexit
import signal
import sys
import math

import problems.knapsack.grader as knapsack_grader
import problems.tsp.grader as tsp_grader

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

class Problem(object):
    def __init__(self, name, grader):
        self.name = name
        self.grader = grader

problems = {
    "knapsack": Problem("knapsack", knapsack_grader.grade),
    "tsp": Problem("tsp", tsp_grader.grade)
}

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

def grade_submission(name, test, submission):
    if test not in testset.tests:
        return "Incorrect test name"

    if problem_name not in problems:
        return "Problem is not registered"

    problems[problem_name].grade(name, test, submission, leaderboard)

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
