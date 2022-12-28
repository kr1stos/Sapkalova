import math
from statistics import mean
import pandas as pd

pd.set_option("expand_frame_repr", False)
dataframe = pd.read_csv("vacancies_dif_currencies.csv")
df_d = pd.read_csv("currencies.csv")


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


dataframe["salary"] = dataframe.apply(lambda row: get_salary(row["salary_from"], row["salary_to"],
                                                             row["salary_currency"],
                                                             row["published_at"][:7].split("-")), axis=1)
dataframe[:100].to_csv("3.4.1.csv", index=False)
