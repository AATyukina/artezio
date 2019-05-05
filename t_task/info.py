import requests
from lxml import html
import datetime
import pandas as pd
import collections


class FlightInfo:
    href = 'http://www.flybulgarien.dk/en/search?departure-city=%s&arrival-city=%s&' \
           'departure-date=%s&arrival-date=%s&adults-children=1'

    def __init__(self):
        self.airp_desc, self.airp_codes = self.getAirportsDesc()
        self._dep_city = None
        self._arr_city = None
        self._dep_date = None
        self._arr_date = None

    @property
    def dep_city(self):
        return self._dep_city

    @property
    def arr_city(self):
        return self._arr_city

    @property
    def dep_date(self):
        return self._dep_date

    @property
    def arr_date(self):
        return self._arr_date

    @dep_city.setter
    def dep_city(self, value):
        if not value.isalpha():
            raise ValueError("Airport code must consist of letters")
        value = value.upper()
        if value not in self.airp_codes:
            raise ValueError("Airport code must be in list of airport codes")
        self._dep_city = value

    @arr_city.setter
    def arr_city(self, value):
        if not value.isalpha():
            raise ValueError("Airport code must consist of letters")
        value = value.upper()
        if value == self._dep_city:
            raise ValueError("Arrival city airport code must be different from departure city airport code")
        if value not in self.airp_codes:
            raise ValueError("Airport code must be in list of airport codes")
        self._arr_city = value

    @dep_date.setter
    def dep_date(self, value):
        try:
            check = datetime.datetime.strptime(value, '%d.%m.%Y')
        except:
            raise ValueError("Set departure date as dd.mm.yyyy")
        start = datetime.datetime.today()
        end = start + datetime.timedelta(days=365)
        if not start <= check <= end:
            raise ValueError("Incorrect date")
        self._dep_date = value

    @arr_date.setter
    def arr_date(self, value):
        if value == "":
            self._arr_date = value
            return
        try:
            check = datetime.datetime.strptime(value, '%d.%m.%Y')
        except:
            raise ValueError("Set departure date as dd.mm.yyyy")
        start = datetime.datetime.strptime(self._dep_date, '%d.%m.%Y') + datetime.timedelta(days=1)
        end = datetime.datetime.today() + datetime.timedelta(days=365)
        if not start <= check <= end:
            raise ValueError("Incorrect date")
        self._arr_date = value

    def getFlightInfo(self):
        flight_info = self.get_inner_href()
        if not self.check_available(flight_info):
            return "No flights available"
        if self.arr_date == "":
            return self._get_flight_info_not_return(flight_info)
        else:
            return self._get_flight_info_return(flight_info)

    def check_available(self, flight_info):
        try:
            for check in flight_info:
                for el in check.xpath(".//td/text()"):
                    if 'No available flights found.' in el:
                        return False
        except:
            pass
        return True

    def get_inner_href(self):
        first_html = requests.get(self.href % (self.dep_city, self.arr_city, self.dep_date, self.arr_date))
        htmltree = html.document_fromstring(first_html.content)
        flight_page = requests.get(htmltree.xpath("//iframe[@name='flybulgarienintraweb']/@src")[0])
        htmltree = html.document_fromstring(flight_page.content)
        flight_info = htmltree.xpath("//table[@id='flywiz_tblQuotes']/tr")
        return flight_info

    def _get_flight_info_not_return(self, flight_info):
        not_return_flights = []
        for index in range(2, len(flight_info) - 1):
            if index % 2 == 0:
                date = flight_info[index].xpath(".//td/text()")[0]
                departure = flight_info[index].xpath(".//td/text()")[1]
                arrival = flight_info[index].xpath(".//td/text()")[2]
                flight_from = flight_info[index].xpath(".//td/text()")[3]
                flight_to = flight_info[index].xpath(".//td/text()")[4]
                duration = datetime.datetime.strptime(arrival, '%H:%M') - datetime.datetime.strptime(departure, '%H:%M')
            else:
                price = flight_info[index].xpath(".//td/text()")[0].replace('Price:  ', '').split()
                d = collections.OrderedDict()
                d['dep date'] = date
                d['dep city'] = flight_from
                d['arr city'] = flight_to
                d['duration(h)'] = duration
                d['price'] = float(price[0])
                d['cur'] = price[1]
                not_return_flights.append(d)

        df = pd.DataFrame(not_return_flights)
        pd.options.display.max_columns = 10
        return df.sort_values('price').reset_index(drop=True)

    def _get_flight_info_return(self, flight_info):
        return_flights_go = []
        return_flights_back = []
        is_info = True

        for index in range(2, len(flight_info)):
            try:
                if is_info:
                    date = flight_info[index].xpath(".//td/text()")[0]
                    departure = flight_info[index].xpath(".//td/text()")[1]
                    arrival = flight_info[index].xpath(".//td/text()")[2]
                    flight_from = flight_info[index].xpath(".//td/text()")[3]
                    flight_to = flight_info[index].xpath(".//td/text()")[4]
                    duration = datetime.datetime.strptime(arrival, '%H:%M') - datetime.datetime.strptime(departure,
                                                                                                         '%H:%M')
                    is_info = False
                else:
                    price = flight_info[index].xpath(".//td/text()")[0].replace('Price:  ', '').split()
                    d = collections.OrderedDict()
                    d['dep date'] = date
                    d['dep city'] = flight_from
                    d['arr city'] = flight_to
                    d['duration(h) go'] = duration
                    d['price_to'] = float(price[0])

                    return_flights_go.append(d)
                    is_info = True
                    start_index = index
            except:
                is_info = True
                start_index = index
                break

        for index in range(start_index, len(flight_info)):
            try:
                if is_info:
                    date = flight_info[index].xpath(".//td/text()")[0]
                    departure = flight_info[index].xpath(".//td/text()")[1]
                    arrival = flight_info[index].xpath(".//td/text()")[2]
                    duration = datetime.datetime.strptime(arrival, '%H:%M') - datetime.datetime.strptime(departure,
                                                                                                         '%H:%M')
                    is_info = False
                else:
                    price = flight_info[index].xpath(".//td/text()")[0].replace('Price:  ', '').split()
                    d = collections.OrderedDict()
                    d['arr date'] = date
                    d['duration(h) back'] = duration
                    d['price_back'] = float(price[0])
                    cur = price[1]
                    is_info = True
                    return_flights_back.append(d)
            except:
                pass

        #собираются комбинации различных перелетов
        total_flight_combinations = []
        for go in return_flights_go:
            for back in return_flights_back:
                total_flight_combinations.append(collections.OrderedDict(list(go.items()) + list(back.items())))

        #формируется цена
        df = pd.DataFrame(total_flight_combinations)
        df['price'] = df['price_to'] + df['price_back']
        df = df.drop(['price_to', 'price_back'], axis=1)
        df['cur'] = cur
        pd.options.display.max_columns = 10
        return df.sort_values('price').reset_index(drop=True)

    def getAirportsDesc(self):
        first_html = requests.get('http://www.flybulgarien.dk/en/timetable')
        htmltree = html.document_fromstring(first_html.content)
        airports_with_desc = htmltree.xpath("//div[@class='text-content']/p/text()")[2].replace("\n- ", "").split(", ")
        airports_codes = [x.split(" > ")[0] for x in airports_with_desc]
        return airports_with_desc, airports_codes


if __name__ == "__main__":
    while True:
        fi = FlightInfo()
        for x in fi.airp_desc: print(x)
        while True:
            try:
                fi.dep_city = input('Departure city code:    ')
                break
            except ValueError as e:
                print(str(e))

        while True:
            try:
                fi.arr_city = input('Arrival city code:   ')
                break
            except ValueError as e:
                print(str(e))

        while True:
            try:
                fi.dep_date = input('Departure date:    ')
                break
            except ValueError as e:
                print(str(e))

        while True:
            try:
                fi.arr_date = input('Arrival date (optional):      ')
                break
            except ValueError as e:
                print(str(e))

        print(fi.getFlightInfo())

        yes_or_no = input("Continue? y/n    ")
        if yes_or_no == "n":
            print("Bye")
            break
