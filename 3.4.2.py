import math
from concurrent import futures
from statistics import mean
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from jinja2 import Environment, FileSystemLoader
import pdfkit

df_d = pd.read_csv("currencies.csv")


def start(arguments):
    year = arguments[1]
    vac_name = arguments[0]
    pr_df = pd.read_csv(f'created_csv_files\\part_{year}.csv')
    pr_df["salary"] = pr_df.apply(lambda row: get_salary(row["salary_from"], row["salary_to"], row["salary_currency"],
                                                         row["published_at"][:7].split("-")), axis=1)
    pr_df_vac = pr_df[pr_df["name"].str.contains(vac_name)]
    s_by_year, v_by_year, inp_v_s, inp_v_c = {year: []}, {year: 0}, {year: []}, {year: 0}
    s_by_year[year] = int(pr_df['salary'].mean())
    v_by_year[year] = len(pr_df)
    inp_v_s[year] = int(pr_df_vac['salary'].mean())
    inp_v_c[year] = len(pr_df_vac)
    a = [s_by_year, v_by_year, inp_v_s, inp_v_c]
    return a


def get_salary(salary_from, salary_to, salary_cur, d):
    d = d[1] + "/" + d[0]
    salary_cur1 = 0
    if salary_cur != "RUR" and salary_cur in ["BYN", "BYR", "EUR", "KZT", "UAH", "USD"]:
        salary_cur.replace("BYN", "BYR")
        date_row = df_d.loc[df_d["date"] == d]
        salary_cur1 = date_row[salary_cur].values[0]
    elif salary_cur == "RUR":
        salary_cur1 = 1
    if math.isnan(salary_from) and not (math.isnan(salary_to)):
        return salary_to * salary_cur1
    elif not (math.isnan(salary_from)) and math.isnan(salary_to):
        return salary_from * salary_cur1
    elif not (math.isnan(salary_from)) and not (math.isnan(salary_to)):
        return mean([salary_from, salary_to]) * salary_cur1


if __name__ == "__main__":
    def sort_dict(dict):
        sortedD = {}
        for key in sorted(dict):
            sortedD[key] = dict[key]
        return sortedD


    def sort_area_dict(dict):
        sortedT = sorted(dict.items(), key=lambda item: item[1], reverse=True)[:10]
        sortedD = {k: v for k, v in sortedT}
        return sortedD


    class UserInput:
        def __init__(self):
            self.file_name = input("Введите название файла: ")
            self.vacancy_name = input("Введите название профессии: ")


    class MakeCsv:
        def __init__(self, file_name):
            self.dataframe = pd.read_csv(file_name)
            self.dataframe["years"] = self.dataframe["published_at"].apply(
                lambda date: int(".".join(date[:4].split("-"))))
            self.years = list(self.dataframe["years"].unique())
            for year in self.years:
                data = self.dataframe[self.dataframe["years"] == year]
                data[["name", "salary_from", "salary_to",
                      "salary_currency", "area_name",
                      "published_at"]].to_csv(f"created_csv_files\\part_{year}.csv", index=False)


    class Report:
        def __init__(self, name, dicts):
            self.generate_image(name, dicts)
            self.generate_pdf(name, dicts)

        @staticmethod
        def generate_pdf(name, dicts):
            b = Environment(loader=FileSystemLoader('.'))
            template = b.get_template("pdf_template.html")
            pdf_template = template.render(
                {'name': name, 'by_year': dicts})
            options = {'enable-local-file-access': None}
            config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
            pdfkit.from_string(pdf_template, '3.4.2.pdf', configuration=config, options=options)

        @staticmethod
        def generate_image(name, dicts):
            nums = np.arange(len(dicts[0].keys()))
            width = 0.4
            list1 = nums - width / 2
            list2 = nums + width / 2
            fig = plt.figure()
            x = fig.add_subplot(221)
            x.set_title("Уровень зарплат по годам")
            x.bar(list1, dicts[0].values(), width, label="средняя з/п")
            x.bar(list2, dicts[1].values(), width, label=f"з/п {name.lower()}")
            x.set_xticks(nums, dicts[0].keys(), rotation="vertical")
            x.tick_params(axis="both", labelsize=8)
            x.legend(fontsize=8)
            x.grid(True, axis="y")
            x = fig.add_subplot(222)
            x.set_title("Количество вакансий по годам")
            x.bar(list1, dicts[2].values(), width, label="Количество вакансий")
            x.bar(list2, dicts[3].values(), width, label=f"Количество вакансий \n{name.lower()}")
            x.set_xticks(nums, dicts[2].keys(), rotation="vertical")
            x.tick_params(axis="both", labelsize=8)
            x.legend(fontsize=8)
            x.grid(True, axis="y")
            plt.tight_layout()
            plt.savefig("graph.png")


    input = UserInput()
    file, vac = input.file_name, input.vacancy_name
    make_csv = MakeCsv(file)
    dataframe = make_csv.dataframe
    years = make_csv.years
    dataframe["salary"] = dataframe.apply(lambda row: get_salary(row["salary_from"], row["salary_to"],
                                                                 row["salary_currency"],
                                                                 row["published_at"][:7].split("-")), axis=1)
    salaries_by_year, vacancies_by_year, inp_vacancy_salary, inp_vacancy_count = {}, {}, {}, {}
    executor = futures.ProcessPoolExecutor()
    processes = []
    for year in years:
        args = (vac, year)
        returned = executor.submit(start, args).result()
        salaries_by_year.update(returned[0])
        vacancies_by_year.update(returned[1])
        inp_vacancy_salary.update(returned[2])
        inp_vacancy_count.update(returned[3])
    print("Динамика уровня зарплат по годам:", sort_dict(salaries_by_year))
    print("Динамика количества вакансий по годам:", sort_dict(vacancies_by_year))
    print("Динамика уровня зарплат по годам для выбранной профессии:", sort_dict(inp_vacancy_salary))
    print("Динамика количества вакансий по годам для выбранной профессии:", sort_dict(inp_vacancy_count))
    dicts_list = [sort_dict(salaries_by_year), sort_dict(inp_vacancy_salary),
                          sort_dict(vacancies_by_year), sort_dict(inp_vacancy_count)]
    report = Report(input.vacancy_name, dicts_list)