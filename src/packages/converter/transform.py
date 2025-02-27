from re import search

from django.core.files.uploadedfile import UploadedFile
from icalendar import Calendar
from pandas import DataFrame, read_excel

from .calendar import create_ical
from .data import convert_all


def import_data(file: str | UploadedFile | DataFrame) -> DataFrame:
    # TODO: !!! REFACTOR
    """Cleans the schedule data of a UBC schedule

    Args:
        file (str): A path to a UBC workday schedule excel file

        file (UploadedFile): A file upload of a
                             UBC workday schedule

        file (DataFrame): A DataFrame obtained by read_excel from pandas
                          of a UBC workday schedule

    Returns:
        A Dataframe of the schedeule content of the uploaded UBC workday
    schedule
    """

    start = _find_start(file)
    end = _find_end(file)

    return read_excel(file, skiprows=start, skipfooter=end)


def _find_start(file: str | UploadedFile | DataFrame) -> int:
    """Finds the index of the start of the schedule data
    Args:
        file (str): A path to a UBC workday schedule excel file

        file (UploadedFile): A file upload of a
                             UBC workday schedule

        file (DataFrame): A DataFrame obtained by read_excel from pandas
                          of a UBC workday schedule


    Returns:
        An int of the index of the begining row of (the column names)
    the schedule data

    """
    if isinstance(file, DataFrame):
        data = _no_header_df(file)
    else:
        data = read_excel(file, header=None)

    def _get_row_with_header() -> DataFrame:
        """
        Returns dataframe of row(s) in data that match the header row,
        keeping the same index values as data
        """
        header = (
            (data[0].isna())
            & (data[1] == "Course Listing")
            & (data[2] == "Credits")
            & (data[3] == "Grading Basis")
            & (data[4] == "Section")
            & (data[5] == "Instructional Format")
            & (data[6] == "Delivery Mode")
            & (data[7] == "Meeting Patterns")
            & (data[8] == "Registration Status")
            & (data[9] == "Instructor")
            & (data[10] == "Start Date")
            & (data[11] == "End Date")
        )

        return data[header]

    def _get_index_of_header() -> int:
        """
        Returns the index of the first row in data that contains all the
        column names
        """

        return _get_row_with_header().index[0]

    return _get_index_of_header()


def _find_end(file: str | UploadedFile | DataFrame) -> int:
    """Finds the index of the end of the schedule data
    Args:
        file (str): A path to a UBC workday schedule excel file

        file (UploadedFile): A file upload of a
                             UBC workday schedule

        file (DataFrame): A DataFrame obtained by read_excel from pandas
                          of a UBC workday schedule

    Returns:
        The index of the ending row of the schedule data
    (the last enrolled course)

    """

    start = _find_start(file)

    if isinstance(file, DataFrame):
        data = _no_header_df(file, skiprows=start + 1)
    else:
        data = read_excel(file, skiprows=start + 1, header=None)

    pattern = "\w+ \w+ \(\d{8}\)"

    index = 0
    for val in data[0]:
        if search(pattern, str(val)) is None:
            return len(data[0]) - index
        else:
            index += 1
    else:
        return 0


def _no_header_df(dataframe: DataFrame, skiprows: int = None) -> DataFrame:
    """
    Makes a new dataframe where the header of dataframe moves down and
    a new header is set to be ints starting from 0

    Args:
        dataframe (DataFrame): a pandas DataFrame

        skiprows (int): the number of rows to skip from
                        the begining of the DataFrame.This behaves like
                        the skiprows argument in the
                        read functions of pandas

    This helper function is to create the same DataFrame that would be
    created with read_excel() with "header=None" as an argument.
    This is for UBC schedule excel files that have already been read
    into a DataFrame but have not been processed yet. This converts
    them into a usable format for the
    _find_start() and _find_end() functions.
    """

    if dataframe.equals(DataFrame({})):
        return DataFrame({})

    new_dataframe = dataframe.copy()

    old_header = new_dataframe.columns.tolist()
    old_values = new_dataframe.values.tolist()

    new_values = [old_header] + old_values

    if skiprows:
        new_values = new_values[skiprows:]

    return DataFrame(new_values)


def convert_file(file: str | UploadedFile | DataFrame) -> Calendar:
    """Converts a UBC Schedule (file) to a Calendar object
    Args:
        file (str): A path to a UBC workday schedule excel file

        file (UploadedFile): A file upload of a
                             UBC workday schedule

        file (DataFrame): A DataFrame obtained by read_excel from pandas
                          of a UBC workday schedule

    Returns:
        A Calendar object from the icalendar package
    """
    data = import_data(file)

    converted = convert_all(data)
    data_dict = converted.to_dict(orient="records")

    return create_ical(data_dict)
