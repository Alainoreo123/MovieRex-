import pandas as pd
import numpy as np
import os
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

movies = pd.read_csv("imdb_cleaned.csv")

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

if os.path.exists("overview_embeddings.npy"):
    overview_embeddings = np.load("overview_embeddings.npy")
    print("Loaded saved movie embeddings.")
else:
    overview_embeddings = embedding_model.encode(
        movies["Overview"].tolist(),
        show_progress_bar=True
    )

    np.save("overview_embeddings.npy", overview_embeddings)
    print("Generated and saved movie embeddings.")

overview_vectorizer = TfidfVectorizer(stop_words="english")

overview_matrix = overview_vectorizer.fit_transform(
    movies["Overview"]
)

# def description_similarity(description):
#     user_vector = overview_vectorizer.transform([description])

#     return cosine_similarity(
#         user_vector, overview_matrix
#     ).flatten()

def description_similarity(description):
    user_embedding = embedding_model.encode(
        [description]
    )

    return cosine_similarity(
        user_embedding,
        overview_embeddings
    ).flatten()

def genre_similarity(movie_genre, user_genres):
    movie_genres = set(movie_genre.split())
    user_genres = set(user_genres)

    if not user_genres:
        return 0

    return len(movie_genres & user_genres) / len(user_genres)

def cast_similarity(movie_cast, user_cast):
    movie_actors =set(
        actor.strip() for actor in movie_cast.split(",")
    )

    user_actors = set(user_cast)

    if not user_actors:
        return 0

    return len(movie_actors & user_actors)/len(user_actors)

def director_similarity(movie_director, user_director):
    if not user_director:
        return 0

    return int(movie_director.lower() == user_director.lower()
    )

def filter_movies(min_runtime=None, max_runtime=None,min_rating=None, max_rating=None):
    filtered = movies.copy()

    if min_runtime is not None:
        filtered = filtered[filtered["Runtime"] >= min_runtime]

    if max_runtime is not None:
        filtered = filtered[filtered["Runtime"] <= max_runtime]

    if min_rating is not None:
        filtered = filtered[filtered["IMDB_Rating"] >= min_rating]

    if max_rating is not None:
        filtered = filtered[filtered["IMDB_Rating"] <= max_rating]

    return filtered

def get_genre_suggestions(query, limit=8):
    query = query.lower().strip()

    if not query:
        return[]

    genres = set()

    for genre_list in movies["Genre"]:
        for genre in genre_list.split():
            if query in genre:
                genres.add(genre)

    return sorted(genres)[:limit]


def get_cast_suggestions(query, limit=8):
    query = query.lower().strip()

    if not query:
        return[]

    actors = set()

    for cast_list in movies["Cast"]:
        for actor in cast_list.split(","):
            actor = actor.strip()

            if query in actor:
                actors.add(actor)

    return sorted(actors)[:limit]

def get_director_suggestions(query, limit=8):
    query = query.lower().strip()

    if not query:
        return[]

    directors = movies[movies["Director"].str.contains(query, regex=False)]["Director"].unique()

    return sorted(directors)[:limit]

def recommend_custom(
        description,
        genres=None,
        cast=None,
        director=None,
        min_runtime=None,
        max_runtime=None,
        min_rating=None,
        max_rating=None,
        n=10):
    filtered_movies = filter_movies(min_runtime, max_runtime, min_rating, max_rating)
    if filtered_movies.empty:
        return []

    description_scores = description_similarity(description)

    genre_scores = []
    cast_scores = []
    director_scores = []

    for index, movie in filtered_movies.iterrows():


        # GENRE SCORE
        if genres:
            genre_score = genre_similarity(
                movie["Genre"], 
                genres
            )
        else: 
            genre_score = 0

        # CAST SCORE 

        if cast:
            cast_score = cast_similarity(
                movie["Cast"],
                cast
            )
        else: cast_score = 0

        if director:
            director_score = director_similarity(
                movie["Director"],
                director
            )
        else: director_score = 0

        genre_scores.append(genre_score)
        cast_scores.append(cast_score)
        director_scores.append(director_score)

    genre_scores = np.array(genre_scores)
    cast_scores = np.array(cast_scores)
    director_scores = np.array(director_scores)

    description_scores = description_scores[filtered_movies.index]

    print("Filtered movies:", len(filtered_movies))
    print("Description scores:", description_scores.shape)
    print("Genre scores:", genre_scores.shape)
    print("Cast scores:", cast_scores.shape)
    print("Director scores:", director_scores.shape)

    final_scores = ( 0.60 * description_scores +
                    0.20 * genre_scores +
                    0.10 * cast_scores + 
                    0.10 * director_scores
        
    )

    ranking = np.argsort(final_scores)[::-1][:n]
    results = []

    for position in ranking:
        movie_index = filtered_movies.index[position]

        results.append({
            "title": movies.loc[movie_index, "Series_Title"],
            "genre": movies.loc[movie_index, "Genre"],
            "director": movies.loc[movie_index, "Director"],
            "cast": movies.loc[movie_index, "Cast"],
            "runtime": movies.loc[movie_index, "Runtime"],
            "rating": movies.loc[movie_index, "IMDB_Rating"],
            "similarity": round(float(final_scores[position]), 4)
        })

    return results


results = recommend_custom(
    description="A criminal investigation involving a dangerous criminal",
    genres=["crime", "drama"],
    cast=["tom hardy", "tom hanks"],
    n=5
)

print("Number of recommendations:", len(results))
print("\nRecommended Movies:\n")

for movie in results:
    print(movie["title"], "->", movie["similarity"])



    

