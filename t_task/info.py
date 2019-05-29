# -*- coding: utf-8 -*-
"""Module contains class FlightInfo and some functions"""
from collections import OrderedDict
from datetime import datetime, timedelta
from itertools import product
from requests import get, exceptions
from lxml import html
import pandas as pd


class FlightInfo(object):
    """Summary of FlightInfo.
    Parameters
    ----------
    dep_city : str
       Departure city code
    arr_city : str
       Arrival city code
    dep_date : str
       Departure date in format dd.mm.yyyy
    arr_date : str
       Arrival date in format dd.mm.yyyy or empty string
    """
    def __init__(self):
        self.dep_city = None
        self.arr_city = None
        self.dep_date = None
        self.arr_date = None

    def set_info(self, dep_city_checked, arr_city_checked, dep_date_checked, arr_date_checked):
        """Set the value of class parameters"""
        self.dep_city = dep_city_checked
        self.arr_city = arr_city_checked
        self.dep_date = dep_date_checked
        self.arr_date = arr_date_checked

    def get_flight_info(self):
        """Establishes a connection and receives data from the site"""
        params = {
            'departure-city': self.dep_city,
            'arrival-city': self.arr_city,
            'departure-date': self.dep_date,
            'arrival-date': self.arr_date,
            'adults-children': '1'
        }
        try:
            main_page_html = get('http://www.flybulgarien.dk/en/search', params=params)
            html_tree = html.document_fromstring(main_page_html.content)

            inner_page_html = get(html_tree.xpath("//iframe[@name='flybulgarienintraweb']/@src")[0])
            html_tree = html.document_fromstring(inner_page_html.content)
        except exceptions.ConnectionError:
            return 'Попытка установить соединение была безуспешной'

        return self.extract_flight_info(html_tree)

    def extract_flight_info(self, html_tree):
        """Get needed tags, send it to the combine function and accumulate data.
         Parameters
        ----------
        html_tree : lxml.html.HtmlElement
             An lxml element
        Returns
        -------
        DataFrame
            A frame with full information about flights sorted by price
        """

        flight_table = html_tree.xpath("//table[@id='flywiz_tblQuotes']")[0]
        dep_flight_info_tags = flight_table.xpath("./tr[contains(@id,'flywiz_rinf')]")
        dep_flight_price_tags = flight_table.xpath("./tr[contains(@id,'flywiz_rprc')]")
        arr_flight_info_tags = flight_table.xpath("./tr[contains(@id,'flywiz_irinf')]")
        arr_flight_price_tags = flight_table.xpath("./tr[contains(@id,'flywiz_irprc')]")

        if not dep_flight_info_tags and not arr_flight_info_tags or not dep_flight_info_tags:
            return 'No flights available'

        dep_flight_info = self.combine_info(dep_flight_info_tags,
                                            dep_flight_price_tags,
                                            is_one_way=True)
        if not dep_flight_info:
            return 'No flights available'

        if self.arr_date:
            arr_flight_info = self.combine_info(arr_flight_info_tags,
                                                arr_flight_price_tags,
                                                is_one_way=False)
            if arr_flight_info:
                total_flight_combinations = []
                for to_fl, back_fl in product(dep_flight_info, arr_flight_info):
                    total_flight_combinations.append(
                        OrderedDict(list(to_fl.items()) +
                                    list(back_fl.items()))
                    )

                data_frame_comb = pd.DataFrame(total_flight_combinations)
                data_frame_comb['price'] = data_frame_comb['price to'] + \
                                           data_frame_comb['price back']
                cur_column = pd.Series(data_frame_comb['cur'])
                data_frame_comb = data_frame_comb.drop(['price to', 'price back',
                                                        'dep city back', 'arr city back',
                                                        'cur'], axis=1)
                data_frame_comb['cur'] = cur_column
                return data_frame_comb.sort_values('price').reset_index(drop=True)
            else:
                print 'No flights found back'
        return pd.DataFrame(dep_flight_info).sort_values('price to').reset_index(drop=True)


    def combine_info(self, flight_info_tags, flight_price_tags, is_one_way):
        """Allows users to enter data.
         Parameters
        ----------
        flight_info_tags : str
             A list of tags with flight information
        flight_price_tags : function
            A list of tags with price
        is_one_way : bool
            Defines names of the data in the dictionary
        Returns
        -------
        list
            A list with OrderedDict elements
        """
        cur = 'cur'
        if is_one_way:
            dep_date = 'dep date'
            dep_city = 'dep city'
            arr_city = 'arr city'
            dur = 'duration(to)'
            price = 'price to'
            needed_date = self.dep_date
        else:
            dep_date = 'date back'
            dep_city = 'dep city back'
            arr_city = 'arr city back'
            dur = 'duration(back)'
            price = 'price back'
            needed_date = self.arr_date

        combined_flight_info = []

        for index, _ in enumerate(flight_info_tags):
            tmp_date = datetime.strptime(flight_info_tags[index].
                                         xpath(".//td/text()")[0], '%a, %d %b %y')
            date = tmp_date.strftime('%d.%m.%Y')
            if date == needed_date:
                departure = datetime.strptime(flight_info_tags[index].
                                              xpath(".//td/text()")[1], '%H:%M')
                arrival = datetime.strptime(flight_info_tags[index].
                                            xpath(".//td/text()")[2], '%H:%M')
                flight_from = flight_info_tags[index].xpath(".//td/text()")[3]
                flight_to = flight_info_tags[index].xpath(".//td/text()")[4]
                price_cur = flight_price_tags[index].xpath(".//td/text()")[0].\
                    replace('Price:  ', '').split()

                duration = arrival - departure
                if arrival < departure:
                    duration += timedelta(days=1)

                cur_flight_info = OrderedDict()
                cur_flight_info[dep_date] = date
                cur_flight_info[dep_city] = flight_from
                cur_flight_info[arr_city] = flight_to
                cur_flight_info[dur] = str(duration)[:-3]
                cur_flight_info[price] = float(price_cur[0])
                cur_flight_info[cur] = price_cur[1]
                combined_flight_info.append(cur_flight_info)
        return combined_flight_info


def enter_check_data():
    """Performs data entry"""
    airports_with_desc, airports_codes = get_airports_desc()
    for airport in airports_with_desc:
        print airport
    dep_city = enter_data(message='Departure city code:    ',
                          is_correct_function=check_city,
                          air_codes=airports_codes)
    arr_city = enter_data(message='Arrival city code:    ',
                          is_correct_function=check_arr_city,
                          air_codes=airports_codes,
                          dep_city=dep_city)
    dep_date = enter_data(message='Departure date (dd.mm.yyyy):    ',
                          is_correct_function=check_dep_date)
    arr_date = enter_data(message='Arrival date (dd.mm.yyyy) - optional:    ',
                          is_correct_function=check_arr_date,
                          dep_date=dep_date)
    return dep_city, arr_city, dep_date, arr_date


def enter_data(message, is_correct_function, **kwargs):
    """Allows users to enter data.
     Parameters
    ----------
    message : str
        Message for input
    is_correct_function : function
        A check function for entered data
    **kwargs : dict
        Some optional parameters for check function
    Returns
    -------
    str
        Correct data
    """
    while True:
        inp_data = raw_input(message).strip()
        if is_correct_function(inp_data, **kwargs):
            return inp_data.upper()


def check_city(city, **kwargs):
    """Checks if airport code is entered correctly"""
    if not city.isalpha():
        print 'Airport code must consist of letters'
        return False
    city = city.upper()
    if city not in kwargs["air_codes"]:
        print 'Airport code must be in list of airport codes'
        return False
    return True


def check_arr_city(arr_city, **kwargs):
    """Checks if arrival city code satisfies the conditions
        and not the same as departure city code"""
    if not check_city(arr_city, **kwargs):
        return False
    if arr_city.upper() == kwargs['dep_city']:
        print 'Departure and arrival cities must be different'
        return False
    return True


def check_dep_date(dep_date):
    """Checks if departure date satisfies the conditions"""
    today_date = datetime.today()
    start = datetime(today_date.year, today_date.month, today_date.day)
    end = start + timedelta(days=365)
    return check_dates_restrictions(dep_date, start, end)


def check_arr_date(arr_date, **kwargs):
    """Checks if arrival date is empty or satisfies the conditions"""
    if arr_date == "":
        return True
    start = datetime.strptime(kwargs['dep_date'], '%d.%m.%Y') + timedelta(days=1)
    end = datetime.today() + timedelta(days=365)
    return check_dates_restrictions(arr_date, start, end)


def check_dates_restrictions(date, start, end):
    """Checks if date satisfies the conditions"""
    try:
        check = datetime.strptime(date, '%d.%m.%Y')
    except ValueError:
        print 'Set date as dd.mm.yyyy'
        return False
    if not start <= check <= end:
        print 'Date must be between ' + \
              str(start.strftime('%d.%m.%Y')) + \
              ' - ' + \
              str(end.strftime('%d.%m.%Y'))
        return False
    return True


def get_airports_desc():
    """Returns airports's codes and description"""
    html_tree = html.document_fromstring(get('http://www.flybulgarien.dk/en/timetable').content)
    airports_with_desc = html_tree.xpath("//div[@class='text-content']/p/text()")[2]\
        .replace("\n- ", "").split(", ")
    airports_codes = [x.split(" > ")[0] for x in airports_with_desc]
    return airports_with_desc, airports_codes


if __name__ == "__main__":
    FI = FlightInfo()
    while True:
        DEP_CITY, ARR_CITY, DEP_DATE, ARR_DATE = enter_check_data()
        FI.set_info(DEP_CITY, ARR_CITY, DEP_DATE, ARR_DATE)
        pd.options.display.max_columns = 10
        pd.options.display.expand_frame_repr = False
        print FI.get_flight_info()
        YES_OR_NO = raw_input('Continue? y/n    ')
        if YES_OR_NO == 'n':
            print 'Bye'
            break
