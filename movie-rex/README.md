# Movie-Rex 🎬

Movie-Rex is a content-based movie recommendation system built with
Python. It recommends movies using plot descriptions, genres, cast,
directors, runtime, and IMDb ratings.

## Features

-   **Recommend by movie:** Enter a movie title to find similar movies.
-   **Recommend by preferences:** Describe the type of movie you want
    and optionally filter by genres, cast, director, runtime, and IMDb
    rating.
-   Semantic plot matching using the pretrained `all-MiniLM-L6-v2`
    Sentence Transformer.
-   TF-IDF and cosine similarity in the movie-based recommendation mode.
-   FastAPI backend with an HTML, CSS, and JavaScript frontend.
-   Autocomplete endpoints for movie titles, genres, cast, and
    directors.
-   Cached movie embeddings to speed up subsequent runs.

## Tech stack

Python, Pandas, NumPy, scikit-learn, Sentence Transformers, FastAPI,
Uvicorn, HTML, CSS, and JavaScript.

## Project structure

``` text
movie-rex/
├── app.py
├── recommender.py
├── recommender_mode2.py
├── preprocessing.py
├── updatecsv.py
├── imdb_top_1000.csv
├── imdb_cleaned.csv
├── overview_embeddings.npy       # Generated cache
└── frontend/
    ├── index.html
    ├── style.css
    └── script.js
```

Your actual files may vary. The backend expects `app.py`, both
recommender modules, and `imdb_cleaned.csv` in the project root.
Frontend files should be inside `frontend/`.

## Requirements

-   Python 3.10 or newer recommended
-   Internet access the first time the Sentence Transformer model is
    downloaded
-   The cleaned dataset `imdb_cleaned.csv`

## Installation and setup

### 1. Open the project

Open the `movie-rex` folder in VS Code, then choose **Terminal → New
Terminal**. Make sure the terminal is in the folder containing `app.py`.

### 2. Install dependencies

Run in PowerShell:

``` powershell
python -m pip install pandas numpy scikit-learn sentence-transformers fastapi "uvicorn[standard]"
```

If `python` is not recognized, try using `py` instead.

### 3. Check the dataset

Make sure `imdb_cleaned.csv` is in the project root.

If you need to recreate the cleaned dataset, run your preprocessing
scripts in the order required by your code:

``` powershell
python preprocessing.py
python updatecsv.py
```

Only rerun these if necessary; check their output before overwriting an
existing cleaned dataset.

### 4. Start Movie-Rex

From the project root, run:

``` powershell
python -m uvicorn app:app --reload
```

Wait for messages similar to:

``` text
Uvicorn running on http://127.0.0.1:8000
Application startup complete.
```

The first run may take longer while the Sentence Transformer model
downloads. The application can create `overview_embeddings.npy` to cache
movie embeddings for later runs.

**Keep the terminal open while using the website.**

### 5. Open the application

-   Website: http://127.0.0.1:8000
-   Interactive API documentation: http://127.0.0.1:8000/docs
-   Health check: http://127.0.0.1:8000/api/health

Stop the server with `Ctrl+C` in the terminal.

## API endpoints

  --------------------------------------------------------------------------------------
  Method                  Endpoint                               Purpose
  ----------------------- -------------------------------------- -----------------------
  `GET`                   `/api/health`                          Check whether the API
                                                                 is running

  `GET`                   `/api/suggestions/titles?q=bat`        Suggest movie titles

  `GET`                   `/api/suggestions/genres?q=act`        Suggest genres

  `GET`                   `/api/suggestions/cast?q=tom`          Suggest cast members

  `GET`                   `/api/suggestions/directors?q=chris`   Suggest directors

  `POST`                  `/api/recommend/movie`                 Recommend movies based
                                                                 on a selected title

  `POST`                  `/api/recommend/custom`                Recommend movies from a
                                                                 description and
                                                                 optional filters
  --------------------------------------------------------------------------------------

Use `/docs` to inspect and test these endpoints.

## How recommendations work

### Mode 1: Recommend by movie

The system ranks movies using a weighted score that combines plot
similarity, genre overlap, cast overlap, and director matching. Plot
similarity uses TF-IDF and cosine similarity.

### Mode 2: Recommend by preferences

The system compares the user's description with movie plot summaries
using embeddings from `all-MiniLM-L6-v2`. It can combine description
similarity with genre, cast, and director matching. Optional runtime and
IMDb rating limits filter the candidate movies before ranking.

The weights are configured in the recommender code.

## Troubleshooting

### `ModuleNotFoundError`

Install the missing dependency:

``` powershell
python -m pip install package-name
```

Replace `package-name` with the missing library.

### `Could not import module "app"`

-   Make sure the terminal is in the project root.
-   Confirm `app.py` exists.
-   Check that the imports in `app.py` match the recommender filenames.

### `FileNotFoundError: imdb_cleaned.csv`

Place `imdb_cleaned.csv` beside `app.py`, or update the CSV path in the
recommender modules.

### CSS or JavaScript does not load

Your FastAPI app mounts the `frontend` directory at `/static`. In
`frontend/index.html`, use:

``` html
<link rel="stylesheet" href="/static/style.css">
<script src="/static/script.js" defer></script>
```

Refresh with `Ctrl+F5`. If it still fails, check Developer Tools with
`F12`, especially **Console** and **Network**.

### Autocomplete suggestions do not appear

Test these endpoints in your browser:

-   http://127.0.0.1:8000/api/suggestions/genres?q=act
-   http://127.0.0.1:8000/api/suggestions/cast?q=tom
-   http://127.0.0.1:8000/api/suggestions/directors?q=chris

If an endpoint returns suggestions but the website does not display
them, inspect `frontend/script.js` and the browser console.

### Hugging Face warning

An unauthenticated-request warning is generally informational when
downloading a public model. A token is not normally required for basic
use, although authentication may improve rate limits.

### Port 8000 is already in use

Stop the other server with `Ctrl+C`, or use another port:

``` powershell
python -m uvicorn app:app --reload --port 8001
```

Then open http://127.0.0.1:8001.

## Evaluation

Useful ranking metrics include:

-   **Precision@K:** Fraction of the top K recommendations that are
    relevant.
-   **Recall@K:** Fraction of all known relevant movies found in the top
    K.
-   **NDCG@K:** Rewards relevant movies appearing higher in the ranking.

These metrics require independently labelled relevant movies for test
queries. Accuracy and R² are generally not appropriate for this ranking
task without a suitable labelled prediction target.

## Notes

-   If the dataset's rows or order change, regenerate
    `overview_embeddings.npy` so embeddings stay aligned with the
    dataset.
-   Put example/test recommendation calls under
    `if __name__ == "__main__":` so they do not run when FastAPI imports
    the recommender modules.
-   This project uses a pretrained sentence-embedding model; it does not
    train that transformer from scratch.

## License

Add a license file if you plan to distribute the project publicly. Check
the dataset's terms before redistributing it.
