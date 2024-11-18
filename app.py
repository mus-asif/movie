import pandas as pd
import streamlit as st
import pickle
import requests

# Replace with your actual OMDB API key
OMDB_API_KEY = '5b14b3fc'

# Fetch movie details like poster, plot, rating, and IMDb ID (for trailer)
def fetch_movie_details(movie_title):
    url = f'https://www.omdbapi.com/?t={movie_title}&apikey={OMDB_API_KEY}'
    response = requests.get(url)
    data = response.json()
    if data.get('Response') == 'True':
        movie_details = {
            'Poster': data.get('Poster'),
            'Plot': data.get('Plot', 'Plot not available'),
            'IMDb_Rating': data.get('imdbRating', 'N/A'),
            'Genre': data.get('Genre', 'N/A'),
            'Released': data.get('Released', 'N/A'),
            'Actors': data.get('Actors', 'N/A'),
            'imdbID': data.get('imdbID', 'N/A')  # Store IMDb ID for trailer
        }
    else:
        movie_details = None
    return movie_details

# Get YouTube link for trailer using IMDb ID
def get_trailer_link(imdb_id):
    if imdb_id:
        return f"https://www.youtube.com/results?search_query={imdb_id}+trailer"
    return None

# Recommendation function
def recommend(movie):
    movie_index = movies_df[movies_df['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_details = []
    for i in movies_list:
        movie_title = movies_df.iloc[i[0]].title
        recommended_movies.append(movie_title)
        details = fetch_movie_details(movie_title)
        recommended_movies_details.append(details)
    return recommended_movies, recommended_movies_details

# Load the data
movies_dict = pickle.load(open('movie_list.pkl', 'rb'))
movies_df = pd.DataFrame(movies_dict)
movies = movies_df['title'].values

similarity = pickle.load(open('similarity.pkl', 'rb'))

# Streamlit app
st.title('Enhanced Movie Recommender System')

selected_movie_name = st.selectbox(
    'Select a movie to get recommendations',
    movies
)

# Fetch details for the selected movie
if selected_movie_name:
    selected_movie_details = fetch_movie_details(selected_movie_name)
    if selected_movie_details:
        st.image(selected_movie_details['Poster'])
        st.write(f"**Plot**: {selected_movie_details['Plot']}")
        st.write(f"**IMDb Rating**: {selected_movie_details['IMDb_Rating']}")
        st.write(f"**Genre**: {selected_movie_details['Genre']}")
        st.write(f"**Released**: {selected_movie_details['Released']}")
        st.write(f"**Actors**: {selected_movie_details['Actors']}")

if st.button('Recommend'):
    recommended_movie_names, recommended_movie_details = recommend(selected_movie_name)
    
    # Display the recommended movies in 2 columns per row
    for i in range(0, len(recommended_movie_names), 2):
        cols = st.columns(2)  # Create 2 columns per row
        for idx, col in enumerate(cols):
            if i + idx < len(recommended_movie_names):
                movie_name = recommended_movie_names[i + idx]
                movie_details = recommended_movie_details[i + idx]
                with col:
                    st.text(movie_name)
                    if movie_details:
                        st.image(movie_details['Poster'])
                        st.write(f"IMDb Rating: {movie_details['IMDb_Rating']}")
                        st.write(f"Genre: {movie_details['Genre']}")
                        st.write(f"Actors: {movie_details['Actors']}")
                        
                        # Add the Watch Trailer link
                        trailer_link = get_trailer_link(movie_details['imdbID'])
                        if trailer_link:
                            st.markdown(f"[Watch Trailer]({trailer_link})", unsafe_allow_html=True)
                        else:
                            st.write("Trailer not available")
                    else:
                        st.write("Details not available")
