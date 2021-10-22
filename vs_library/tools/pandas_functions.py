
# built-ins
import os
from collections import defaultdict

# external packages
import pandas
import numpy
from rapidfuzz import process, fuzz


def read_spreadsheet(filepath):

    """Reads a spreadsheet format file and converts it to pandas.DataFrame
    
    See more on pandas.DataFrame at:
    https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html
    
    Parameters
    ----------
    filepath : str
        Path to spreadsheet file on user's computer to be imported
    """

    _ , ext = os.path.splitext(filepath)

    try:
        if ext in ('.xls', '.xlsx', '.xlsm', '.xlsb', '.ods'):
            df = pandas.read_excel(filepath)

        elif ext == '.csv':
            df = pandas.read_csv(filepath)
        
        elif ext == '.tsv':
            df = pandas.read_table(filepath)
        
        else:
            df = pandas.DataFrame()
            return df, f"File not imported. Extension: \'{ext}\' not recognized"

        return df, f"File successfully imported as \'{os.path.basename(filepath)}\'"

    except Exception as e:
        
        df = pandas.DataFrame()

        return df, f"ERROR: {str(e)}"


def to_spreadsheet(df, filepath):

    """
    Converts a pandas.DataFrame into a spreadsheet file
    
    See more on pandas.DataFrame at:
    https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html

    Parameters
    ----------
    df : pandas.DataFrame()
        Not empty dataframe to be exported

    filepath : str
        Path on a user's computer where pandas.DataFrame() is to be exported
    """

    _ , ext = os.path.splitext(filepath)

    try:
        if ext in ('.ods', '.xlsx', '.xlsm', '.xlsb'):
            df.to_excel(filepath, index=False)

        elif ext == '.csv':
            df.to_csv(filepath, index=False)
        
        elif ext == '.tsv':
            df.to_csv(filepath, sep='\t', index=False)
        
        else:
            return False, f"File not exported. Extension: \'{ext}\' not recognized"

        return True, f"File successfully exported to \'{os.path.abspath(filepath)}\'"

    except Exception as e:
        return False, f"ERROR: {str(e)}"


def column_group_percentage(df, col):

    """
    Calculates the size percentage of a column group
    
    Returns
    -------
    pandas.Series

    """

    return df.groupby(col).size().apply(lambda x: x/len(df)*100)


def uniqueness(df):

    """
    Calculates the ratio of unique elements to the length of pandas.DataFrame
    in each column

    Returns
    -------
    pandas.Series
    """

    return df.nunique().apply(lambda x: x/len(df))


def adjusted_uniqueness(df, selected_cols):

    """
    Calculates the ratio of unique elements to length of pandas.DataFrame
    adjusted to selected columns
    
    Returns
    -------
    pandas.Series
    """

    u = df[selected_cols].nunique().apply(lambda x: x/len(df))
    return u.apply(lambda x: x / u.sum())


def get_column_dupes(df, column):

    """
    Finds for duplicates within a column
    
    Returns
    -------
    (duplicate row indices, duplicated row values)
    """
    # replace all blanks with NaN
    temp_df = df.replace('', numpy.nan)
    # keep is set to False so all duplicated values are accounted
    column_check = temp_df[column].duplicated(keep=False)

    # keep only duplicated rows and drop NaN
    df_dupe = temp_df[column_check].dropna(subset=[column])

    dupes_index = df_dupe.index.tolist()
    dupes = df_dupe[column].values.tolist()

    return dupes_index, dupes


def get_column_blanks(df, column):

    """
    Finds for blanks within a column
    
    Returns
    -------
    (blank row indices, blank row values)
    """

    # replace all blanks with NaN
    temp_df = df.replace('', numpy.nan)
    column_check = pandas.isnull(temp_df[column])
    
    # keep only blank rows
    df_blank = temp_df[column_check]

    blank_index = df_blank.index.tolist()
    blanks = df_blank[column].values.tolist()

    return blank_index, blanks


class PandasMatcher:

    def __init__(self):

        self.__df_to = pandas.DataFrame()
        self.__df_from = pandas.DataFrame()

        self.column_threshold = defaultdict(float)
        self.columns_to_match = defaultdict(list)
        self.columns_to_get = []
        self.required_threshold = 75
        self.cutoff = False

    @property
    def df_to(self):
        return self.__df_to

    @df_to.setter
    def df_to(self, df):
        self.__df_to = df.astype('string').replace(pandas.NA, '')
        self.columns_to_match.clear()

        for column_to in self.__df_to.columns:
            self.column_threshold[column_to] = self.required_threshold
            if column_to in self.__df_from.columns:
                self.columns_to_match[column_to].append(column_to)
            else:
                self.columns_to_match[column_to] = []

    @property
    def df_from(self):
        return self.__df_from

    @df_from.setter
    def df_from(self, df):
        self.__df_from = df.astype('string').replace(pandas.NA, '')
        self.columns_to_get.clear()

        for _, columns_from in self.columns_to_match.items():
            columns_from.clear()

        for column_from in self.__df_from.columns:
            if column_from in self.columns_to_match.keys():
                self.columns_to_match[column_from].append(column_from)

    def _choices(self):
        choices = {}
        for column_to, columns_from in self.columns_to_match.items():
            for column_from in columns_from:
                if column_to not in choices.keys():
                    choices[column_to] = self.__df_from[column_from].copy()
                else:
                    choices[column_to] += ' ' + self.__df_from[column_from]

        return choices

    def _compute_score(self, choices, index_to, uniqueness):
        match_scores = defaultdict(float)

        for column_to, columns_from in self.columns_to_match.items():

            if columns_from:
                row_to = self.__df_to.iloc[index_to]
                matches = process.extract(row_to[column_to], choices[column_to],
                                          scorer=fuzz.WRatio,
                                          limit=len(self.__df_from),
                                          score_cutoff=0 if not self.cutoff else self.column_threshold[
                                                                                     column_to] or 0)

                for _, score, index_from in matches:
                    match_scores[index_from] += score * uniqueness[column_to]

        return match_scores

    def _top_matches(self, match_scores, optimal_threshold):

        def filter_highest(y):
            return {k: v for k, v in y.items() if v == max(y.values())}

        top_matches = defaultdict(dict)

        for index_from, match_score in filter_highest(match_scores).items():
            if round(match_score, 2) >= round(self.required_threshold, 2):
                match_status = 'REVIEW' if match_score < optimal_threshold else 'MATCHED'
                top_matches[index_from].update({'match_status': match_status,
                                                'match_score': match_score})

        return top_matches

    def match(self):

        columns_to_match = [column for column in self.columns_to_match.keys() if self.columns_to_match[column]]
        uniqueness = adjusted_uniqueness(self.__df_to, columns_to_match)
        optimal_threshold = sum([self.column_threshold[column] * uniqueness[column] for column in columns_to_match])

        choices = self._choices()
        df_matched = self.__df_to.copy()

        scores = []

        summary = {'average_score': 0.0,
                   'highest_score': 0.0,
                   'lowest_score': 0.0,
                   'optimal': 0,
                   'review': 0,
                   'total': 0,
                   'unmatched': 0,
                   'ambiguous': 0}
                   
        for index_to in range(0, len(self.__df_to)):

            match_scores = self._compute_score(choices, index_to, uniqueness)
            top_matches = self._top_matches(match_scores, optimal_threshold)

            if len(top_matches) == 1:
                index_from = next(iter(top_matches))

                for column in self.columns_to_get:
                    df_matched.at[index_to, column] = self.__df_from.at[index_from, column]

                df_matched.at[index_to, 'row_index'] = int(index_from + 2)
                df_matched.at[index_to, 'match_score'] = top_matches[index_from]['match_score']
                df_matched.at[index_to, 'match_status'] = top_matches[index_from]['match_status']

                scores.append(top_matches[index_from]['match_score'])

                if top_matches[index_from]['match_status'] == "REVIEW":
                    summary['review'] += 1
                elif top_matches[index_from]['match_status'] == "MATCHED":
                    summary['optimal'] += 1

                summary['total'] += 1

            elif len(top_matches) > 1:
                df_matched['row_index'] = df_matched['row_index'].astype('object')
                df_matched.at[index_to, 'row_index'] = ', '.join(list(map(str, top_matches.keys())))
                df_matched.at[index_to, 'match_status'] = 'AMBIGUOUS'

                summary['ambiguous'] += 1

            else:
                df_matched.at[index_to, 'match_status'] = 'UNMATCHED'
                summary['unmatched'] += 1

        summary['average_score'] = sum(scores) / len(scores) if scores else 0
        summary['highest_score'] = max(scores) if scores else -1
        summary['lowest_match_score'] = min(scores) if scores else -1

        return df_matched, summary
