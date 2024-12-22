# Import pandas library for data analysis
import pandas as pd

plastic_df = pd.read_csv('global_plastic_waste.csv')
whr_df = pd.read_csv('WHR_2023.csv')
gef_df = pd.read_csv('GEF_2023.csv', encoding='ISO-8859-1') # Specified encoding because otherwise I got errors
codes_df = pd.read_csv('plotly_countries_and_codes.csv')

# Define a function to standardize column names
def standardize_columns(df):
    df.columns = (
        df.columns
        .str.strip()         # Remove leading/trailing whitespace
        .str.lower()         # Convert to lowercase
        .str.replace(' ', '_')  # Replace spaces with underscores
        .str.replace('[^a-z0-9_]', '', regex=True)  # Remove special characters
    )
    return df

standardize_columns(plastic_df)
standardize_columns(whr_df)
standardize_columns(gef_df)
standardize_columns(codes_df)

# Merge plastic_df and gef_df first
merged_df = pd.merge(codes_df, plastic_df, on='country', how='left')

# Merge plastic_df and gef_df first
merged_df = pd.merge(merged_df, gef_df, on='country', how='left')

# Merge the resulting DataFrame with whr_df
df = pd.merge(merged_df, whr_df, on='country', how='left')

# Display the merged DataFrame
print(df.head())

# Check the number of rows to confirm no observations from gef_df were lost
print(f"Number of rows in gef_df: {len(gef_df)}")
print(f"Number of rows in merged_df: {len(df)}")

# Rename typo in column name
df.rename(columns={'life_exectancy': 'life_expectancy'}, inplace=True)

# Correcting DataTypes

print("Before cleaning:")
print(df.info())

# Step 1: Convert 'life_expectancy' to numeric, coercing errors to NaN
df['life_expectancy'] = pd.to_numeric(df['life_expectancy'], errors='coerce')
# Step 3: Convert the 'life_expectancy' column to integer
df['life_expectancy'] = df['life_expectancy'].astype('float64')

# Step 1: Convert 'life_expectancy' to numeric, coercing errors to NaN
df['hdi'] = pd.to_numeric(df['hdi'], errors='coerce')
# Step 3: Convert the 'life_expectancy' column to integer
df['hdi'] = df['hdi'].astype('float64')

# Step 1: Remove the dollar sign and commas
df['per_capita_gdp'] = df['per_capita_gdp'].replace({'\$': '', ',': ''}, regex=True)
# Step 2: Convert the cleaned values to float
df['per_capita_gdp'] = pd.to_numeric(df['per_capita_gdp'], errors='coerce')

# Step 1: Convert 'life_expectancy' to numeric, coercing errors to NaN
df['population_millions'] = pd.to_numeric(df['population_millions'], errors='coerce')
# Step 3: Convert the 'life_expectancy' column to integer
df['population_millions'] = df['population_millions'].astype('float64')

# Convert the 'sdgi' column to string to handle mixed types (strings and numbers)
df['sdgi'] = df['sdgi'].astype(str)

# Check for non-numeric values in the column
non_numeric_values = df['sdgi'][~df['sdgi'].str.replace('.', '', 1).str.isdigit() & ~df['sdgi'].isna()]
print("Non-numeric values:", non_numeric_values)

# Option 1: Replace invalid values with NaN
df['sdgi'] = pd.to_numeric(df['sdgi'], errors='coerce')

# Convert to float
df['sdgi'] = df['sdgi'].astype(float)

# Verify the datatype
print(df['sdgi'].dtype)

print("After cleaning:")
print(df.info())

# Save as a new csv file
df.to_csv('global_data_new.csv', index=False)

print(df.columns)