
# built-ins
import os

# external packages
import pandas
import numpy


def read_spreadsheet(filepath):
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

        return df, e


def to_spreadsheet(df, filepath):
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
        return False, e


def column_group_size(df, col):
    return df.groupby(col).size()


# returns a panda.Series object containing percentages of each column group
def column_group_percentage(df, col):
    return df.groupby(col).size().apply(lambda x: len(df))


# returns a float value, uniqueness of the column
def column_uniqueness(df, col):
    return df[col].nunique() / len(df)


# returns a panda.Series object containing adjusted uniqueness for selected columns
def adjusted_column_uniqueness(df, selected_cols):
    t = df[selected_cols].nunique() / len(df)
    return t.apply(lambda x: x / t.sum())


# returns a string of the largest group in the column
def column_largest_group(df, col):
    return df.groupby(col).size().idxmax()


# returns a string of the smallest group in the column
def column_smallest_group(df, col):
    return df.groupby(col).size().idxmin()


def get_column_dupes(df, column):
    duplicate_candidates = df[column].duplicated(keep=False)
    df[column].replace('', numpy.nan, inplace=True)
    df_dupe = df[duplicate_candidates].dropna(subset=[column])

    dupes_index = df_dupe.index.tolist()
    dupes = df_dupe[column].values.tolist()

    return dupes_index, dupes


def get_column_blanks(df, column):
    df[column].replace('', numpy.nan, inplace=True)
    blank_candidates = pandas.isnull(df[column])
    df_blank = df[blank_candidates]

    blank_index = df_blank.index.tolist()
    blanks = df_blank[column].values.tolist()

    return blank_index, blanks