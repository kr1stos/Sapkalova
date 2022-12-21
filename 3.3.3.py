import pandas as pd
import requests

pd.set_option("expand_frame_repr", False)
urls = []
for j in range(1, 23):
    if 1 <= j <= 8:
        urls.append(
            f"https://api.hh.ru/vacancies?date_from=2022-12-19T0{j}:00:00&date_to=2022-12-19T0{j + 1}:00:00&specialization=1&")
    elif j == 9:
        urls.append(
            f"https://api.hh.ru/vacancies?date_from=2022-12-19T0{j}:00:00&date_to=2022-12-19T{j + 1}:00:00&specialization=1&")
    else:
        urls.append(
            f"https://api.hh.ru/vacancies?date_from=2022-12-19T{j}:00:00&date_to=2022-12-19T{j + 1}:00:00&specialization=1&")
df = pd.DataFrame(columns=["name", "salary_from", "salary_to", "salary_currency", "area_name", "published_at"])
for url in urls:
    pages = requests.get(url).json()
    for i in range(pages["pages"]):
        params = {'page': i}
        response = requests.get(url, params=params)
        json = requests.get(url, params=params).json()
        items = json["items"]
        for x in items:
            try:
                df.loc[len(df)] = [x["name"], x["salary"]["from"], x["salary"]["to"], x["salary"]["currency"],
                                   x["area"]["name"], x["published_at"]]
            except TypeError:
                continue
df.to_csv("Vacancies_by_HH.csv", index=False)
print(df)

