import pandas as pd

renewables_df = pd.read_csv('renewables.csv')

def standardize_columns(df):
    df.columns = (
        df.columns
        .str.strip()         # Remove leading/trailing whitespace
        .str.lower()         # Convert to lowercase
        .str.replace(' ', '_')  # Replace spaces with underscores
        .str.replace('[^a-z0-9_]', '', regex=True)  # Remove special characters
    )
    return df

standardize_columns(renewables_df)

renewables_2020 = renewables_df[renewables_df['year'] == 2020]
renewables_2020.to_csv('renewables2020.csv', index=False)

renewables_2020['entity'] = renewables_2020['entity'].replace('Czechia', 'Czech Republic')
# List of EU-27 country names
eu27_countries = [
    "Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czech Republic",
    "Denmark", "Estonia", "Finland", "France", "Germany", "Greece", "Hungary",
    "Ireland", "Italy", "Latvia", "Lithuania", "Luxembourg", "Malta", "Netherlands",
    "Poland", "Portugal", "Romania", "Slovakia", "Slovenia", "Spain", "Sweden"
]

# Filter for rows where the country column is in the EU-27 list
eu27_renewables_2020 = renewables_2020[renewables_2020['entity'].isin(eu27_countries)]

# Display the filtered DataFrame
print(eu27_renewables_2020)
eu27_renewables_2020.to_csv('EUrenewables2020.csv', index=False)

print(eu27_renewables_2020.columns)