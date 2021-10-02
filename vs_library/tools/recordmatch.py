# external packages
from fuzzywuzzy import fuzz


def uniqueness(records):
    columns = records[0].keys() if records else []
    uniqueness = dict()

    for column in set(columns):
        column_list = [r[column] for r in records]
        uniqueness[column] = len(set(column_list)) / len(records)

    return uniqueness


def adjusted_uniqueness(uniqueness, selected_columns):
    total = sum([uniqueness[column] for column in selected_columns])

    return {column: uniqueness[column]/total for column in selected_columns}


def match_ratio(a, b):
    string_a = str(a).strip().lower()
    string_b = str(b).strip().lower()

    if string_a and string_b:
        if len(string_a) <= 2 or len(string_b) <= 2:
            return fuzz.partial_ratio(string_a, string_b)/100
        elif len(string_a.split('-')) > 1 or len(string_b.split('-')) > 1 or \
             len(string_a.split(' ')) > 1 or len(string_b.split(' ')) > 1:
            return fuzz.token_set_ratio(string_a, string_b)/100
        else:
            return fuzz.ratio(string_a, string_b)/100
    else:
        return float(0)


def match(records, X, column, threshold=0):
    scores = [match_ratio(X[column], R[column]) for R in records]
    max_score = max(scores)

    return [records[index] for index, score in enumerate(scores) if score==max_score and score>=threshold]


def cross(records, X, column, other_columns, threshold=0):
    scores = [max([match_ratio(X[column], R[o_c]) for o_c in other_columns]) for R in records]
    max_score = max(scores)

    return [records[index] for index, score in enumerate(scores) if score==max_score and score>=threshold]


def combined(records, X, columns, uniqueness, threshold=0):
    adj  = adjusted_uniqueness(uniqueness, columns)

    scores = [sum(adj[c] * match_ratio(X[c], R[c]) for c in columns) for R in records]
    max_score = max(scores)

    return [records[index] for index, score in enumerate(scores) if score==max_score and score>=threshold]

