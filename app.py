from flask import Flask, render_template, request
import pandas as pd
import pickle
import requests
import os

app = Flask(__name__)

# Load data
movies = pd.read_csv('data/movies.csv')
movies.columns = movies.columns.str.strip()  # 🔧 Remove any extra spaces in headers
movies = movies[['title', 'overview']]  # Use only necessary columns

similarity = pickle.load(open('data/similarity.pkl', 'rb'))

# TMDB Poster fetcher
def fetch_poster(movie_title):
    api_key = os.getenv("TMDB_API_KEY")  # 🔐 Securely read API Key
    url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie_title}"
    response = requests.get(url)
    data = response.json()
    if data['results']:
        poster_path = data['results'][0].get('poster_path')
        return f"https://image.tmdb.org/t/p/w500/{poster_path}" if poster_path else None
    return None

# Recommend function with posters
def recommend(movie_title):
    try:
        index = movies[movies['title'].str.lower() == movie_title.lower()].index[0]
        distances = list(enumerate(similarity[index]))
        sorted_movies = sorted(distances, key=lambda x: x[1], reverse=True)[1:6]

        recommended_titles = []
        recommended_posters = []

        for i in sorted_movies:
            title = movies.iloc[i[0]]['title']
            recommended_titles.append(title)
            recommended_posters.append(fetch_poster(title))

        return list(zip(recommended_titles, recommended_posters))
    except IndexError:
        return []

@app.route('/', methods=['GET', 'POST'])
def home():
    recommendations = []
    if request.method == 'POST':
        movie_name = request.form['movie']
        recommendations = recommend(movie_name)
    return render_template('index.html', recommendations=recommendations)

if __name__ == '__main__':
    app.run(debug=True)
