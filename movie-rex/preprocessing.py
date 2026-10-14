import pandas as pd
import re

df = pd.read_csv("imdb_top_1000.csv")

movies = df[
    ["Series_Title", "Genre", "Overview",
     "Director", "Star1", "Star2", "Star3", "Star4",
     "Runtime", "IMDB_Rating"]
].copy()

text_columns = [
    "Genre", "Overview", "Director",
    "Star1", "Star2", "Star3", "Star4"
]

for col in text_columns:
    movies[col] = movies[col].fillna("")

movies["Runtime"] = (
    movies["Runtime"]
    .str.replace("min", "", regex=False)
    .astype(float)
)

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

for col in text_columns:
    movies[col] = movies[col].apply(clean_text)

movies["Title_Clean"] = movies["Series_Title"].str.lower().str.strip()

print(movies.head())
print(movies.shape)
print(movies.isnull().sum())
print("DUPLICATE TITLES:", movies["Title_Clean"].duplicated().sum())

movies.to_csv("imdb_cleaned.csv", index=False)