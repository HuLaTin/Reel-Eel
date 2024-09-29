import pandas as pd
import keys
import requests
import os

# Load the Google Sheet data
googleSheetCSV = "https://docs.google.com/spreadsheets/d/" + keys.googleSheetId + "/export?format=csv"
gs = pd.read_csv(googleSheetCSV)

# Drop rows with missing IMDb id or cumulative rating
gs.dropna(subset=["IMDB id", "Cumulative Rating (1-5)"], inplace=True)

# Clean and format the data
gs["Cumulative Rating (1-5)"] = gs["Cumulative Rating (1-5)"].astype(int)
gs["Year"] = gs["Year"].astype(int)

# Save cleaned data for reference (optional)
gs.to_csv("In/HulaHoopMovieNight.csv", index=False)

# Get the list of IMDb IDs from the Google Sheet
movie_ids = gs["IMDB id"].tolist()

# Check if "Out/moviesData.csv" exists
if os.path.exists("Out/moviesData.csv"):
    # Load the existing movie data
    existing_movies_df = pd.read_csv("Out/moviesData.csv")
    existing_imdb_ids = existing_movies_df["imdbID"].tolist()  # Use the correct column name (e.g., "imdbID")
else:
    # Create an empty DataFrame if the file doesn't exist
    existing_movies_df = pd.DataFrame()
    existing_imdb_ids = []

# Find IMDb IDs that are missing (not yet fetched)
missing_ids = [imdb_id for imdb_id in movie_ids if imdb_id not in existing_imdb_ids]

# Initialize a list to store new movie data
new_movie_list = []

# OMDb API key
api_key = keys.OMDBkey

# Fetch data from OMDb for missing movies
import time

for imdb_id in missing_ids:
    url = f'http://www.omdbapi.com/?i={imdb_id}&apikey={api_key}'
    
    # Request movie data from OMDb
    response = requests.get(url)
    
    if response.status_code == 200:
        movie_data = response.json()
        new_movie_list.append(movie_data)
    else:
        print(f"Failed to retrieve data for IMDb ID {imdb_id}")
    
    # Optional: delay to avoid rate limits
    time.sleep(1)

# Convert the new movie data to a DataFrame
if new_movie_list:
    new_movies_df = pd.DataFrame(new_movie_list)
    
    # Append new movies to the existing CSV file
    if not existing_movies_df.empty:
        updated_movies_df = pd.concat([existing_movies_df, new_movies_df], ignore_index=True)
    else:
        updated_movies_df = new_movies_df
    
    # Save the updated DataFrame to "Out/moviesData.csv"
    updated_movies_df.to_csv("Out/moviesData.csv", index=False)
    print(updated_movies_df.head())
else:
    print("No new movies to fetch.")
