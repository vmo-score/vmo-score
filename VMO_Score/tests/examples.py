def find_interval(env, label, t):
    return [item for item in env[label] if item[0] == t]


def get_next_time(env, label, initial_t):
    r = find_interval(env, label, initial_t)
    if (len(r) == 0):
        return None  # infinite
    else:
        return r[0][1]  # We found an interval and we get its second value


def valid_next(env, label, t):
    return len(find_interval(env, label, t)) != 0  # We found an interval

test_env = {0: [(130, 142), (529, 542), (676, 863)],
            1: [(116, 130), (249, 529), (542, 615), (645, 676), (916, 971), (1021, 1088)],
            2: [(0, 84)],
            3: [(84, 116), (142, 249), (615, 645), (863, 916), (971, 1021)]}

f1 = get_next_time(test_env, 0, 529)
print f1
print valid_next(test_env, 1, f1)
