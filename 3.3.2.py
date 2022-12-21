import math
import os
import pandas as pd
from multiprocessing import Process, Queue

pd.options.mode.chained_assignment = None


class UserInput:
    def __init__(self):
        self.fileName = 'csv_files_dif_currencies'
        self.jobName = 'Аналитик'


def fill_df(df, currencies):
    curr = list(currencies.loc[:, ~currencies.columns.isin(['date', 'Unnamed: 0'])].columns.values) + ['RUR']
    df = df[df['salary_currency'].isin(curr)]
    df['salary'] = df.apply(lambda x: get_salary(x, currencies), axis=1)
    df.drop(columns=['salary_from', 'salary_to', 'salary_currency'], inplace=True)
    df = df.reindex(columns=['name', 'salary', 'area_name', 'published_at'], copy=True)
    return df


def calc_year_stat_mp(fileName, jobName, q, currencies):
    df = pd.read_csv(fileName)
    df = fill_df(df, currencies)
    data_job = df[df['name'].str.contains(jobName, case=False)]
    q.put([int(df['published_at'].values[0][:4]), df.shape[0], math.floor(df['salary'].mean()), data_job.shape[0],
           math.floor(data_job['salary'].mean()), df])


def get_salary(x, currencies):
    salary_from, salary_to, salary_currency, published_at = x.loc['salary_from'], x.loc['salary_to'], \
                                                            x.loc['salary_currency'], x.loc['published_at']
    d = published_at[:7]
    if math.isnan(salary_to) or math.isnan(salary_from):
        salary = salary_to if math.isnan(salary_from) else salary_from
    else:
        salary = math.floor((salary_from + salary_to) / 2)
    if salary_currency == 'RUR':
        return salary
    return math.floor(salary * currencies.loc[currencies['date'] == d][salary_currency].values[0])


def calc_year_stat_mp1():
    global year_by_num, year_by_salary, year_by_num_job, year_by_salary_job, df_res
    process = []
    q = Queue()
    currencies = pd.read_csv('currencies.csv')
    for file_name in os.listdir(user_input.fileName):
        a = Process(target=calc_year_stat_mp,
                    args=(user_input.fileName + '/' + file_name, user_input.jobName, q, currencies.copy()))
        process.append(a)
        a.start()
    for a in process:
        a.join(1)
        d = q.get()
        year_by_num[d[0]] = d[1]
        year_by_salary[d[0]] = d[2]
        year_by_num_job[d[0]] = d[3]
        year_by_salary_job[d[0]] = d[4]
        df_res.append(d[5])
    year_by_num = dict(sorted(year_by_num.items(), key=lambda i: i[0]))
    year_by_salary = dict(sorted(year_by_salary.items(), key=lambda i: i[0]))
    year_by_num_job = dict(sorted(year_by_num_job.items(), key=lambda i: i[0]))
    year_by_salary_job = dict(sorted(year_by_salary_job.items(), key=lambda i: i[0]))


def area_stats():
    global vac_num_by_area, salary_by_area
    df = pd.concat(df_res, ignore_index=True)
    all_vac_num = df.shape[0]
    percent = int(all_vac_num * 0.01)
    d = df.groupby('area_name')['name'] \
        .count().apply(lambda x: round(x / all_vac_num, 4)).sort_values(ascending=False).head(10).to_dict()
    vac_num_by_area = d
    area_vac_num = df.groupby('area_name')['name'] \
        .count().loc[lambda x: x > percent].to_dict()
    d = df.loc[df['area_name'].isin(area_vac_num.keys())] \
        .groupby('area_name')['salary'].mean().apply(lambda x: math.floor(x)).sort_values(ascending=False).head(10) \
        .to_dict()
    salary_by_area = d


def print_stats():
    print(f'Динамика уровня зарплат по годам: {year_by_salary}')
    print(f'Динамика количества вакансий по годам: {year_by_vac_num}')
    print(f'Динамика уровня зарплат по годам для выбранной профессии: {year_by_salary_job}')
    print(f'Динамика количества вакансий по годам для выбранной профессии: {year_by_vac_num_job}')
    print(f'Уровень зарплат по городам (в порядке убывания): {salary_by_area}')
    print(f'Доля вакансий по городам (в порядке убывания): {vac_num_by_area}')


if __name__ == '__main__':
    year_by_vac_num = {}
    year_by_salary = {}
    year_by_vac_num_job = {}
    year_by_salary_job = {}
    vac_num_by_area = {}
    salary_by_area = {}
    df_res = []
    user_input = UserInput()
    calc_year_stat_mp1()
    area_stats()
    print_stats()
