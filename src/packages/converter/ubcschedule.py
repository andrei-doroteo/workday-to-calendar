""" This module provides a class to represent a UBC Workday calendar
"""

from icalendar import Calendar
from pandas import DataFrame

from . import convert_file


class UBCSchedule:
    """A model of a UBC Workday schedule

    Attributes:
        __data (DataFrame): Data for a UBC Schedule
        __calendar (Calendar): An icalendar Calendar object
                               of a UBC Schedule
    """

    def __init__(self, data: DataFrame):
        """
        Initializes __data attribute and __calendar attribute
        """
        self.__data = data
        self.__calendar = None

    @property
    def data(self) -> DataFrame:
        """Getter method for __data"""
        return self.__data

    @data.setter
    def data(self, new: DataFrame) -> None:
        """Setter method for __data"""
        self.__data = new

    @property
    def calendar(self) -> Calendar:
        """getter method for __calendar

        __calendar initialises to None.
        You must call update_calendar() method first to return a value
        """
        return self.__calendar

    def update_calendar(self):
        """updates __calendar attribute to have current __data"""
        self.__calendar = convert_file(self.__data)
