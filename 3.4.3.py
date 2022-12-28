import math
from statistics import mean
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from jinja2 import Environment, FileSystemLoader
import pdfkit
from matplotlib import ticker


def sort_area_dict(dict):
    sortedT = sorted(dict.items(), key=lambda item: item[1], reverse=True)[:10]
    sortedD = {k: v for k, v in sortedT}
    return sortedD


def sort_dict(dict):
    sortedD = {}
    for key in sorted(dict):
        sortedD[key] = dict[key]
    return sortedD


def get_salary(salary_from, salary_to, salary_cur, d):
    d = d[1] + "/" + d[0]
    salary_cur1 = 0
    if salary_cur != "RUR" and salary_cur in ["BYN", "BYR", "EUR", "KZT", "UAH", "USD"]:
        salary_cur.replace("BYN", "BYR")
        date_row = df_date.loc[df_date["date"] == d]
        salary_cur1 = date_row[salary_cur].values[0]
    elif salary_cur == "RUR":
        salary_cur1 = 1
    if math.isnan(salary_from) and not (math.isnan(salary_to)):
        return salary_to * salary_cur1
    elif not (math.isnan(salary_from)) and math.isnan(salary_to):
        return salary_from * salary_cur1
    elif not (math.isnan(salary_from)) and not (math.isnan(salary_to)):
        return mean([salary_from, salary_to]) * salary_cur1


class UserInput:
    def __init__(self):
        self.file_name = input("Введите название файла: ")
        self.vacancy_name = input("Введите название профессии: ")
        self.region = input("Введите название региона: ")


class Report:
    def __init__(self, vac_name, region, dicts_by_area, dicts_by_year, vac_with_others):
        self.generate_image(vac_name, region, dicts_by_area, dicts_by_year, vac_with_others)
        self.generate_pdf(vac_name, region, dicts_by_area, dicts_by_year)

    @staticmethod
    def generate_pdf(vac_name, region, dicts_by_area, dicts_by_year):
        b = Environment(loader=FileSystemLoader('.'))
        template = b.get_template("pdf_template.html")
        pdf_template = template.render(
            {'name': vac_name, 'reg': region, 'by_area': dicts_by_area, 'by_year': dicts_by_year,
             'keys_0_area': list(dicts_by_area[0].keys()), 'values_0_area': list(dicts_by_area[0].values()),
             'keys_1_area': list(dicts_by_area[1].keys()), 'values_1_area': list(dicts_by_area[1].values())})
        options = {'enable-local-file-access': None}
        config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
        pdfkit.from_string(pdf_template, 'report.pdf', configuration=config, options=options)

    @staticmethod
    def generate_image(vac_name, region, dicts_by_area, dicts_by_year, vac_with_others):
        cities = np.arange(len(dicts_by_area[0].keys()))
        cities_names = {}
        for key, value in dicts_by_area[0].items():
            if "-" in key or " " in key:
                key = key.replace("-", "-\n")
                key = key.replace(" ", "\n")
            cities_names[key] = value
        nums = np.arange(len(dicts_by_year[0].keys()))
        width = 0.4
        list1 = nums
        fig = plt.figure()
        x = fig.add_subplot(221)
        x.set_title("Уровень зарплат по годам")
        x.bar(list1, dicts_by_year[0].values(), width, label=f"з/п {vac_name.lower()} {region.lower()}")
        x.set_xticks(nums, dicts_by_year[0].keys(), rotation="vertical")
        x.tick_params(axis="both", labelsize=8)
        x.legend(fontsize=8)
        x.grid(True, axis="y")
        x = fig.add_subplot(222)
        x.set_title("Количество вакансий по годам")
        x.bar(list1, dicts_by_year[1].values(), width,
              label=f"Количество вакансий \n{vac_name.lower()} {region.lower()}")
        x.set_xticks(nums, dicts_by_year[1].keys(), rotation="vertical")
        x.tick_params(axis="both", labelsize=8)
        x.legend(fontsize=8)
        x.grid(True, axis="y")
        x = fig.add_subplot(223)
        x.set_title("Уровень зарплат по городам")
        width = 0.8
        x.barh(cities, dicts_by_area[0].values(), width, align="center")
        x.set_yticks(cities, labels=cities_names.keys(), horizontalalignment="right", verticalalignment="center")
        x.tick_params(axis="x", labelsize=8)
        x.tick_params(axis="y", labelsize=6)
        x.xaxis.set_major_locator(ticker.MultipleLocator(100000))
        x.invert_yaxis()
        x.grid(True, axis="x")
        x = fig.add_subplot(224)
        x.set_title("Доля вакансий по городам")
        dicts_by_area[1]["Другие"] = vac_with_others
        x.pie(dicts_by_area[1].values(), labels=dicts_by_area[1].keys(), textprops={'size': 6},
              colors=["#ff8006", "#28a128", "#1978b5", "#0fbfd0", "#bdbe1c", "#808080", "#e478c3", "#8d554a",
                      "#9567be",
                      "#d72223", "#1978b5", "#ff8006"])
        x.axis('equal')
        plt.tight_layout()
        plt.savefig("graph.png")


input = UserInput()
file, vac, reg = input.file_name, input.vacancy_name, input.region
dataframe = pd.read_csv(file)
dataframe["years"] = dataframe["published_at"].apply(lambda date: int(".".join(date[:4].split("-"))))
years = list(dataframe["years"].unique())
salaries_areas, vacancies_areas, inp_vacancy_salary, inp_vacancy_count = {}, {}, {}, {}
df_date = pd.read_csv("CB_Currency.csv")
dataframe["salary"] = dataframe.apply(lambda row: get_salary(row["salary_from"], row["salary_to"],
                                                             row["salary_currency"],
                                                             row["published_at"][:7].split("-")), axis=1)
vacancies = len(dataframe)
dataframe["count"] = dataframe.groupby("area_name")['area_name'].transform("count")
df_norm = dataframe[dataframe['count'] >= 0.01 * vacancies]
cities = list(df_norm["area_name"].unique())
others = len(dataframe[dataframe['count'] < 0.01 * vacancies]) / vacancies
for city in cities:
    df_s = df_norm[df_norm['area_name'] == city]
    salaries_areas[city] = int(df_s['salary'].mean())
    vacancies_areas[city] = round(len(df_s) / len(dataframe), 4)
dataframe_vac = dataframe[dataframe["name"].str.contains(vac)]
for year in years:
    dataframe_v_s = dataframe_vac[(dataframe_vac['years'] == year) & (dataframe_vac['area_name'] == reg)]
    if not dataframe_v_s.empty:
        inp_vacancy_salary[year] = int(dataframe_v_s['salary'].mean())
        inp_vacancy_count[year] = len(dataframe_v_s)
print("Уровень зарплат по городам (в порядке убывания):", sort_area_dict(salaries_areas))
print("Доля вакансий по городам (в порядке убывания):", sort_area_dict(vacancies_areas))
print("Динамика уровня зарплат по годам для выбранной профессии и региона:", sort_dict(inp_vacancy_salary))
print("Динамика количества вакансий по годам для выбранной профессии и региона:", sort_dict(inp_vacancy_count))
dicts_list_by_area = [sort_area_dict(salaries_areas), sort_area_dict(vacancies_areas)]
dicts_list_by_year = [sort_dict(inp_vacancy_salary), sort_dict(inp_vacancy_count)]
report = Report(vac, reg, dicts_list_by_area, dicts_list_by_year, others)
