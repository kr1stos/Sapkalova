import pandas as pd
file_name = "vacancies_by_year (1).csv"
df = pd.read_csv(file_name)
df["years"] = df["published_at"].apply(lambda s: int(s[:4]))
years = list(df["years"].unique())
for year in years:
    data = df[df["years"] == year]
    data.iloc[:, :6].to_csv(f"created_csv_files\\part_{year}.csv", index=False)