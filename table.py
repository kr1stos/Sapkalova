import csv
import re
from prettytable import PrettyTable


class Salary:
    """Класс для представления зарплаты
    Attributes:
        salary_from (int): Нижняя граница вилки зарплат
        salary_to (int): Верхняя граница вилки зарплат
        salary_gross (str): Оклад указанный до вычета налогов
        salary_currency (str): Идентификатор валюты оклада
        salary_average (float): Средняя зарплата
        ru_valuta (dict): Словарь расшифровки валют
        currency_rub (dict): Словарь курса валют
    """
    ru_valuta = {'AZN': 'Манаты', 'BYR': 'Белорусские рубли', 'EUR': 'Евро', 'GEL': 'Грузинский лари',
                 'KGS': 'Киргизский сом', 'KZT': 'Тенге', 'RUR': 'Рубли', 'UAH': 'Гривны', 'USD': 'Доллары',
                 'UZS': 'Узбекский сум'}

    currency_rub = {"AZN": 35.68, "BYR": 23.91, "EUR": 59.90, "GEL": 21.74, "KGS": 0.76, "KZT": 0.13, "RUR": 1,
                    "UAH": 1.64, "USD": 60.66, "UZS": 0.0055}

    def __init__(self, vacancy):
        """Инициализирует объект Salary
        Args:
            vacancy (dict): Информация об вакансии, полученная в виде словаря из файла
        """
        self.salary_from = int(float(vacancy['salary_from']))
        self.salary_to = int(float(vacancy['salary_to']))
        self.salary_gross = 'Без вычета налогов' if vacancy['salary_gross'].lower() == 'true' else 'С вычетом налогов'
        self.salary_currency = vacancy['salary_currency']
        self.salary_average = Salary.currency_rub[self.salary_currency] * (self.salary_from + self.salary_to) / 2

    def __str__(self):
        """Форматирует данные о зарплате.
        Returns:
            str: данные о зарплате в виде 1 строки
        """
        return '{0:,} - {1:,} ({2}) ({3})'.format(self.salary_from, self.salary_to,
                                                  Salary.ru_valuta[self.salary_currency],
                                                  self.salary_gross).replace(',', ' ')


class Vacancy:
    """Класс для представления вакансии
    Attributes:
        index (int): Индекс вакансии
        name (str): Название вакансии
        description (str): Описание вакансии
        skills (str): Навыки
        key_skills (str): Навыки сокращенные до 100 символов
        skills_length (int): Кол-во символов в характеристике навыков
        experience_id (str): Опыт работы
        premium (str): Премиум-вакансия
        employer_name (str): Компания
        salary_class (Salary): Содержит информацию о зарплате
        salary (str): Информация о зарплате в строчном виде
        area_name (str): Регион
        published (str): Место публикации
        published_at (str): Время публикации
        order (list): Список переменных
        experience_weight_dictionary (dict): Словарь помощник для перевода опыта работы
        ru_experience (dict): Словарь перевода опыта работы
    """
    order = ['index', 'name', 'description', 'key_skills', 'experience_id', 'premium', 'employer_name', 'salary',
             'area_name', 'published_at']
    experience_weight_dictionary = {'Нет опыта': 1, 'От 1 года до 3 лет': 2, 'От 3 до 6 лет': 3, 'Более 6 лет': 4}
    ru_experience = {'noExperience': 'Нет опыта', 'between1And3': 'От 1 года до 3 лет', 'between3And6': 'От 3 до 6 лет',
                     'moreThan6': 'Более 6 лет'}

    def __init__(self, vacancy):
        """Инициализирует объект Vacancy
         Args:
            vacancy (dict): Информация об вакансии, полученная в виде словаря из файла
        """
        self.index = 0
        self.name = self.clearHTML(vacancy['name'])
        self.description = self.shortener(self.clearHTML(vacancy['description']))
        self.skills = vacancy['key_skills'].split('\n')
        self.key_skills = self.shortener(vacancy['key_skills'])
        self.skills_length = len(self.skills)
        self.experience_id = self.ru_experience[vacancy['experience_id']]
        self.premium = 'Да' if vacancy['premium'].lower() == 'true' else 'Нет'
        self.employer_name = vacancy['employer_name']
        self.salary_class = Salary(vacancy)
        self.salary = str(self.salary_class)
        self.area_name = vacancy['area_name']
        self.published = vacancy['published_at']
        self.published_at = '{0[2]}.{0[1]}.{0[0]}'.format(vacancy['published_at'][:10].split('-'))

    @staticmethod
    def clearHTML(string):
        """Удаляет теги и лишние пробелы
        Returns:
            str: Строка без тегов и лишних пробелов
        """
        result = re.sub(r'<.*?>', '', string)
        result = re.sub(r'\s+', ' ', result)
        return result.strip()

    @staticmethod
    def shortener(string):
        """Сокращает строку до 100 символов и в конец добавляет ...
        Returns:
            str: Строка из 103 символов с ...
        """
        return string if len(string) <= 100 else string[:100] + '...'

    @property
    def salary_average(self):
        """Берет среднюю зарплату из класса
        Returns:
            int: Средняя зарплата
        """
        return self.salary_class.salary_average

    @property
    def salary_currency(self):
        """Берет валюту зарплаты из класса
        Returns:
            str: Курс валюты
        """
        return self.salary_class.salary_currency

    @property
    def salary_from(self):
        """Берет нижнюю границу зарплаты из класса
        Returns:
            int: Нижняя граница зарплаты
        """
        return self.salary_class.salary_from

    @property
    def salary_to(self):
        """Берет верхнюю границу зарплаты из класса
        Returns:
            int: Верхняя граница зарплаты
        """
        return self.salary_class.salary_to

    @property
    def experience_weight(self):
        """Задает число(вес) для опыта работы
        Returns:
            int: Вес опыта работы
        """
        return self.experience_weight_dictionary[self.experience_id]

    def get_list(self):
        """Делает из данных лист
        Returns:
            list: Данные о вакансии
        """
        return [getattr(self, key) for key in self.order]


class DataSet:
    """Обрабатывает и считывает данные файла
    Attributes:
        file_name (str): Название файла
        filter_param (str): Параметр фильтрации
        sort_param (str): Параметр сортировки
        sort_reverse (str): Порядок сортировки
        sort_range (str): Диапазон вывода
        vacancies_objects (list): Лист с вакансиями
        ru_dictionary (dict): Словарь с переводом
        conditions_sort (dict): Словарь с характеристиками для вакансии для сортировки
    """
    ru_dictionary = {'Описание': 'description', 'Навыки': 'skills_length', 'Оклад': 'salary_average',
                     'Дата публикации вакансии': 'published', 'Опыт работы': 'experience_weight',
                     'Премиум-вакансия': 'premium',
                     'Идентификатор валюты оклада': 'salary_currency', 'Название': 'name',
                     'Название региона': 'area_name',
                     'Компания': 'employer_name'}
    conditions_sort = {'Навыки': lambda vacancy, value: all([skill in vacancy.skills for skill in value.split(', ')]),
                       'Оклад': lambda vacancy, value: vacancy.salary_from <= float(value) <= vacancy.salary_to,
                       'Дата публикации вакансии': lambda vacancy, value: vacancy.published_at == value,
                       'Опыт работы': lambda vacancy, value: vacancy.experience_id == value,
                       'Премиум-вакансия': lambda vacancy, value: vacancy.premium == value,
                       'Идентификатор валюты оклада': lambda vacancy, value: Salary.ru_valuta[
                                                                                 vacancy.salary_currency] == value,
                       'Название': lambda vacancy, value: vacancy.name == value,
                       'Название региона': lambda vacancy, value: vacancy.area_name == value,
                       'Компания': lambda vacancy, value: vacancy.employer_name == value}

    def __init__(self, file_name, filter_param, sort_param, sort_reverse, sort_range):
        """Инициализирует объект DataSet
        Args:
             file_name (str): Название файла
            filter_param (str): Параметр фильтрации
            sort_param (str): Параметр сортировки
            sort_reverse (str): Порядок сортировки
            sort_range (str): Диапазон вывода
        """
        self.file_name = file_name
        self.filter_param = filter_param
        self.sort_param = sort_param
        self.sort_reverse = sort_reverse
        self.sort_range = sort_range
        self.vacancies_objects = []

    def csv_reader(self):
        """Считывает файл, записывает данные в лист
        Returns:
            list: Данные файла в виде словарей в листе
        """
        h = []
        with open(self.file_name, mode='r', encoding='utf-8-sig') as file:
            reader = csv.reader(file)
            for index, row in enumerate(reader):
                if index == 0:
                    h = row
                    csv_h_length = len(row)
                elif '' not in row and len(row) == csv_h_length:
                    self.vacancies_objects.append(Vacancy(dict(zip(h, row))))
        if len(self.vacancies_objects) == 0:
            if len(h) == 0:
                print('Пустой файл')
            else:
                print('Нет данных')
            exit()

    def get_rows(self):
        """Объединяет данные о вакансиях в list
        Returns:
            list: Данные вакансий
        """
        return [vacancy.get_list() for vacancy in self.vacancies_objects]

    def filter_rows(self):
        """Фильтрует вакансии
        """
        if len(self.filter_param) == 0:
            return
        self.vacancies_objects = list(
            filter(lambda vacancy: self.conditions_sort[self.filter_param[0]](vacancy, self.filter_param[1]),
                   self.vacancies_objects))

    def sort_rows(self):
        """Сортирует вакансии в нужном порядке
        """
        if self.sort_param != '':
            self.vacancies_objects.sort(key=lambda a: getattr(a, DataSet.ru_dictionary[self.sort_param]),
                                        reverse=self.sort_reverse)
        elif self.sort_param == '' and self.sort_reverse:
            self.vacancies_objects.reverse()

    def get_range(self):
        """Сокращает данные о вакансиях до нужного диапазона
        Returns:
            list: Данные вакансий
        """
        vacancies_temp = []
        length = len(self.sort_range)
        for index, vacancy in enumerate(self.vacancies_objects):
            if (length > 1 and self.sort_range[0] <= index < self.sort_range[1]) or (
                    length == 1 and self.sort_range[0] <= index) or length == 0:
                vacancy.index = index + 1
                vacancies_temp.append(vacancy)
        self.vacancies_objects = vacancies_temp


class InputConnect:
    """Отвечает за обработку параметров вводимых пользователем: фильтры, сортировка, диапазон вывода,
    требуемые столбцы, а также за печать таблицы на экран
    Attributes:
        errors (list): Ошибки
        file_name (str): Имя файла
        filter_param (str): Параметр фильтрации
        sort_param (str): Параметр сортировки
        sort_reverse (bool): Определяет порядок сортировки
        sort_range (list): Диапозон вывода
        table_fields (list): Требуемые столбцы
        table_h (list): Список со столбцами
    """
    table_h = ['№', 'Название', 'Описание', 'Навыки', 'Опыт работы', 'Премиум-вакансия', 'Компания', 'Оклад',
               'Название региона', 'Дата публикации вакансии']

    def __init__(self):
        """Инициализирует объект InputConnect
        """
        self.errors = []
        self.file_name = input('Введите название файла: ')
        self.filter_param = self.parse_filter_param(input('Введите параметр фильтрации: '))
        self.sort_param = self.parse_sort_param(input('Введите параметр сортировки: '))
        self.sort_reverse = self.parse_sort_reverse(input('Обратный порядок сортировки (Да / Нет): '))
        self.sort_range = self.parse_sort_range(input('Введите диапазон вывода: '))
        self.table_fields = self.parse_table_fields(input('Введите требуемые столбцы: '))
        if len(self.errors) != 0:
            print(self.errors[0])
            exit()
        data_set = DataSet(self.file_name, self.filter_param, self.sort_param, self.sort_reverse, self.sort_range)
        data_set.csv_reader()
        data_set.filter_rows()
        data_set.sort_rows()
        data_set.get_range()
        rows = data_set.get_rows()
        if len(rows) == 0:
            print('Ничего не найдено')
        else:
            table = PrettyTable(align='l', field_names=InputConnect.table_h, max_width=20, hrules=1)
            table.add_rows(rows)
            print(table.get_string(fields=self.table_fields))

    def parse_filter_param(self, filter_param):
        """Обрабатывает ввод пользователя и выводит ошибку, если данные введены некорректно.
        Returns:
            list: Параметры фильтрации
        """
        if filter_param == '':
            return []
        if ': ' not in filter_param:
            self.errors.append('Формат ввода некорректен')
            return []
        filter_param = filter_param.split(': ')
        if filter_param[0] not in list(DataSet.conditions_sort.keys()):
            self.errors.append('Параметр поиска некорректен')
            return []
        return filter_param

    def parse_sort_reverse(self, sort_reverse):
        """Обрабатывает ввод пользователя и выводит ошибку, если данные введены некорректно
        Returns:
            bool: Вид порядка сортировки
        """
        if sort_reverse not in ('', 'Да', 'Нет'):
            self.errors.append('Порядок сортировки задан некорректно')
        return True if sort_reverse == 'Да' else False

    def parse_sort_param(self, sort_param):
        """Обрабатывает ввод пользователя и выводит ошибку, если данные введены некорректно
        Returns:
            list: Параметры сортировки
        """
        if sort_param not in InputConnect.table_h + ['']:
            self.errors.append('Параметр сортировки некорректен')
        return sort_param

    def parse_sort_range(self, sort_range):
        """Обрабатывает ввод пользователя и выводит ошибку, если данные введены некорректно
        Returns:
            list: Диапазон сортировки
        """
        return [] if sort_range == '' else [int(limit) - 1 for limit in sort_range.split()]

    def parse_table_fields(self, table_fields):
        """Обрабатывает ввод пользователя и выводит ошибку, если данные введены некорректно
        Returns:
            list: Заголовки столбцов
        """
        return InputConnect.table_h if table_fields == '' else ['№'] + [a for a in table_fields.split(', ') if
                                                                        a in InputConnect.table_h]


def get_answer():
    """Запускает программу
    """
    InputConnect()
