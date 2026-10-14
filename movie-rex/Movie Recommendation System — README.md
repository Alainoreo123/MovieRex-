# Movie Recommendation System

A personalized content-based movie recommendation system built using the IMDb Top 1000 dataset.

The system provides two different recommendation modes:

1. **Movie-Based Recommendation** — The user enters a movie they like, and the system recommends movies similar to it.
2. **Custom Preference Recommendation** — The user describes the type of movie they want and optionally provides preferences such as cast, director, runtime, and IMDb rating.

---

## Dataset

The project uses the **IMDb Top 1000 Movies** dataset.

The original dataset contains 1,000 movies and 16 features, including:

- Movie title
- Release year
- Certificate
- Runtime
- Genre
- IMDb rating
- Overview
- Meta score
- Director
- Cast
- Number of votes
- Gross
- Poster link

Only features relevant to recommendation will be used.

---

## Recommendation Modes

### Mode 1 — Movie-Based Recommendation

The user enters an existing movie from the dataset.

Example:

```text
Enter a movie: Inception
```

The system analyzes the movie's:

- Genre
- Overview
- Director
- Cast

It then compares the selected movie with other movies using text similarity and returns the most similar movies.

Example:

```text
Inception
    ↓
Extract movie features
    ↓
TF-IDF representation
    ↓
Compare with other movies
    ↓
Cosine similarity
    ↓
Rank movies
    ↓
Top recommendations
```

---

### Mode 2 — Custom Preference Recommendation

The user describes the type of movie they want.

Required inputs:

- Genre
- Vague movie description

Optional inputs:

- Cast
- Director
- Runtime range
- IMDb rating range

Example:

```text
Genre:
Sci-Fi, Thriller

Description:
A group of astronauts travels through space
to find a new home for humanity.

Cast:
Matthew McConaughey

Director:
Christopher Nolan

Runtime:
120 - 180 minutes

IMDb Rating:
8 - 10
```

The description is treated as a search query and compared against the movie overviews in the dataset.

The optional fields are used to further refine the recommendations.

---

## Feature Selection

### Main Content Features

These features describe the actual content of a movie:

- `Genre`
- `Overview`
- `Director`
- `Star1`
- `Star2`
- `Star3`
- `Star4`

These will primarily be processed using **TF-IDF and cosine similarity**.

### Preference Features

These features represent user preferences:

- `Runtime`
- `IMDB_Rating`

These will be processed separately as numerical features or optional filters.

### Features Not Used Initially

- `Poster_Link`
- `Certificate`
- `Meta_score`
- `No_of_Votes`
- `Gross`

These do not directly describe the movie's content and are not required for the initial recommendation model.

`Released_Year` may be retained for displaying information but will not be used as a primary similarity feature.

---

## System Architecture

```text
                    MOVIE RECOMMENDER
                           |
                +----------+----------+
                |                     |
             MODE 1                 MODE 2
          Movie Input            Custom Input
                |                     |
          Existing Movie       User Preferences
                |                     |
                +----------+----------+
                           |
                    Feature Processing
                           |
             +-------------+-------------+
             |                           |
       Text Features              Numerical Features
             |                           |
          TF-IDF                Runtime / Rating
             |                           |
             +-------------+-------------+
                           |
                    Similarity / Filtering
                           |
                    Ranked Recommendations
                           |
                     Top 5 / Top 10
```

---

## Technology Stack

- **Python**
- **Pandas** — Data loading and preprocessing
- **NumPy** — Numerical operations
- **Scikit-learn** — TF-IDF and similarity calculations
- **Jupyter Notebook / VS Code** — Development environment

---

## Project Pipeline

```text
Raw Dataset
     ↓
Data Inspection
     ↓
Feature Selection
     ↓
Missing Value Handling
     ↓
Duplicate Removal
     ↓
Text Cleaning
     ↓
Feature Combination
     ↓
Preprocessed Dataset
     ↓
TF-IDF Vectorization
     ↓
Cosine Similarity
     ↓
Recommendation Engine
     ↓
User Interface
```

---

## Future Improvements

Possible improvements include:

- User-specific feature weighting
- Better natural-language processing
- Genre weighting
- Runtime preference scoring
- Rating preference scoring
- Hybrid recommendation techniques
- Improved search for movie titles
- Recommendation explanations
- Web-based user interface
- Movie posters and additional movie information

---

## Goal

The goal of the project is to create a recommendation system that goes beyond simply finding movies with similar descriptions.

It provides two ways for users to discover movies:

**"I liked this movie. What else is similar?"**

and

**"I want a movie like this. What should I watch?"**