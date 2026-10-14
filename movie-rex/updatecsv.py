import pandas as pd

movies = pd.read_csv("imdb_cleaned.csv")

if "Cast" not in movies.columns:
    movies["Cast"] = movies[["Star1", "Star2", "Star3", "Star4"]].apply(
        lambda row: ", ".join(x for x in row if x),
        axis=1
    )

    movies = movies.drop(columns=["Star1", "Star2", "Star3", "Star4"])

movies["Genre"] = movies["Genre"].str.replace("sci fi", "scifi", regex=False)
movies["Genre"] = movies["Genre"].str.replace("film noir", "filmnoir", regex=False)

movies.to_csv("imdb_cleaned.csv", index=False)

# Identification features : Series_Title, Title_Clean
# Content features (TD-IDF) : Genre, Overview, Director, Cast 
# Preference numerical features :- Runtime, IMDB Rating

# Overview :- compare movie plot both method 1 and 2
# Genre :- compare directly with other movie genres
# Cast :- compare directly with cast of other movies
# Director :- compare directly with directors of other movies
# Runtime :- first applies all the similarity features then performs preference checks from the remaining data
# Rating:- first applies all the similarity features then performs preference checks from the remaining data


    #                INCEPTION
    #                    │
    #     ┌──────────────┼──────────────┐
    #     ↓              ↓              ↓
    # Overview         Genre       Director/Cast
    #    │               │              │
    #   TF-IDF         TF-IDF         TF-IDF
    #    │               │              │
    #    └───────────────┼──────────────┘
    #                    ↓
    #             Weighted Score
    #                    ↓
    #              Top Movies

#                   USER INPUT
#                      │
#        ┌─────────────┼─────────────┐
#        ↓             ↓             ↓
#  Description       Genre         Cast
#        ↓             ↓             ↓
#      TF-IDF        TF-IDF        TF-IDF
#        │             │             │
#        └─────────────┼─────────────┘
#                      ↓
#               Similarity Score
#                      +
#              Runtime Filter
#                      +
#               Rating Filter
#                      ↓
#                Top Movies

# ┌───────────────────────────────────────────┐
# │              MOVIE FEATURES                │
# ├───────────────────────────────────────────┤
# │ Overview       → Content similarity        │
# │ Genre          → Content similarity        │
# │ Cast           → Content similarity        │
# │ Director       → Content similarity        │
# │ Runtime        → Optional user filter      │
# │ IMDB_Rating    → Optional user filter      │
# │ Series_Title   → Display                   │
# │ Title_Clean    → Movie lookup              │
# └───────────────────────────────────────────┘