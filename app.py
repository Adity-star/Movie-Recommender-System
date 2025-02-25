import streamlit as st
import pickle
import requests
import time

# Load movies and similarity model
movies = pickle.load(open('movie_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))


# Function to fetch the poster of the selected movie using TMDb API
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=69eb3e66ce0e65630e27ff1b66f32bb7&language=en-US"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500/{poster_path}"
        else:
            return "https://via.placeholder.com/500x750?text=No+Poster+Available"  #  no poster
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching poster: {e}")
        return "https://via.placeholder.com/500x750?text=Error+Fetching+Poster"

# Function to recommend movies based on the similarity matrix and fetch their posters
def recommend(movie, movies, similarity):

    if movie not in movies['title'].values:
        st.warning("Movie not found in the dataset.")
        return [], [], None

    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    recommended_movie_names = []
    recommended_movie_posters = []

    # Get top 5 recommendations
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)

    # Fetch the poster for the selected movie
    selected_movie_id = movies.iloc[index].movie_id
    selected_movie_poster = fetch_poster(selected_movie_id)

    return recommended_movie_names, recommended_movie_posters, selected_movie_poster


# Streamlit UI
st.set_page_config(page_title="Movie Recommender System", layout="wide")

# Set header and subtitle with customized styling
st.markdown("<h1 style='text-align: center; color: #FF6347;'>🎬 Movie Recommender System</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center;'>Find similar movies based on your selection</h2>", unsafe_allow_html=True)

# Dropdown for selecting a movie
movie_list = movies['title'].values
selected_movie = st.selectbox("Select a movie", movie_list)

# When the button is clicked to show recommendations
if st.button('Show Recommendations'):
    # Add loading spinner
    with st.spinner('Fetching recommendations...'):
        time.sleep(2)  # Simulate loading time

        recommended_movie_names, recommended_movie_posters, selected_movie_poster = recommend(selected_movie, movies,
                                                                                              similarity)

        # Display the selected movie's poster and name
        if selected_movie_poster:
            st.image(selected_movie_poster, caption=f"**Selected Movie**: {selected_movie}", use_container_width=True)

        # Display the recommended movies with their posters
        if recommended_movie_names:
            st.subheader('✨ Top 5 Recommended Movies:')

            # create columns for displaying recommendations
            cols = st.columns(5)
            for idx, col in enumerate(cols):
                if idx < len(recommended_movie_names):
                    with col:
                        st.image(recommended_movie_posters[idx],
                                 use_container_width=True)
                        st.write(f"**{recommended_movie_names[idx]}**")

        else:
            st.warning("No recommendations available.")
