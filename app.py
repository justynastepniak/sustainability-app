import streamlit as st
import pandas as pd
from streamlit_option_menu import option_menu
import plotly.express as px
import plotly.graph_objects as go

# Set page configuration to widen layout
st.set_page_config(
    page_title="Sustainability and Happiness",
    layout="wide",  # Use wide layout
)

# CSS to reduce the default margins
st.markdown(
    """
    <style>
        .main .block-container {
            padding-top: 1rem;
            padding-right: 1rem;
            padding-left: 1rem;
            padding-bottom: 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Read datafiles
df = pd.read_csv('global_data_new.csv')
timeseries_df = pd.read_csv('whr_timeseries.csv', index_col=0)
finland_data = df[df['country'] == 'Finland']

def display_world_average(df, column):
    # Calculate the average SDGI score
    world_average = df[column].mean()

    # Display the average score
    st.metric("World Average:", f"{world_average:.2f}")

def display_country_count(df, column):
    """
    Displays the count of countries with data for the specified column.
    
    Parameters:
    df (DataFrame): Data containing the country information and numerical data.
    column (str): The column to check for non-null values.
    """
    # Calculate the number of countries with non-null data in the specified column
    countries_with_data = df[df[column].notnull()]['code'].nunique()
    
    # Display the count as a metric
    st.metric("Countries with data: ", f"{countries_with_data:,}")

def display_top_three(df, column):
    # Get the top 3 rows
    top_countries = df.nlargest(3, column)['country'].tolist()

    # Format the countries with their ranks
    formatted_countries = ", ".join([f"{i+1}. {country}" for i, country in enumerate(top_countries)])

    # Display the result
    st.metric("Top 3 countries:", formatted_countries)

def display_map(df, column, fill_color, min, max):
    # dataframe, numerical data column, color scheme, minimal value in column, max value in column 
    # Create the choropleth map
    fig = go.Figure(data=go.Choropleth(
        locations=df['code'],                # Country ISO codes or names
        z=df[column],            
        text=df['country'],                  # Country names for hover text
        marker_line_color='darkgray',         # Country borders
        marker_line_width=0.5,                # Border width
        coloraxis="coloraxis"                 # Reference to the coloraxis
    ))

    # Update layout
    fig.update_layout(
        geo=dict(
            showframe=False,                
            showcoastlines=False,              
            projection_type='equirectangular',  
            showland=True,
            landcolor='lightgray',
            fitbounds="locations",
            uirevision='constant'
        ),
        coloraxis=dict(
            colorscale=fill_color,
            colorbar_len = 0.5,
            colorbar=dict(
                tickmode = 'auto'
            ),
            cmin = min,
            cmax = max,
        ),
        dragmode=False,  # Disable dragging and panning
        margin=dict(t=0, b=0, l=0, r=0)
    )

    # Display the map
    st.plotly_chart(fig, use_container_width=True)

def create_scatterplot_per_income(data, y_value, x_value, y_title, x_title):
    # Create scatterplot with color based on income group
    fig = px.scatter(
        data,
        x=x_value,
        y=y_value,
        hover_name='country',  # Display country names on hover
        color='income_group',  # Color points based on 'income_group'
        labels={  # Custom axis labels
            x_value: x_title,
            y_value: y_title,
            'income_group': 'Income Group'
        },
        category_orders={'income_group': ['LI', 'LM', 'UM', 'HI']},  # Order the income group categories
    )

    # Add a single regression line for the entire dataset
    fig.add_trace(
        px.scatter(
            data,
            x=x_value,
            y=y_value,
            trendline="ols"  # Adds an ordinary least squares (OLS) regression line
        ).data[1]  # Use the second trace, which is the regression line
    )

    # Update layout to remove the legend and gridlines
    fig.update_layout(
        height=500,
        showlegend=False,  # Hide the legend
        plot_bgcolor='white',  # Set background to white
        paper_bgcolor='white',  # Set the paper background to white
        xaxis=dict(showgrid=False, zeroline=False),  # Remove x-axis gridlines
        yaxis=dict(showgrid=False, zeroline=False)   # Remove y-axis gridlines
    )

    # Display the plot in Streamlit
    st.plotly_chart(fig, use_container_width=True)

def create_scatterplot(df, y_value, x_value, income_group='all', y_title='', x_title=''):
    # Filter data based on the selected income group
    if income_group != 'all':
        filtered_data = df[df['income_group'] == income_group]
    else:
        filtered_data = df

    # Create scatterplot
    fig = px.scatter(
        filtered_data,
        x=x_value,
        y=y_value,
        hover_name='country',  # Display country names on hover
        color='income_group',  # Color points based on 'income_group'
        labels={  # Custom axis labels
            x_value: x_title,
            y_value: y_title,
            'income_group': 'Income Group'
        },
        category_orders={'income_group': ['LI', 'LM', 'UM', 'HI']},  # Order the income group categories
        trendline="ols"
    )

    # Update layout to remove the legend and gridlines
    fig.update_layout(
        height=500,
        showlegend=False,  # Hide the legend
        plot_bgcolor='white',  # Set background to white
        paper_bgcolor='white',  # Set the paper background to white
        xaxis=dict(showgrid=False, zeroline=False),  # Remove x-axis gridlines
        yaxis=dict(showgrid=False, zeroline=False)   # Remove y-axis gridlines
    )

    # Display the plot in Streamlit
    st.plotly_chart(fig, use_container_width=True)


# Sidebar Menu
with st.sidebar:
    selected = option_menu(
        menu_title="Main Menu",  # required
        options=["Home", "Global Overview", "Finland - Case Study", "Case Study 2", "References"],  # required
        default_index=0,  # optional
    )

if selected == "Home":
    st.title("How do sustainable environmental practices of countries correlate with the well-being and happiness of their citizens?")
    st.text("Our project explores the link between a country’s sustainable practices and the happiness and mental wellbeing of its residents. As sustainability becomes a global priority, our goal is to explore specifics of these correlations.")

if selected == "Global Overview":
    st.title(f"{selected} - are residents of sustainable countries happier?")
    st.text("To explore the link between sustainability and happiness, we will first examine global trends of reported happiness and sustainability measured by SDGI. We will also consider countries of varying income levels to take different economic contexts into consideration.")
    st.header("Global Happiness Score in 2023")
    st.text("The Happiness Score, also known as the Happiness Index, measures the well-being and life satisfaction of people across different countries. The results are based on self-assessments of happiness, well-being, sustainability, and resilience.")
    display_map(df, 'happiness_score', 'YlGn', 1.86, 7.8)
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        display_top_three(df, 'happiness_score')
    with col2:
        display_world_average(df, 'happiness_score')
    with col3:
        display_country_count(df, 'happiness_score')
    st.header("SDGI")
    st.text("The Sustainable Development Goals Index (SDGI) measures and ranks countries' progress toward achieving the United Nations' 17 Sustainable Development Goals using various performance indicators.")
    display_map(df, 'sdgi', 'YlGn', 40, 86.5)
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        display_top_three(df, 'sdgi')
    with col2:
        display_world_average(df, 'sdgi')
    with col3:
        display_country_count(df, 'sdgi')
    st.text("The two maps that follow show measurements of happiness and sustainability across different nations worldwide, based on international standards. While developed countries tend to score higher on both measures, suggesting a possible relationship, the results are ambiguous and do not necessarily indicate causation.")
    st.header("Relation of Happiness Score and...")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<h2 style='text-align: center;'>SDGI</h2>", unsafe_allow_html=True)
        create_scatterplot_per_income(df, 'happiness_score', 'sdgi', 'Happiness Score', 'SDGI')
    with col2:
        st.markdown("<h2 style='text-align: center;'>GDP per capita</h2>", unsafe_allow_html=True)
        create_scatterplot_per_income(df, 'happiness_score', 'per_capita_gdp',  'Happiness Score', 'GDP per capita')
    with col3:
        st.markdown("<h2 style='text-align: center;'>HDI</h2>", unsafe_allow_html=True)
        create_scatterplot_per_income(df, 'happiness_score', 'hdi', 'Happiness Score', 'HDI')
    st.text("As we can see from the first graph, the Happiness Score and GDP per capita are positively correlated. Happiness tends to be higher in nations with higher GDP per capita. Economic wealth is not the only factor that determines happiness, though, as evidenced by the disparity in Happiness Scores between nations with lower to middle GDP per capita.")
    st.text("The second chart shows how the HDI and Happiness Score are related, with a higher correlation than GDP per capita. The Happiness Score increases dramatically as the HDI rises, reflecting advancements in living standards, health, and education.")
    st.text("The Happiness Score and the SDGI have the strongest correlation, as shown in the third graph. Happiness is consistently higher in nations with higher SDGI scores, which show progress toward achieving sustainable development goals such as social equality, environmental protection, and poverty reduction. ")
    st.header("Ambiguous results")
    st.markdown("### Recycling rate seems to...")
    col1, col2 = st.columns(2)  
    with col1:
        st.markdown("#### ...positively correlate with happiness among upper middle income countries...")
        create_scatterplot(df, 'recycling_rate', 'happiness_score', 'UM', 'Recycling rate', 'Happiness Score')
    with col2:
        st.markdown("#### ...but negatively among lower middle income countries.")
        create_scatterplot(df, 'recycling_rate', 'happiness_score', 'LM', 'Recycling rate', 'Happiness Score')
    st.markdown("### Biocapacity of cropland rate seems to...")
    col1, col2 = st.columns(2)  
    with col1:
        st.markdown("#### ...positively correlate with happiness among upper middle income countries...")
        create_scatterplot(df, 'cropland', 'happiness_score', 'UM', 'Cropland', 'Happiness Score')
    with col2:
        st.markdown("#### ...but slightly negatively whithin high income countries.")
        create_scatterplot(df, 'cropland', 'happiness_score', 'HI', 'Cropland', 'Happiness Score')
    st.text("The graphs suggests that the relationship between environmental factors and happiness is more complex than a simple positive correlation. It also highlights the potential influence of economic factors on the relationship between environmental sustainability and well-being.")
    st.header("Conclusion")
    st.text("While some trends and connections may be observed, involving more extensive studies over a longer period and possibly incorporating additional variables to better understand the complex relationships between sustainability and happiness, we need to investigate further.")
    st.text("Further analysis, including more comprehensive data and long-term studies, is essential to fully understand the complex interplay between sustainability and happiness.  While certain indicators like GDP, HDI, and SDGI show a positive correlation with happiness, the analysis of environmental factors such as recycling rates and biocapacity reveals more nuanced trends that vary by income level. In conclusion, more research is needed to draw firm conclusions about whether sustainability directly leads to higher happiness, considering the multitude of variables at play.")

if selected == "Finland - Case Study":
    st.title("Why is Finland so happy? Exploring sustainability's role")
    st.markdown("""
    Finland consistently ranks as the happiest country in the world. This dashboard explores the 
    factors contributing to Finland's happiness, with a focus on sustainable practices.
    """)

    # Extract relevant metrics
    happiness_score = finland_data['happiness_score'].values[0]
    sdgi = finland_data['sdgi'].values[0]
    hdi = finland_data['hdi'].values[0]
    gdp = finland_data['per_capita_gdp'].values[0]


    # Display key metrics
    st.subheader("Key Metrics for Finland in 2023")
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Happiness Score", f"{happiness_score:.2f}", "Rank: #1")
    col2.metric("SDGI (Sustainable Development Goals Index)", f"{sdgi:.2f}", "Rank: #1")
    col3.metric("HDI", f"{hdi:.2f}", "Rank #7")
    col4.metric("GDP per capita", f"${int(gdp):,}", "Rank #16")

    # Display the dataset
    st.write("### Happiness Score Time Series for the Top 3 Countries")

    # You can select which countries to display (e.g., Top 3 based on a certain metric)
    top_3_countries = timeseries_df.mean(axis=1).nlargest(3).index.tolist()

    # Filter the dataframe for the top 3 countries
    top_3_df = timeseries_df.loc[top_3_countries]

    # Create an interactive plot for the time series
    fig = px.line(top_3_df.T, 
                labels={'value': 'Happiness Score', 'index': 'Year'})

    # Display the plot
    st.plotly_chart(fig)


if selected == "Case Study 2":
    st.title(f"Title {selected}")
    """CASE STUDY 2 CODE"""