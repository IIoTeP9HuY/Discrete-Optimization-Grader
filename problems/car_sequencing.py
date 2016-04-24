from utils import parse_ints

def parse_testcase(lines):
    total_cars_number, options_number, types_number = parse_ints(lines[0])
    car_types = []

    window_capacity = parse_ints(lines[1])
    window_size = parse_ints(lines[2])

    for i in range(types_number):
        line = parse_ints(lines[3 + i])
        type_id, cars_number = line[:2]
        options = line[2:]
        assert type_id == i
        car_types.append((cars_number, options))

    return {
        "car_types": car_types,
        "options": zip(window_capacity, window_size)
    }

def parse_submission(submission):
    lines = map(str.rstrip, submission.split('\n'))
    total_violations_number = parse_ints(lines[0])[0]
    sequence = parse_ints(lines[1])
    return {
        "total_violations_number": total_violations_number,
        "sequence": sequence
    }

def evaluate(testcase, submission):
    car_types = testcase["car_types"]
    options = testcase["options"]

    user_total_violations_number = submission["total_violations_number"]
    sequence = submission["sequence"]

    car_type_number = [0 for _ in car_types]
    for car in sequence:
        car_type_number[car] += 1
    for i in range(len(car_type_number)):
        if car_types[i][0] != car_type_number[i]:
            raise Exception("Wrong number of cars of type {}, expected {}, found {}"
                            .format(i, car_types[i][0], car_type_number[i]))

    total_violations_number = 0
    for option_id in range(len(options)):
        capacity = options[option_id][0]
        size = options[option_id][1]

        for pos in range(len(sequence) + size):
            taken = 0
            begin = max(pos - size + 1, 0)
            end = min(pos + 1, len(sequence))
            for car in sequence[begin:end]:
                taken += car_types[car][1][option_id]
            if taken > capacity:
                total_violations_number += taken - capacity

    if user_total_violations_number != total_violations_number:
        raise Exception("Wrong violations number reported: got {}, actual {}"
                        .format(user_total_violations_number, total_violations_number))

    return total_violations_number
