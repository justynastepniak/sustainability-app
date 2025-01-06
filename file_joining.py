import pandas as pd
import os

# Define the folder where the CSV files are stored
folder_path = "timeseries"

# List all CSV files in the directory
csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

# Initialize a dictionary to store happiness scores for all countries
all_countries_happiness_scores = {}

# Loop through each file and process it
for file in csv_files:
    file_path = os.path.join(folder_path, file)
    
    # Extract year from the file name (assuming the year is part of the filename)
    year = file.split('.')[0]  # Adjust based on your file naming convention
    
    # Ensure that only the numeric year is kept (e.g., if file name contains extra text like "whr_2020.csv")
    year = ''.join(filter(str.isdigit, year))
    
    # Read the CSV file into a DataFrame
    df = pd.read_csv(file_path)
    
    # Loop through each row to extract the happiness score for each country
    for index, row in df.iterrows():
        country = row['country']
        happiness_score = row['happiness_score']
        
        # Add the happiness score for the country in the dictionary
        if country not in all_countries_happiness_scores:
            all_countries_happiness_scores[country] = {}
        
        # Add the score for the specific year
        all_countries_happiness_scores[country][year] = happiness_score

# Convert the dictionary of all countries' happiness scores into a DataFrame
all_countries_df = pd.DataFrame.from_dict(all_countries_happiness_scores, orient='index')

# Rename the index to 'country'
all_countries_df.index.name = 'country'

# Save the DataFrame to a CSV file
all_countries_df.to_csv('whr_timeseries.csv')

# Display the DataFrame (optional)
print("All Countries Data:")
print(all_countries_df)