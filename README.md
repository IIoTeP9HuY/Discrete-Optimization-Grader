# Grader for Discrete Optimization course

This repository contains code of web-based solutions grader for discrete optimization course

### Usage

To start webserver on port 80 with testcases in folder ./testcases:

```bash
    python web.py --port 80 --data ./testcases
```

To send submission to 3rd testcase:

```bash
    ./submit.py your_name 3.public path_to_your_3_submission
```

### Requirements

* Python 2.7
* Flask (>=0.10.1)
* Requests
