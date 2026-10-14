import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

movies = pd.read_csv("imdb_cleaned.csv")

# print(movies.head())
# print(movies.shape)
# print(movies.columns)
# print("overview: ", overview_matrix.shape)
# print("genre: ",genre_matrix.shape)
# print("cast: ",cast_matrix.shape)
# print("director: ",director_matrix.shape)
# print(genre_vectorizer.get_feature_names_out()[:20])
# print(movies.shape)
# print(overview_matrix.shape)
# print(overview_vectorizer.get_feature_names_out()[-20:])


overview_vectorizer = TfidfVectorizer(stop_words="english")
overview_matrix = overview_vectorizer.fit_transform(movies["Overview"])

# genre_vectorizer = TfidfVectorizer()
# genre_matrix = genre_vectorizer.fit_transform(movies["Genre"])

# director_vectorizer = TfidfVectorizer()
# director_matrix = director_vectorizer.fit_transform(movies["Director"])

# cast_vectorizer = TfidfVectorizer()
# cast_matrix = cast_vectorizer.fit_transform(movies["Cast"])

overview_similarity = cosine_similarity(overview_matrix)
print(overview_similarity.shape)


# function that finds similarity  between genre

def genre_similarity(genre1, genre2):
    genres1 = set(genre1.split())
    genres2 = set(genre2.split())

    if not genres1 or not genres2:
        return 0

    return len(genres1&genres2) / len(genres1 | genres2) # here & returns intersection and | returns union

# MOVIE CAST SIMILARITY FOR MODE 1

def movie_cast_similarity(cast1, cast2):
    actors1 = set(actor.strip() for actor in cast1.split(","))
    actors2 = set(actor.strip() for actor in cast2.split(","))

    if not actors1 or not actors2:
        return 0

    return len(actors1 & actors2) / len(actors1 | actors2)

# CAST SIMILARITY SCORE (MODE 2)
# def cast_similarity(movie_cast, user_cast):
#     movie_actors = set(actor.strip() for actor in movie_cast.split(","))
#     user_actors = set(actor.strip() for actor in user_cast.split(","))

#     if not user_actors:
#         return 0

#     return len(movie_actors&user_actors) / len(user_actors)

user_cast = "tom hardy, tom holland"

# DIRECTOR SIMILARITY SCORE 

def director_similarity(movie_director, user_director):
    if not user_director: 
        return 0

    return int(movie_director == user_director)


# THE MAIN ALGO


def recommend_movies(movie_title, n=10):

    movie_title = movie_title.lower().strip()

    matches = movies[movies["Title_Clean"] == movie_title]

    if matches.empty:
        return []

    movie_index = matches.index[0]

    target_genre = movies.loc[movie_index, "Genre"]
    target_cast = movies.loc[movie_index, "Cast"]
    target_director = movies.loc[movie_index, "Director"]

    overview_scores = overview_similarity[movie_index]

    genre_scores = []
    cast_scores = []
    director_scores = []

    for i in range(len(movies)):
        genre_scores.append(
            genre_similarity(
                target_genre,
                movies.loc[i, "Genre"]
            )
        )

        cast_scores.append(
            movie_cast_similarity(
                target_cast,
                movies.loc[i, "Cast"]
            )
        )

        director_scores.append(
            director_similarity(
                target_director,
                movies.loc[i, "Director"]
            )
        )

    genre_scores = np.array(genre_scores)
    cast_scores = np.array(cast_scores)
    director_scores = np.array(director_scores)

    final_score = (
        0.60 * overview_scores +
        0.20 * genre_scores +
        0.07 * cast_scores +
        0.13 * director_scores
    )

    similar_movies = final_score.argsort()[::-1]

    similar_movies = [
        i for i in similar_movies
        if i != movie_index
    ][:n]

    results = []

    for i in similar_movies:
        results.append({
            "title": movies.loc[i, "Series_Title"],
            "genre": movies.loc[i, "Genre"],
            "director": movies.loc[i, "Director"],
            "cast": movies.loc[i, "Cast"],
            "runtime": movies.loc[i, "Runtime"],
            "rating": movies.loc[i, "IMDB_Rating"],
            "similarity": round(float(final_score[i]), 4)
        })

    return results


def get_title_suggestions(query, limit=8):
    query = query.lower().strip()

    if not query:
        return []

    matches = movies[
        movies["Title_Clean"].str.contains(query, regex=False)
    ]

    return matches["Series_Title"].head(limit).tolist()
    


results = recommend_movies("The Dark Knight", n=5)

for movie in results:
    print(movie["title"], "->", movie["similarity"])

    








