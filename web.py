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

import problems.knapsack as knapsack
import problems.tsp as tsp

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
    def __init__(self, name, parse_testcase, parse_submission, evaluate):
        self.name = name
        self.parse_testcase = parse_testcase
        self.parse_submission = parse_submission
        self.evaluate = evaluate

problems = {
    "knapsack": Problem("knapsack", knapsack.parse_testcase, knapsack.parse_submission, knapsack.evaluate),
    "tsp": Problem("tsp", tsp.parse_testcase, tsp.parse_submission, tsp.evaluate)
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

def grade_submission(username, testcase_name, raw_submission):
    if testcase_name not in testset.tests:
        return "Incorrect test name"

    if problem_name not in problems:
        return "Problem is not registered"

    problem = problems[problem_name]

    try:
        testcase = problem.parse_testcase(
            open(os.path.join(testset.path, testcase_name)).readlines())
    except Exception as e:
        return "Failed to parse testcase: " + str(e)

    try:
        submission = problem.parse_submission(raw_submission)
    except Exception as e:
        return "Failed to parse submission: " + str(e)

    try:
        score = problem.evaluate(testcase, submission)
        leaderboard.update_record(username, testcase_name, score)
        leaderboard.save(leaderboard_path)
    except Exception as e:
        return "Failed to evaluate submission: " + str(e)


@bp.route("/")
def main_page():
    return render_template("main.html", problem=problem_name.upper())

@bp.route("/submit", methods=["GET", "POST"])
def submit_page():
    if is_frozen:
        return redirect(url_for(".leaderboard_page", verdict="Leaderboard is frozen"))

    if request.method == "POST":
        submission = request.files["file"]
        username = request.form["name"]
        testcase_name = request.form["problem"]
        verdict = grade_submission(username, testcase_name, submission.read())
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
