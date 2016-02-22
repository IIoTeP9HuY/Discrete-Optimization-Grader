# Grader for Combinatorial Optimization course

This repository contains code of web-based solutions grader for combinatorial optimization course

### Usage

To start webserver for tsp problem on port 80 with testcases in folder ./tsp_testcasesrecording results to file tsp_leaderboard:

```bash
python web.py --port 80 --problem tsp --data ./tsp_testcases --leaderboard tsp_leaderboard
```

To send submission to 3rd testcase for problem knapsack:

```bash
./submit.py your_name knapsack 3.public path_to_your_3_submission
```

### Requirements

* Python 2.7
* Flask (>=0.10.1)
* Requests
