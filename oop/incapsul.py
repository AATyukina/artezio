class NameSurname:
    def __init__(self, name, surname):
        self.__name = name
        self.__surname = surname

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name=str):
        if name.isalpha():
            self.__name = name
    @property
    def surname(self):
        return self.__surname

    @surname.setter
    def surname(self, surname=str):
        if surname.isalpha():
            self.__surname = surname


my_data = NameSurname("Orina", "Tukina")
print(my_data.name)
print(my_data.surname)
my_data.name = "Arina"
my_data.surname = "Tyukina"
print(my_data.name)
print(my_data.surname)
