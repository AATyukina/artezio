from requests import get, exceptions
from lxml import html
from datetime import datetime, timedelta
import pandas as pd
from collections import OrderedDict
from itertools import product


class FlightInfo:
    def __init__(self):
        self.dep_city = None
        self.arr_city = None
        self.dep_date = None
        self.arr_date = None

    def set_info(self, dep_city_checked, arr_city_checked, dep_date_checked, arr_date_checked):
        self.dep_city = dep_city_checked
        self.arr_city = arr_city_checked
        self.dep_date = dep_date_checked
        self.arr_date = arr_date_checked

    def get_flight_info(self):
        # получили данные по перелетам
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

        # выделяем данные по перелетам
        flight_table = html_tree.xpath("//table[@id='flywiz_tblQuotes']")[0]
        dep_flight_info_tags = flight_table.xpath("./tr[contains(@id,'flywiz_rinf')]")
        dep_flight_price_tags = flight_table.xpath("./tr[contains(@id,'flywiz_rprc')]")
        arr_flight_info_tags = flight_table.xpath("./tr[contains(@id,'flywiz_irinf')]")
        arr_flight_price_tags = flight_table.xpath("./tr[contains(@id,'flywiz_irprc')]")

        if not dep_flight_info_tags and not arr_flight_info_tags or not dep_flight_info_tags:
            return 'No flights available'

        dep_flight_info = self.combine_info(dep_flight_info_tags, dep_flight_price_tags,
                                            self.dep_date, dep_date='dep date',
                                            dep_city='dep city', arr_city='arr city',
                                            price='price to', dur='duration(to)')
        if not dep_flight_info:
            return 'No flights available'

        if self.arr_date:
            arr_flight_info = self.combine_info(arr_flight_info_tags, arr_flight_price_tags,
                                                self.arr_date, dep_date='date back',
                                                dep_city='dep city back', arr_city='arr city back',
                                                price='price back', dur='duration(back)')
            if arr_flight_info:
                total_flight_combinations = []
                for go, back in product(dep_flight_info, arr_flight_info):
                    total_flight_combinations.append(OrderedDict(list(go.items()) + list(back.items())))

                df = pd.DataFrame(total_flight_combinations)
                df['price'] = df['price to'] + df['price back']
                s = pd.Series(df['cur'])
                df = df.drop(['price to', 'price back', 'dep city back', 'arr city back', 'cur'], axis=1)
                df['cur'] = s
                return df.sort_values('price').reset_index(drop=True)
            else:
                print('No flights found back')
        return pd.DataFrame(dep_flight_info).sort_values('price to').reset_index(drop=True)

    def combine_info(self, flight_info_tags,
                     flight_price_tags, needed_date,
                     dep_date='', dep_city='',
                     arr_city='', dur='duration(h)',
                     price='', cur='cur'):
        combined_flight_info = []

        for index in range(len(flight_info_tags)):
            tmp_date = datetime.strptime(flight_info_tags[index].xpath(".//td/text()")[0], '%a, %d %b %y')
            date = tmp_date.strftime('%d.%m.%Y')
            if date == needed_date:
                departure = flight_info_tags[index].xpath(".//td/text()")[1]
                arrival = flight_info_tags[index].xpath(".//td/text()")[2]
                flight_from = flight_info_tags[index].xpath(".//td/text()")[3]
                flight_to = flight_info_tags[index].xpath(".//td/text()")[4]
                duration = datetime.strptime(arrival, '%H:%M') - datetime.strptime(departure, '%H:%M')
                price_cur = flight_price_tags[index].xpath(".//td/text()")[0].replace('Price:  ', '').split()

                d = OrderedDict()
                d[dep_date] = date
                d[dep_city] = flight_from
                d[arr_city] = flight_to
                d[dur] = duration
                d[price] = float(price_cur[0])
                d[cur] = price_cur[1]
                combined_flight_info.append(d)
        return combined_flight_info


def enter_check_data():
    airports_with_desc, airports_codes = get_airports_desc()
    for x in airports_with_desc:
        print(x)
    dep_city = enter_data(message='Departure city code:    ',
                          is_correct_function=check_city,
                          air_codes=airports_codes)
    arr_city = enter_data(message='Arrival city code:    ',
                          is_correct_function=check_arr_city,
                          air_codes=airports_codes,
                          dep_city=dep_city)
    dep_date = enter_data(message='Departure date:    ',
                          is_correct_function=check_dep_date)
    arr_date = enter_data(message='Arrival date(optional):    ',
                          is_correct_function=check_arr_date,
                          dep_date=dep_date)
    return dep_city, arr_city, dep_date, arr_date


def enter_data(message, is_correct_function, **kwargs):
    while True:
        var = input(message)
        if is_correct_function(var, **kwargs):
            return var.upper()


def check_city(var, **kwargs):
    if not var.isalpha():
        print("Airport code must consist of letters")
        return False
    var = var.upper()
    if var not in kwargs["air_codes"]:
        print("Airport code must be in list of airport codes")
        return False
    return True


def check_arr_city(var, **kwargs):
    if not check_city(var, **kwargs):
        return False
    if var.upper() == kwargs['dep_city']:
        print('Departure and arrival cities must be different')
        return False
    return True


def check_dep_date(var):
    start = datetime.today()
    end = start + timedelta(days=365)
    return check_dates_restrictions(var, start, end)


def check_arr_date(var, **kwargs):
    if var == "":
        return True
    start = datetime.strptime(kwargs['dep_date'], '%d.%m.%Y') + timedelta(days=1)
    end = datetime.today() + timedelta(days=365)
    return check_dates_restrictions(var, start, end)


def check_dates_restrictions(var, start, end):
    try:
        check = datetime.strptime(var, '%d.%m.%Y')
    except ValueError:
        print("Set date as dd.mm.yyyy")
        return False
    if not start <= check <= end:
        print("Incorrect date")
        return False
    return True


def get_airports_desc():
    html_tree = html.document_fromstring(get('http://www.flybulgarien.dk/en/timetable').content)
    airports_with_desc = html_tree.xpath("//div[@class='text-content']/p/text()")[2].replace("\n- ", "").split(", ")
    airports_codes = [x.split(" > ")[0] for x in airports_with_desc]
    return airports_with_desc, airports_codes


if __name__ == "__main__":
    fi = FlightInfo()
    while True:
        dep_city, arr_city, dep_date, arr_date = enter_check_data()
        fi.set_info(dep_city, arr_city, dep_date, arr_date)
        pd.options.display.max_columns = 10
        print(fi.get_flight_info())
        yes_or_no = input("Continue? y/n    ")
        if yes_or_no == "n":
            print("Bye")
            break
