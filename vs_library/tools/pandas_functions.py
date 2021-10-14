
# built-ins
import os

# external packages
import pandas
import numpy


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