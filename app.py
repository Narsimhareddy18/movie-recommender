from flask import Flask, render_template, request
import pickle
import pandas as pd

app = Flask(__name__)

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