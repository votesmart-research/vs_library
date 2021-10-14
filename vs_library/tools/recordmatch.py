
# external packages
from fuzzywuzzy import fuzz


def uniqueness(records):
    """
    Calculates the ratio of unique elements to the length of records
    in each columns

    Returns
    -------
    dict
    """
    columns = records[0].keys() if records else []
    uniqueness = dict()

    for column in set(columns):
        items = [r[column] for r in records]
        uniqueness[column] = len(set(items)) / len(records)

    return uniqueness


def adjusted_uniqueness(uniqueness, selected_columns):

    """
    Calculates the ratio of unique elements to the length of records
    adjusted to selected columns
    
    Returns
    -------
    dict
    """

    total = sum([uniqueness[column] for column in selected_columns])
    return {column: uniqueness[column]/total for column in selected_columns}


def match_ratio(a, b):

    """
    Calculates the matching scores of two strings

    Special Criterias
    -----------------
        1) String with 2 or less characters will be match on characters found
           in another string
        2) String with hyphens or contains multiple words will match based
           on each words

    Returns
    -------
    float
    """

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

    """
    Finds possible matching records based on scores of each string of the same column

    Parameters
    ----------
    records : [dict_1, dict_2...]
        Each record is a dictionary containing the same keys as next on the list

    X : dict
        A record to be matched with other records

    column : string
        To specify a column in the record

    threshold : decimal
        The total matching score have to pass this in order for the possible match
        to be considered valid. Can be any number between 0 and 1, 0 being the lowest 
        and 1 being the highest. Ex. 0.5 is 50 percent and 0.9 is 90 percent
    """

    scores = [match_ratio(X[column], R[column]) for R in records]
    max_score = max(scores)

    return [records[index] for index, score in enumerate(scores) if score==max_score and score>=threshold]


def cross(records, X, column, other_columns, threshold=0):

    """
    Finds possible matching records based on string of a specified column cross with 
    string of other columns

    Parameters
    ----------
    records : [dict_1, dict_2...]
        Each record is a dictionary containing the same keys as next on the list

    X : dict
        A record to be matched with other records

    column : string
        To specify a column in the record

    other_columns : list
        Specifying the list of columns to be matched with the selected column

    threshold : decimal
        The total matching score have to pass this in order for the possible match
        to be considered valid. Can be any number between 0 and 1, 0 being the lowest 
        and 1 being the highest. Ex. 0.5 is 50 percent and 0.9 is 90 percent
    """
    scores = [max([match_ratio(X[column], R[o_c]) for o_c in other_columns]) for R in records]
    max_score = max(scores)

    return [records[index] for index, score in enumerate(scores) if score==max_score and score>=threshold]


def combined(records, X, columns, uniqueness, threshold=0):
    """
    Finds possible matching records based on the combination of matching string scores
    in the specified columns

    Parameters
    ----------
    records : [dict_1, dict_2...]
        Each record is a dictionary containing the same keys as next on the list

    X : dict
        A record to be matched with other records

    columns : list
        Specifying the list of columns to be matched

    uniqueness : dict
        Uniqueness of each column in records
        Note: No reason to compute the uniqueness of records over and over again, 
        hence this is set as a parameter

    threshold : decimal
        The total matching score have to pass this in order for the possible match
        to be considered valid. Can be any number between 0 and 1, 0 being the lowest 
        and 1 being the highest. Ex. 0.5 is 50 percent and 0.9 is 90 percent
    """
    adj  = adjusted_uniqueness(uniqueness, columns)

    scores = [sum(adj[c] * match_ratio(X[c], R[c]) for c in columns) for R in records]
    max_score = max(scores)

    return [records[index] for index, score in enumerate(scores) if score==max_score and score>=threshold]

