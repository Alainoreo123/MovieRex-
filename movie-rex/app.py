from pathlib import Path
from typing import Optional
import math

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# These imports expect your existing recommender files to be in the same folder as app.py.
# If importing either file prints test recommendations, move that test code under:
# if __name__ == "__main__":
from recommender import recommend_movies, get_title_suggestions
from recommender_mode2 import (
    recommend_custom,
    get_genre_suggestions,
    get_cast_suggestions,
    get_director_suggestions,
)

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(title="Movie-Rex API", version="1.0.0")
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


class MovieRecommendationRequest(BaseModel):
    movie_title: str = Field(min_length=1, max_length=200)
    n: int = Field(default=10, ge=1, le=50)


class CustomRecommendationRequest(BaseModel):
    description: str = Field(min_length=3, max_length=1000)
    genres: list[str] = Field(default_factory=list, max_length=20)
    cast: list[str] = Field(default_factory=list, max_length=20)
    director: Optional[str] = Field(default=None, max_length=200)
    min_runtime: Optional[float] = Field(default=None, ge=1, le=1000)
    max_runtime: Optional[float] = Field(default=None, ge=1, le=1000)
    min_rating: Optional[float] = Field(default=None, ge=0, le=10)
    max_rating: Optional[float] = Field(default=None, ge=0, le=10)
    n: int = Field(default=10, ge=1, le=50)


def clean_for_json(value):
    """Convert pandas/numpy values to JSON-safe Python values."""
    if hasattr(value, "item"):
        try:
            value = value.item()
        except (ValueError, TypeError):
            pass
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    if isinstance(value, dict):
        return {str(k): clean_for_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean_for_json(v) for v in value]
    return value


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/api/health")
def health():
    return {"status": "ok", "app": "Movie-Rex"}


@app.get("/api/suggestions/titles")
def title_suggestions(q: str = Query(default="", max_length=100)):
    return {"suggestions": get_title_suggestions(q) if q.strip() else []}


@app.get("/api/suggestions/genres")
def genre_suggestions(q: str = Query(default="", max_length=100)):
    return {"suggestions": get_genre_suggestions(q) if q.strip() else []}


@app.get("/api/suggestions/cast")
def cast_suggestions(q: str = Query(default="", max_length=100)):
    return {"suggestions": get_cast_suggestions(q) if q.strip() else []}


@app.get("/api/suggestions/directors")
def director_suggestions(q: str = Query(default="", max_length=100)):
    return {"suggestions": get_director_suggestions(q) if q.strip() else []}


@app.post("/api/recommend/movie")
def recommend_by_movie(request: MovieRecommendationRequest):
    results = recommend_movies(request.movie_title, n=request.n)
    if not results:
        raise HTTPException(status_code=404, detail="Movie not found. Try selecting a title from the suggestions.")
    return {"results": clean_for_json(results)}


@app.post("/api/recommend/custom")
def recommend_by_preferences(request: CustomRecommendationRequest):
    if request.min_runtime is not None and request.max_runtime is not None and request.min_runtime > request.max_runtime:
        raise HTTPException(status_code=422, detail="Minimum runtime cannot exceed maximum runtime.")
    if request.min_rating is not None and request.max_rating is not None and request.min_rating > request.max_rating:
        raise HTTPException(status_code=422, detail="Minimum rating cannot exceed maximum rating.")

    try:
        results = recommend_custom(
            description=request.description,
            genres=request.genres or None,
            cast=request.cast or None,
            director=request.director or None,
            min_runtime=request.min_runtime,
            max_runtime=request.max_runtime,
            min_rating=request.min_rating,
            max_rating=request.max_rating,
            n=request.n,
        )
    except Exception as exc:
        # The terminal running Uvicorn will show the full traceback for debugging.
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {exc}") from exc

    return {"results": clean_for_json(results or [])}
