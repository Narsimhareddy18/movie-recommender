from flask import Flask, render_template, request
import pickle
import pandas as pd
import requests  # 🆕 For TMDB API requests


app = Flask(__name__)

# 🆕 Function to fetch movie poster from TMDB API
def fetch_poster(movie_title):
    api_key = 'YOUR_API_KEY_HERE'  # Replace with your TMDB API Key
    url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie_title}"
    response = requests.get(url)
    data = response.json()
    if data['results']:
        poster_path = data['results'][0]['poster_path']
        return f"https://image.tmdb.org/t/p/w500/{poster_path}"
    return None


movies = pd.read_csv('data/movies.csv')
similarity = pickle.load(open('data/similarity.pkl', 'rb'))

def recommend(movie_title):
    try:
        index = movies[movies['title'] == movie_title].index[0]
        distances = list(enumerate(similarity[index]))
        sorted_movies = sorted(distances, key=lambda x: x[1], reverse=True)[1:6]
        return [movies.iloc[i[0]].title for i in sorted_movies]
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