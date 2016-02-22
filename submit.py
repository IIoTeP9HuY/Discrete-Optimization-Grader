#!/usr/bin/env python
# Usage example: ./submit.py my_nickname knapsack 1.public ./1.solution

import requests
import HTMLParser
from argparse import ArgumentParser

def main():
    parser = ArgumentParser(description="Script to submit solutions to grader")
    parser.add_argument("name", type=str)
    parser.add_argument("problem", type=str, choices=["knapsack", "tsp"])
    parser.add_argument("testcase", type=str, help="name of testcase")
    parser.add_argument("submission", type=str, help="path to submission file")

    args = parser.parse_args()

    url = "http://shad.akashin.me/{}/submit".format(args.problem)
    data = {
        "name": args.name,
        "problem": args.testcase,
    }
    r = requests.post(url, data=data, files={"file": open(args.submission)})
    if r.status_code == 200 and r.reason == "OK":
        for line in r.text.split("\n"):
            if "<h2>" in line:
                h = HTMLParser.HTMLParser()
                line = h.unescape(line).replace("<h2>", "").replace("</h2>", "")
                print(line)
                break

if __name__ == "__main__":
    main()
