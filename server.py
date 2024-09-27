from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)
import requests

import pickle
import json
import difflib
import os

# Load the similarity matrix from the .pkl file
with open("similarity_matrix4.pkl", "rb") as file:
    loaded_similarity_matrix = pickle.load(file)

df_movies=pd.read_csv("finaldf1.csv",encoding='ISO-8859-1')

api_key="fb47a9a0e7b454d24998042f495d0fe6"
api_token = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJmYjQ3YTlhMGU3YjQ1NGQyNDk5ODA0MmY0OTVkMGZlNiIsIm5iZiI6MTcyNDcyMzU3My4yMzI4OTQsInN1YiI6IjY2Y2QzMGFhMjhlMWMzNjMxMzZhOWE3NSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.lnA1Jn29f7IkchQW6KByXz7xnJBxFY4AKJJvu6EDyiU"


def find_similar_names(name):

    # Find the closest matches
    similar_names = difflib.get_close_matches(name, df_movies["title"].tolist(), n=6, cutoff=0.5)

    return similar_names


def get_recommended_movies(movie_name):
    recommed_movies = []

    idx = df_movies.index[df_movies["title"]==movie_name.lower()]
    #movie_id = df_movies["id"][idx[0]]
    movie_sim = loaded_similarity_matrix[idx[0]]
    #sorted_numbers = sorted(movie_sim, reverse=True)
    sorted_numbers_with_indices = sorted(enumerate(movie_sim), key=lambda x: x[1], reverse=True)

    # Extract the sorted values and their corresponding indices
    sorted_indices = [index for index, value in sorted_numbers_with_indices][1:6]
    #sorted_values = [value for index, value in sorted_numbers_with_indices][1:6]
    
    #print(sorted_indices,sorted_values)

    for i in sorted_indices:
        recommed_movies.append(df_movies["title"][i])

    print(recommed_movies)

    return recommed_movies

# Function to fetch movie details, including the poster
def get_movie_details(movie_name):
    # Replace this with actual logic to fetch movie details
    print(movie_name)
    idx = df_movies.index[df_movies["title"]==movie_name.lower()]
    print(idx[0])
    movie_id = df_movies["id"][idx[0]]
    #print(movie_id)
    url = "https://api.themoviedb.org/3/movie/{}?api_key=fb47a9a0e7b454d24998042f495d0fe6&language=en-US".format(movie_id)
    headers = {"accept": "application/json"}
    response = requests.get(url, headers=headers)
    response_json = json.loads(response.text)
    #print(response_json)
    image_path = "https://image.tmdb.org/t/p/w500"+response_json["poster_path"]

    print(image_path)
    return image_path

last_recommended_movies = []
@app.route('/', methods=['GET', 'POST'])
def index():
    global last_recommended_movies
    main_movie = "Avatar"
    main_movie_poster = None
    recommended_movies = []
    recommended_posters = []
    
    
    if request.method == 'POST':
        movie_name = request.form['movie_name']
        
        print("new request..")
        if movie_name.lower() in df_movies['title'].values:
            print("movie available")
            main_movie_poster = get_movie_details(movie_name)
            main_movie = movie_name
            recommended_movies = get_recommended_movies(movie_name)
            last_recommended_movies = recommended_movies.copy()

        else:
            similar_movies=find_similar_names(movie_name)
            if similar_movies:
                
                main_movie_poster = get_movie_details(similar_movies[0])
                main_movie = similar_movies[0]  
                recommended_movies = get_recommended_movies(main_movie)
            else:
                main_movie = movie_name + " movie not available !! Try other !!"
                print("movie not available")

        # Fetch posters for recommended movies
        recommended_posters = [get_movie_details(movie) for movie in recommended_movies]

    return render_template(
        'index.html',
        main_movie=main_movie.title(),
        main_movie_poster=main_movie_poster,
        recommended_movies=recommended_movies,
        recommended_posters=recommended_posters
    )


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000) 
#print(loaded_similarity_matrix.shape)
#print(df_movies["title"][3])


