import pandas as pd
from flask import Flask, request, render_template
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import os

app = Flask(__name__)

# Load movie data
movies = pd.read_csv('data/movies.csv')
movies = movies[['title', 'overview']]
movies['overview'] = movies['overview'].fillna('')

# Vectorize text using TF-IDF
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(movies['overview'])

# Compute cosine similarity
cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

# Map titles to index
indices = pd.Series(movies.index, index=movies['title'].str.lower())


# Fetch poster from TMDB
import requests

def fetch_poster(movie_title):
    api_key = os.getenv("TMDB_API_KEY")  # securely using Render env variable
    url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie_title}"
    response = requests.get(url)
    data = response.json()
    if 'results' in data and len(data['results']) > 0:
        poster_path = data['results'][0]['poster_path']
        return f"https://image.tmdb.org/t/p/w500/{poster_path}"
    return None


# Recommend function
def recommend(title):
    title = title.lower()
    if title not in indices:
        return [], []

    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1:6]
    movie_indices = [i[0] for i in sim_scores]

    recommended_titles = movies['title'].iloc[movie_indices].tolist()
    posters = [fetch_poster(movie) for movie in recommended_titles]
    return recommended_titles, posters


# Home route
@app.route('/', methods=['GET', 'POST'])
def home():
    recommendations = []
    posters = []
    if request.method == 'POST':
        movie = request.form.get('movie')
        recommendations, posters = recommend(movie)
    return render_template('index.html', recommendations=recommendations, posters=posters)


if __name__ == '__main__':
    app.run(debug=True)
