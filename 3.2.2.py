import pandas as pd
from multiprocessing import Process, Queue

a = []


def start(vac_name, year, queue):
    pr_df = pd.read_csv(f'created_csv_files\\part_{year}.csv')
    pr_df.loc[:, 'salary'] = pr_df.loc[:, ['salary_from', 'salary_to']].mean(axis=1)
    pr_df_vac = pr_df[pr_df["name"].str.contains(vac_name)]
    s_by_year, v_by_year, inp_v_s, inp_v_c = {year: []}, {year: 0}, {year: []}, {year: 0}
    s_by_year[year] = int(pr_df['salary'].mean())
    v_by_year[year] = len(pr_df)
    inp_v_s[year] = int(pr_df_vac['salary'].mean())
    inp_v_c[year] = len(pr_df_vac)
    d_list = [s_by_year, v_by_year, inp_v_s, inp_v_c]
    queue.put(d_list)


if __name__ == "__main__":

    def sort_area_dict(dict):
        sortedT = sorted(dict.items(), key=lambda item: item[1], reverse=True)[:10]
        sortedD = {k: v for k, v in sortedT}
        return sortedD


    def sort_dict(dict):
        sortedD = {}
        for key in sorted(dict):
            sortedD[key] = dict[key]
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


    pd.set_option("expand_frame_repr", False)
    input = UserInput()
    file, vac = input.file_name, input.vacancy_name
    make_csv = MakeCsv(file)
    df = make_csv.dataframe
    years = make_csv.years
    df["published_at"] = df["published_at"].apply(lambda date: int(".".join(date[:4].split("-"))))
    df['salary'] = df.loc[:, ['salary_from', 'salary_to']].mean(axis=1)
    vacancies = len(df)
    df["count"] = df.groupby("area_name")['area_name'].transform("count")
    df_norm = df[df['count'] >= 0.01 * vacancies]
    cities = list(df_norm["area_name"].unique())
    salaries_by_year, vacancies_by_year, inp_vacancy_salary, inp_vacancy_count, salaries_areas, vacancies_areas \
        = {}, {}, {}, {}, {}, {}
    for city in cities:
        df_s = df_norm[df_norm['area_name'] == city]
        salaries_areas[city] = int(df_s['salary'].mean())
        vacancies_areas[city] = round(len(df_s) / len(df), 4)
    q = Queue()
    processes = []
    for y in years:
        p = Process(target=start, args=(vac, y, q))
        processes.append(p)
        p.start()
    for p in processes:
        a = q.get()
        salaries_by_year.update(a[0])
        vacancies_by_year.update(a[1])
        inp_vacancy_salary.update(a[2])
        inp_vacancy_count.update(a[3])
        p.join()
    print("Динамика уровня зарплат по годам:", sort_dict(salaries_by_year))
    print("Динамика кол-ва вакансий по годам:", sort_dict(vacancies_by_year))
    print("Динамика уровня зарплат по годам для выбранной профессии:", sort_dict(inp_vacancy_salary))
    print("Динамика кол-ва вакансий по годам для выбранной профессии:", sort_dict(inp_vacancy_count))
    print("Уровень зарплат по городам в порядке убывания:", sort_area_dict(salaries_areas))
    print("Доля вакансий по городам в порядке убывания:", sort_area_dict(vacancies_areas))
