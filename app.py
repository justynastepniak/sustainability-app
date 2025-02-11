import streamlit as st
import pandas as pd
import altair as alt
from streamlit_option_menu import option_menu
import plotly.express as px
import plotly.graph_objects as go
import requests
from branca.colormap import linear
from branca.colormap import LinearColormap
import folium

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
renewables_df = pd.read_csv('EUrenewables2020.csv')
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
    colors = {
        'LI' : '#9b5de5',
        'LM' : '#f15bb5',
        'UM' : '#fee440',
        'HI' : '#00f5d4',
    }

    fig = px.scatter(
        data,
        x=x_value,
        y=y_value,
        hover_name='country',  # Display country names on hover
        color='income_group',  # Color points based on 'income_group'
        color_discrete_map=colors,
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
    fig.update_traces(line=dict(color='#A9A9A9'), selector=dict(mode='lines'))

    # Update layout to remove the legend and gridlines
    fig.update_layout(
        height=450,
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

    # color based on income group
    colors = {
        'LI' : '#9b5de5',
        'LM' : '#f15bb5',
        'UM' : '#fee440',
        'HI' : '#00f5d4',
    }
    # Create scatterplot
    fig = px.scatter(
        filtered_data,
        x=x_value,
        y=y_value,
        hover_name='country',  # Display country names on hover
        color='income_group',  # Color points based on 'income_group'
        color_discrete_map=colors,
        labels={  # Custom axis labels
            x_value: x_title,
            y_value: y_title,
            'income_group': 'Income Group'
        },
        category_orders={'income_group': ['LI', 'LM', 'UM', 'HI']},  # Order the income group categories
        trendline="ols"
    )

    fig.update_traces(line=dict(color='#A9A9A9'), selector=dict(mode='lines'))

    # Update layout to remove the legend and gridlines
    fig.update_layout(
        height=350,
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
        options=["Home", "Introduction / Global Overview", "Finland - Case Study", "Eco-anxiety", "References"],  # required
        default_index=0,  # optional
    )

if selected == "Home":
    st.title("How do sustainable environmental practices of countries correlate with the well-being and happiness of their citizens?")
    st.markdown("""Our project explores the link between a country’s 
    sustainable practices and the happiness and mental wellbeing of its residents. As sustainability becomes a 
    global priority, our goal is to explore specifics of these correlations.""")

if selected == "Introduction / Global Overview":
    st.title(f"{selected} - are residents of sustainable countries happier?")
    st.markdown("""To explore the link between **sustainability and happiness**, we will first examine global trends 
    of reported happiness and sustainability measured by SDGI. We will also consider countries of <span style='background-color: LemonChiffon;'>varying income 
    levels</span> to take different economic contexts into consideration.""", unsafe_allow_html=True)

    st.header("Global Happiness Score in 2023")
    st.markdown("""The Happiness Score, also known as the Happiness Index, measures the well-being and life satisfaction of people across different countries. 
    The results are based on **self-assessments of happiness, well-being, sustainability, and resilience.**""")
    
    display_map(df, 'happiness_score', 'YlGn', 1.86, 7.8)
    
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        display_top_three(df, 'happiness_score')
    with col2:
        display_world_average(df, 'happiness_score')
    with col3:
        display_country_count(df, 'happiness_score')

    st.header("The Sustainable Development Goals Index in 2023")
    st.markdown("""The Sustainable Development Goals Index (SDGI) measures and ranks countries' progress toward achieving [the United Nations' 17 
    Sustainable Development Goals](https://sdgs.un.org/goals) using various performance indicators. """)

    display_map(df, 'sdgi', 'YlGn', 40, 86.5)

    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        display_top_three(df, 'sdgi')
    with col2:
        display_world_average(df, 'sdgi')
    with col3:
        display_country_count(df, 'sdgi')

    st.markdown("""The two maps that follow show measurements of happiness and sustainability across different nations worldwide, 
    based on international standards. While developed countries tend to score higher on both measures, suggesting a possible relationship,  <span style='background-color: LemonChiffon;'>
    the results are ambiguous and do not necessarily indicate causation.</span>""", unsafe_allow_html=True)
    st.markdown("**In the next steps, we'll visualise correlations between Happines Score and SDGI and compare them to economic measures.**")
    
    st.header("Relation of Happiness Score and...")
    st.markdown("""<div style='text-align: center;'>Legend: <span style='color:#9b5de5;'>⬤</span> Low Income <span style='color:#f15bb5;'>⬤</span> Lower Middle Income   <span style='color:#fee440;'>⬤</span> Lower Upper Income   <span style='color:#00f5d4;'>⬤</span> High Income
    </div>""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.markdown("<h3 style='text-align: center;'>SDGI</h3>", unsafe_allow_html=True)
        create_scatterplot_per_income(df, 'happiness_score', 'sdgi', 'Happiness Score', 'SDGI')
        st.markdown(""" <div style='text-align: justify;'>The Happiness Score and the <b>SDGI</b> have <span style='background-color: LemonChiffon;'>a strong correlation,
                    suggesting sustainable practices might be linked to overall wellbeing.</span>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("<h3 style='text-align: center;'>GDP per capita</h33>", unsafe_allow_html=True)
        create_scatterplot_per_income(df, 'happiness_score', 'per_capita_gdp',  'Happiness Score', 'GDP per capita')
        st.markdown(""" <div style='text-align: justify;'>The Happiness Score and <b>GDP (Gross Domestic Product) per capita</b> also correlate positively, but the value of correlation coefficient is lower.
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("<h3 style='text-align: center;'>HDI</h3>", unsafe_allow_html=True)
        create_scatterplot_per_income(df, 'happiness_score', 'hdi', 'Happiness Score', 'HDI')
        st.markdown(""" <div style='text-align: justify;'>The same holds true for <b>HDI (Human Development Index)</b> and the Happiness Score.
        </div>""", unsafe_allow_html=True)
    
    st.markdown("")
    st.markdown("""Overall, <b>SDGI shows a stronger correlation with Happiness Score than economic measures</b> such as GDP per capita or HDI. 
                However, a country's income must be considered when analyzing these measures. 
                <span style='background-color:#00f5d4;'>High-income countries</span> consistently outperform lower-income countries in terms of both happiness and sustainability, <b>as they have the resources to do so.</b>
                """, unsafe_allow_html=True)
    st.markdown("""
                In next steps we will explore in depth what are correlations between specific practices and happiness.
            """)

    st.header("Happiness Score and (un)sustainable practices")
    st.markdown("""<div style='text-align: center;'>Legend: <span style='color:#9b5de5;'>⬤</span> Low Income <span style='color:#f15bb5;'>⬤</span> Lower Middle Income   <span style='color:#fee440;'>⬤</span> Lower Upper Income   <span style='color:#00f5d4;'>⬤</span> High Income
    </div>""", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        create_scatterplot_per_income(df, 'happiness_score', 'recycling_rate', 'Happiness Score', 'Recycling Rate')
    with col2:
        create_scatterplot_per_income(df, 'happiness_score', 'forest_land', 'Happiness Score', 'Forest Land')
    with col3:
        create_scatterplot_per_income(df, 'happiness_score', 'per_capita_waste_kg', 'Happiness Score', 'Per capita plastic waste')
    with col4:
        create_scatterplot_per_income(df, 'happiness_score', 'carbon_footprint', 'Happiness Score', 'Carbon Footprint')

    st.markdown("""Interestingly, <span style='background-color: LemonChiffon;'>happiness scores are positively correlated with both sustainable and unsustainable practices.</span>
                Countries that <b>recycle more and have more forest land</b> (graph 1 & 2) tend to have higher happiness scores, showing the benefits of environmental care. 
                At the same time, countries with <b>higher plastic waste and carbon footprints</b> (graph 3 & 4) also often report higher happiness, 
                likely due to economic growth and consumption. This suggests that while sustainability contributes to well-being, 
                economic development linked to unsustainable practices can also play a role in increasing happiness.""", unsafe_allow_html=True)

    st.header("Results by income groups")
    
    st.markdown("""To gain a deeper insight, we will investigate correlations separately **for different income groups.**
    """)
    st.markdown("""<div style='text-align: center;'>Legend: <span style='color:#9b5de5;'>⬤</span> Low Income <span style='color:#f15bb5;'>⬤</span> Lower Middle Income   <span style='color:#fee440;'>⬤</span> Lower Upper Income   <span style='color:#00f5d4;'>⬤</span> High Income
    </div>""", unsafe_allow_html=True)

    st.subheader("Recycling rate")
    col1, col2, col3, col4 = st.columns(4)  
    with col1:
        create_scatterplot(df, 'recycling_rate', 'happiness_score', 'LI', 'Recycling rate', 'Happiness Score')
    with col2:
        create_scatterplot(df, 'recycling_rate', 'happiness_score', 'LM', 'Recycling rate', 'Happiness Score')
    with col3:
        create_scatterplot(df, 'recycling_rate', 'happiness_score', 'UM', 'Recycling rate', 'Happiness Score')
    with col4:
        create_scatterplot(df, 'recycling_rate', 'happiness_score', 'HI', 'Recycling rate', 'Happiness Score')
    st.markdown("The results show that depending on income level of a country, <span style='background-color: LemonChiffon;'>recycling rate can be either positivey or negatively correlated.</span>", unsafe_allow_html=True)
    st.subheader("Carbon footprint")
    col1, col2, col3, col4 = st.columns(4)  
    with col1:
        create_scatterplot(df, 'carbon_footprint', 'happiness_score', 'LI', 'Carbon footprint', 'Happiness Score')
    with col2:
        create_scatterplot(df, 'carbon_footprint', 'happiness_score', 'LM', 'Carbon footprint', 'Happiness Score')
    with col3:
        create_scatterplot(df, 'carbon_footprint', 'happiness_score', 'UM', 'Carbon footprint', 'Happiness Score')
    with col4:
        create_scatterplot(df, 'carbon_footprint', 'happiness_score', 'HI', 'Carbon footprint', 'Happiness Score')
    st.markdown("In case of total carbon footprit, it seems that its correlation with happines <span style='background-color: LemonChiffon;'>decreses as income status increases.</span>", unsafe_allow_html=True)
    st.subheader("Total biocapacity")
    col1, col2, col3, col4 = st.columns(4)  
    with col1:
        create_scatterplot(df, 'total_biocapacity', 'happiness_score', 'LI', 'Total Biocapacity', 'Happiness Score')
    with col2:
        create_scatterplot(df, 'total_biocapacity', 'happiness_score', 'LM', 'Total Biocapacity', 'Happiness Score')
    with col3:
        create_scatterplot(df, 'total_biocapacity', 'happiness_score', 'UM', 'Total Biocapacity', 'Happiness Score')
    with col4:
        create_scatterplot(df, 'total_biocapacity', 'happiness_score', 'HI', 'Total Biocapacity', 'Happiness Score')
    st.markdown("Total biocapacity of a country seems to be <span style='background-color: LemonChiffon;'>irrelevant for low and middle income countries</span>, and <span style='background-color: LemonChiffon;'>correlate positively with happiness for high income countries.</span>",unsafe_allow_html=True)
    st.header("Conclusion")
    st.markdown("""
    
    **Further analysis with comprehensive data and long-term studies is needed to understand the complex relationship between sustainability and happiness.**
    While indicators like GDP, HDI, and SDGI correlate positively with happiness, environmental factors such as recycling rates and biocapacity reveal nuanced trends. 
    Low and middle-income countries may achieve sustainability yet struggle with economic challenges, or lack resources for solutions tailored to wealthier nations. 
    More research is required to determine if sustainability directly impacts happiness, considering these multifaceted variables.
    
    """)
    st.markdown("""**As the next step in our research, we will analyze Finland,** the happiest and most sustainable country in the world according to the data, 
    focusing on exploring the role of sustainable practices in shaping its high happiness levels. """)

    st.header("Data Sources")
    st.markdown("""
                1. [World Happiness Report 2023](https://www.kaggle.com/datasets/sazidthe1/global-happiness-scores-and-factors?select=WHR_2023.csv)
                2. [Global Ecological Footprint 2023](https://www.kaggle.com/datasets/jainaru/global-ecological-footprint-2023)
                3. [Global Plastic Waste 2023](https://www.kaggle.com/datasets/prajwaldongre/global-plastic-waste-2023-a-country-wise-analysis)
    
    """)
if selected == "Finland - Case Study":
    st.title("Why is Finland so happy? Exploring sustainability's role")
    st.markdown("""
    <span style='background-color: LemonChiffon;'>Finland consistently ranks as the happiest country in the world.</span> This dashboard explores the 
    factors contributing to Finland's happiness, with a focus on sustainable practices.
    """, unsafe_allow_html=True)

    # Extract relevant metrics
    happiness_score = finland_data['happiness_score'].values[0]
    sdgi = finland_data['sdgi'].values[0]
    hdi = finland_data['hdi'].values[0]
    gdp = finland_data['per_capita_gdp'].values[0]


    # Display key metrics
    st.header("Key Metrics for Finland in 2023")
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Happiness Score", f"{happiness_score:.2f}", "Rank: #1")
    col2.metric("SDGI (Sustainable Development Goals Index)", f"{sdgi:.2f}", "Rank: #1")
    col3.metric("HDI", f"{hdi:.2f}", "Rank #7")
    col4.metric("GDP per capita", f"${int(gdp):,}", "Rank #16")

    st.markdown("**In 2023, Finland ranked #1 globally in both Happiness and the SDGI**, reflecting its strong quality of life and sustainability efforts. However, its lower (but still relatively high) rankings in HDI and GDP per capita suggest that the correlations between happiness and economic indicators might be weaker in comparison with sustainability indicators.")

    # Display the dataset
    st.header("Happiness Score Time Series for the Top 3 Countries")

    # Select the top 3 countries based on their average happiness score
    top_3_countries = timeseries_df.mean(axis=1).nlargest(3).index.tolist()

    # Filter the dataframe for the top 3 countries
    top_3_df = timeseries_df.loc[top_3_countries]

    # Transpose the DataFrame for Plotly
    top_3_df_t = top_3_df.T.reset_index()
    top_3_df_t = top_3_df_t.melt(id_vars='index', var_name='Country', value_name='Happiness Score')

    # Define a color mapping, explicitly setting Finland to red
    color_map = {
        top_3_countries[0]: 'red',    # Finland
        top_3_countries[1]: 'lightgreen',  # Second country
        top_3_countries[2]: 'lightblue'    # Third country
    }

    # Create an interactive plot for the time series
    fig = px.line(
        top_3_df_t,
        x='index',
        y='Happiness Score',
        color='Country',
        color_discrete_map=color_map,  # Apply the color map
        labels={'index': 'Year'}
    )

    # Display the plot
    st.plotly_chart(fig)

    st.write("Finland has consistently ranked 1st in the Global Happiness Report since 2018, consistently outperforming other happy Nordic countries like Denmark and Iceland. ")

    st.header("But what is the reason for it?")
    st.markdown("Some articles point to sustainable factors like proximity of nature or unpolluted air. [[source](https://www.businessfinland.com/press-release/2024/why-is-finland-the-happiest-country-in-the-world-for-the-7th-time/)] We'll see if data matches those assumptions comparing Finland's sustainable efforts to similar EU-27 countries.")
    st.header("Proximity to nature")
    st.text("To analyze proximity to nature, many different factors can be taken into consideration. We'll have a look at forest land biocapacity and total biocapacity (measured in global hectares per person).")

    # Filter the DataFrame for 'region_x' = 'EU-27'
    eu27_countries = df[df['region_x'] == 'EU-27']

    col1, col2 = st.columns(2)
    with col1:
        # Get the top 5 countries by forest_land
        top_countries_eu27 = eu27_countries.sort_values(by='forest_land', ascending=False).head(5)
        # Add a column to identify Finland for custom coloring
        top_countries_eu27['Color'] = top_countries_eu27['country'].apply(lambda x: 'Finland' if x == 'Finland' else 'Other')

        # Create an Altair bar chart
        bar_chart = alt.Chart(top_countries_eu27).mark_bar().encode(
            x=alt.X('country:N', sort='-y', title='Country'),
            y=alt.Y('forest_land:Q', title='Forest Land'),
            color=alt.Color('Color:N', legend=None, scale=alt.Scale(domain=['Finland', 'Other'], range=['#d62728', 'lightgreen'])),
            tooltip=['country', 'forest_land']
        ).properties(
            title='Top 5 Countries by Forest Land in EU-27',
            width=700,
            height=400
        ).configure_axis(
            labelFontSize=12,
            titleFontSize=14
        ).configure_title(
            fontSize=16,
            anchor='start',
            color='black'
        )

        # Display the bar chart in Streamlit
        st.altair_chart(bar_chart, use_container_width=True)
    with col2:
        # Get the top 5 countries by total_biocapacity
        top_countries_eu27 = eu27_countries.sort_values(by='total_biocapacity', ascending=False).head(5)
        top_countries_eu27['Color'] = top_countries_eu27['country'].apply(lambda x: 'Finland' if x == 'Finland' else 'Other')
        # Create an Altair bar chart
        bar_chart = alt.Chart(top_countries_eu27).mark_bar().encode(
            x=alt.X('country:N', sort='-y', title='Country'),
            y=alt.Y('total_biocapacity:Q', title='Total Biocapacity'),
            color=alt.Color('Color:N', legend=None, scale=alt.Scale(domain=['Finland', 'Other'], range=['#d62728', 'lightgreen'])),
            tooltip=['country', 'total_biocapacity']
        ).properties(
            title='Top 5 Countries by Total Biocapacity in EU-27',
            width=700,
            height=400
        ).configure_axis(
            labelFontSize=12,
            titleFontSize=14
        ).configure_title(
            fontSize=16,
            anchor='start',
            color='black'
        )

        # Display the bar chart in Streamlit
        st.altair_chart(bar_chart, use_container_width=True)

    st.markdown("**Finland ranks first among EU-27 countries in terms of forest land and total biocapacity, emphasizing its deep connection to nature.**") 
    
    st.header("Clean Energy")

    st.text("To assess Finland's performance in electricity production, we will examine the total renewable electricity in TWh generated by EU-27 countries (solar, biomass, wind, and hydroelectric power).")

    # Get the top 10 countries by renewables
    top_countries_eu27 = renewables_df.sort_values(by='electricity_from_renewables_twh', ascending=False).head(10)

    # Add a new column to identify if the country is Finland
    top_countries_eu27['highlight'] = top_countries_eu27['entity'].apply(lambda x: 'red' if x == 'Finland' else 'muted_blue')

    # Create an Altair bar chart
    bar_chart = alt.Chart(top_countries_eu27).mark_bar().encode(
        x=alt.X('entity:N', sort='-y', title='Country'),
        y=alt.Y('electricity_from_renewables_twh:Q', title='Electricity from Renewables (TWh)'),
        color=alt.Color('highlight:N', legend=None, 
                        scale=alt.Scale(domain=['red', 'muted_blue'], range=['red', 'lightblue'])),
        tooltip=['entity', 'electricity_from_renewables_twh']
    ).properties(
        title='Top 10 Countries by Electricity from Renewables in EU-27, 2020',
        width=700,
        height=400
    ).configure_axis(
        labelFontSize=12,
        titleFontSize=14
    ).configure_title(
        fontSize=16,
        anchor='start',
        color='black'
    )

    # Display the bar chart in Streamlit
    st.altair_chart(bar_chart, use_container_width=True)

    st.markdown("Although Finland does not rank 1st in terms of total renewable electricity production (ranking 7th), <span style='background-color: LemonChiffon;'>a closer examination of the percentage share of different energy sources may provide more valuable insights.</span>", unsafe_allow_html=True)
    st.subheader("Energy in Finland by source")
    col1, col2 = st.columns(2)
    
    # Filter the DataFrame for Finland
    finland_data = renewables_df[renewables_df['entity'] == 'Finland']

    # Ensure there is only one row for Finland in the dataset (e.g., the latest year)
    finland_data = finland_data.iloc[-1]
    # Calculate the components of electricity production
    electricity_from_renewables = finland_data['electricity_from_renewables_twh']
    electricity_from_fossil = finland_data['electricity_from_fossil_fuels_twh']
    electricity_from_nuclear = finland_data['electricity_from_nuclear_twh']

    # Calculate the total electricity production
    total_electricity = electricity_from_renewables + electricity_from_fossil + electricity_from_nuclear

    # Calculate percentages for the pie chart
    data = pd.DataFrame({
        'Source': ['Renewables', 'Fossil Fuels', 'Nuclear'],
        'Electricity (TWh)': [electricity_from_renewables, electricity_from_fossil, electricity_from_nuclear],
        'Percentage': [
            (electricity_from_renewables / total_electricity) * 100,
            (electricity_from_fossil / total_electricity) * 100,
            (electricity_from_nuclear / total_electricity) * 100
        ]
    })

    # Create the pie chart
    pie_chart = alt.Chart(data).mark_arc(innerRadius=50).encode(
        theta=alt.Theta(field="Electricity (TWh)", type="quantitative"),
        color=alt.Color(
            'Source:N',
            scale=alt.Scale(
                domain=['Renewables', 'Fossil Fuels', 'Nuclear'],
                range=['#2ca02c', '#ff7f0e', '#1f77b4']  # Green for renewables, orange for fossil, blue for nuclear
            )
        ),
        tooltip=[
            alt.Tooltip('Source:N', title='Source'),
            alt.Tooltip('Electricity (TWh):Q', title='Electricity (TWh)', format=',.2f'),
            alt.Tooltip('Percentage:Q', title='Percentage', format='.2f')
        ],
        text=alt.Text('Percentage:Q', format='.1f')  # Show percentage on the pie slices
    ).properties(
        width=400,
        height=300
    ).configure_title(
        fontSize=16,
        anchor='start',
        color='black'
    ).configure_view(
        strokeOpacity=0  # Remove stroke around the pie chart
    )

    # Display the pie chart and metrics in Streamlit
    cola, colb = st.columns([2, 1])

    with cola:
        # Displaying metrics in columns
        col1, col2, col3 = st.columns(3)
        col1.metric("Renewables", f"{data[data['Source'] == 'Renewables']['Percentage'].values[0]:.1f}%", "Green Energy")
        col2.metric("Nuclear Energy", f"{data[data['Source'] == 'Nuclear']['Percentage'].values[0]:.1f}%", "Low Carbon")
        col3.metric("Fossil Fuels", f"{data[data['Source'] == 'Fossil Fuels']['Percentage'].values[0]:.1f}%", "Non-Renewable")
        
        # Explanatory text below the metrics
        st.markdown("""
        <span style='background-color: LemonChiffon;'>Finland's electricity production is primarily powered by renewable sources,</span> with a significant share coming from wind, solar, and bioenergy. 
        Nuclear energy also plays a crucial role in the country's low-carbon energy mix. However, fossil fuels still account for a portion of the electricity generation,
        reflecting the country's ongoing transition towards more sustainable energy solutions.
        """, unsafe_allow_html=True)

    with colb:
        # Display the pie chart in Streamlit
        st.altair_chart(pie_chart)

    st.subheader("Energy consumption")
        # Filter relevant columns for visualization
    energy_consumption_df = renewables_df[['entity', 'primary_energy_consumption_per_capita_kwhperson']]

    # Sort the values by primary energy consumption per capita in descending order and take the top 10
    top_10_energy_consumption_df = energy_consumption_df.sort_values(by='primary_energy_consumption_per_capita_kwhperson', ascending=False).head(10)

    # Add a column to identify Finland for custom coloring
    top_10_energy_consumption_df['Color'] = top_10_energy_consumption_df['entity'].apply(lambda x: 'Finland' if x == 'Finland' else 'Other')

    # Create a bar chart
    bar_chart = alt.Chart(top_10_energy_consumption_df).mark_bar().encode(
        x=alt.X('primary_energy_consumption_per_capita_kwhperson:Q', title='Primary Energy Consumption per Capita (kWh)'),
        y=alt.Y('entity:N', sort='-x', title='Country'),
        color=alt.Color('Color:N', scale=alt.Scale(domain=['Finland', 'Other'], range=['red', 'lightblue'])),  # Red for Finland, muted for others
        tooltip=[
            alt.Tooltip('entity:N', title='Country'),
            alt.Tooltip('primary_energy_consumption_per_capita_kwhperson:Q', title='Consumption (kWh)', format='.2f')
        ]
    ).properties(
        title="Top 10 Countries by Primary Energy Consumption per Capita in EU-27",
        width=700,
        height=400
    ).configure_title(
        fontSize=16,
        anchor='start',
        color='black'
    )

    # Display the bar chart in Streamlit
    st.altair_chart(bar_chart, use_container_width=True)

    st.markdown("**Although coming mostly from renewable sources, energy consumption measured per capita in Finland is quite high, ranking 6th in Euro-27 countries.**")

    st.header("Plastic waste management")
    st.text("A look into country's waste production and management can give us insights into it's sustainable practices. We'll inspect Finland's per capita plastic waste production and the rate of recycling.")
    col1, col2 = st.columns(2)

    with col1:

        # Filter the DataFrame for countries in the EU-27 region
        eu27_waste_df = df[df['region_x'] == 'EU-27'][['country', 'per_capita_waste_kg']]

        # Sort the values by per capita waste in ascending order and take the top 20
        top_20_eu27_waste_df = eu27_waste_df.sort_values(by='per_capita_waste_kg', ascending=False).head(20)

        # Add a column to identify Finland for custom coloring
        top_20_eu27_waste_df['Color'] = top_20_eu27_waste_df['country'].apply(lambda x: 'Finland' if x == 'Finland' else 'Other')
        # Calculate the average per capita waste for EU-27
        eu27_avg_waste = eu27_waste_df['per_capita_waste_kg'].mean()
        # Create a vertical bar chart for per capita waste
        bar_chart_eu27_waste = alt.Chart(top_20_eu27_waste_df).mark_bar().encode(
            y=alt.Y('country:N', sort='-x', title='Country'),
            x=alt.X('per_capita_waste_kg:Q', title='Per Capita Waste (kg)'),
            color=alt.Color('Color:N', scale=alt.Scale(domain=['Finland', 'Other'], range=['#d62728', 'lightgray'])),  # Red for Finland
            tooltip=[
                alt.Tooltip('country:N', title='Country'),
                alt.Tooltip('per_capita_waste_kg:Q', title='Per Capita Waste (kg)', format='.2f')
            ]
        )

        # Add the vertical line for EU-27 average waste
        line_avg = alt.Chart(pd.DataFrame({'x': [eu27_avg_waste]})).mark_rule(color='black').encode(
        x='x:Q'
        )

        # Layer the bar chart and vertical line together using alt.layer
        final_chart = alt.layer(bar_chart_eu27_waste, line_avg).properties(
            title="Top 20 EU-27 Countries by Per Capita Plastic Waste",
            width=700,
            height=400
        ).configure_axis(
            labelFontSize=12,
            titleFontSize=14
        )

        # Display the bar chart with full container width
        st.altair_chart(final_chart, use_container_width=True)


        finland_waste = top_20_eu27_waste_df[top_20_eu27_waste_df['country'] == 'Finland']['per_capita_waste_kg'].values[0]

        # Display the EU-27 average per capita waste as a metric
        cola, colb = st.columns(2)
        with cola:
            st.metric("EU-27 Average Per Capita Waste", f"{eu27_avg_waste:.2f} kg")
        with colb:
            st.metric("Finland's Per Capita Waste", f"{finland_waste:.2f} kg")

        st.text("Finland ranks 9th in plastic waste production per capita among EU-27 countries, and it's only slightly under average.")

    with col2:
        # Filter the DataFrame for countries in the EU-27 region
        eu27_recycling_rate_df = df[df['region_x'] == 'EU-27'][['country', 'recycling_rate']]

        # Sort the values by recycling rate in descending order and take the top 20
        top_20_eu27_recycling_rate_df = eu27_recycling_rate_df.sort_values(by='recycling_rate', ascending=False).head(20)

        # Add a column to identify Finland for custom coloring
        top_20_eu27_recycling_rate_df['Color'] = top_20_eu27_recycling_rate_df['country'].apply(lambda x: 'Finland' if x == 'Finland' else 'Other')
        
        # Calculate the average recycling rate for EU-27
        eu27_avg_recycling_rate = eu27_recycling_rate_df['recycling_rate'].mean()
       
        # Create a vertical bar chart for recycling rate
        bar_chart_eu27_recycling = alt.Chart(top_20_eu27_recycling_rate_df).mark_bar().encode(
            y=alt.Y('country:N', sort='-x', title='Country'),
            x=alt.X('recycling_rate:Q', title='Recycling Rate (%)'),
            color=alt.Color('Color:N', scale=alt.Scale(domain=['Finland', 'Other'], range=['#d62728', 'lightgray'])),  # Red for Finland, muted blue for others
            tooltip=[
                alt.Tooltip('country:N', title='Country'),
                alt.Tooltip('recycling_rate:Q', title='Recycling Rate (%)', format='.2f')
            ]
        )

        # Add the vertical line for EU-27 average waste
        line_avg = alt.Chart(pd.DataFrame({'x': [eu27_avg_recycling_rate]})).mark_rule(color='black').encode(
        x='x:Q'
        )

        # Layer the bar chart and vertical line together using alt.layer
        final_chart = alt.layer(bar_chart_eu27_recycling, line_avg).properties(
            title="Top 20 EU-27 Countries by Per Capita Recycling Rate",
            width=700,
            height=400
        ).configure_axis(
            labelFontSize=12,
            titleFontSize=14
        )

        # Display the bar chart with full container width
        st.altair_chart(final_chart, use_container_width=True)
        # Calculate Finland's per capita waste
        finland_rec = eu27_recycling_rate_df[eu27_recycling_rate_df['country'] == 'Finland']['recycling_rate'].values[0]

        cola, colb =  st.columns(2)
        # Display the EU-27 average recycling rate as a metric
        with cola:
            st.metric("EU-27 Average Recycling Rate", f"{eu27_avg_recycling_rate:.2f}%")
        with colb:
            st.metric("Finland's Recycling Rate", f"{finland_rec:.2f} %")

        st.text("Finland's average recycling rate is about 5 p.p. higher than EU-27's average and it ranks on the 10th place among those countries.")

    st.markdown("""**To sum up, Finalnd's plastic waste management does not significantly deviate from EU's average.**""")

    st.header("Other factors")
    col1, col2 = st.columns(2)
    with col1:

        category_labels = {
            'social_support': 'Social Support',
            'healthy_life_expectancy': 'Healthy Life Expectancy',
            'freedom_to_make_life_choices': 'Freedom to Make Life Choices',
            'generosity': 'Generosity',
            'perceptions_of_corruption': 'Perceptions of Corruption'
        }

        # Columns to include in the radar chart
        categories = list(category_labels.keys())

        # Normalize each column by its maximum value
        normalized_df = df.copy()
        for column in categories:
            normalized_df[column] = normalized_df[column] / normalized_df[column].max()

        # Filter the data for Finland
        finland_data = normalized_df[normalized_df['country'] == 'Finland']

        # Extract the normalized values for Finland
        values = finland_data[categories].values.flatten().tolist()

        # Close the radar chart by repeating the first value
        values += values[:1]
        labels = [category_labels[cat] for cat in categories] + [category_labels[categories[0]]]

        # Create a radar chart
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=labels,
            fill='toself',
            name='Finland',
            line_color='rgba(235, 206, 235, 1)',  # Muted blue for the line
            fillcolor='rgba(235, 206, 235, 0.5)'  # Muted blue with transparency for fill
        ))

        # Update layout
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]  # Normalized scale from 0 to 1
                )
            ),
            title="Radar Chart: Finland's Scores (Normalized to Max Values)",
            showlegend=False
        )

        # Display the radar chart in Streamlit
        st.plotly_chart(fig)

    with col2:    
        st.markdown(
            """
            <div style="margin: 50px 0;">
                When we take into consideration <b> other categories, that are not directly related to sustainability,</b> 
                <span style='background-color: LemonChiffon;'>Finland scores high in metrics measuring social support, healthy life expectancy, 
                freedom to make life choices, and perceptions of corruption.</span> These factors might also influence happiness of Finnish citizens. 
                Generosity, in contrast, is comparatively lower, indicating it may play a less prominent role in the broader context of happiness.
                <br><br>

            </div>
            """,
            unsafe_allow_html=True
        )

    st.header("Conclusion")
    st.markdown("""<span style='background-color: LemonChiffon;'>The link between Finland's sustainable practices and the happiness of its citizens is not entirely clear. </span>
    While Finland has abundant forests and relies heavily on renewable and nuclear energy, **these factors alone do not fully explain its high happiness rankings.**
    For example, Finland's performance in plastic waste management is fairly average compared to other European countries. It’s likely that other factors, 
    such as income, healthcare, and cultural influences, play a larger role in determining happiness. **More research is needed to understand how environmental 
    efforts might contribute to well-being alongside these other factors.**""", unsafe_allow_html=True)

    st.header("Data Sources")
    st.markdown("""
                1. [World Happiness Report 2023](https://www.kaggle.com/datasets/sazidthe1/global-happiness-scores-and-factors?select=WHR_2023.csv)
                2. [Global Ecological Footprint 2023](https://www.kaggle.com/datasets/jainaru/global-ecological-footprint-2023)
                3. [Global Plastic Waste 2023](https://www.kaggle.com/datasets/prajwaldongre/global-plastic-waste-2023-a-country-wise-analysis)
                4. [Global Data on Sustainable Energy 2020](https://www.kaggle.com/datasets/anshtanwar/global-data-on-sustainable-energy)
    
    """)

if selected == "Eco-anxiety":
    st.title(f"Sustaiability, wellbeing and ecoanxiety: a deeper dive in the topic.")   
    st.markdown("""
        Climate change isn’t just an environmental crisis, it’s an emotional one too. More and more people,
        especially young individuals, are experiencing <span style='background-color: LemonChiffon;'><b>eco-anxiety</b>, a deep sense of worry, fear, and helplessness 
        about the future of our planet.</span> The reality of climate change feels overwhelming, and many struggle 
        with feelings of uncertainty and frustration, particularly when they see a lack of urgent action 
        from governments and institutions.""",
        unsafe_allow_html=True
    )

    # Title
    st.write("### Distribution of health professionals' opinion on climate change impact")

    st.markdown(
        "In 2020, a global survey asked health professionals about the effects of climate change on mental health conditions "
        "like anxiety and depression. The following bar chart summarizes their perspectives:"
    )

    col1, col2 = st.columns(2)

    with col1:
        # Data for the bar chart
        data = pd.DataFrame({
            'Opinions': ['More frequent or severe', 'Less frequent or severe', 'Will remain unchanged', "Don't know"],
            'Percentage': [76.8, 2.2, 13.2, 7.9]
        })

        # Create Altair horizontal bar chart
        chart = alt.Chart(data).mark_bar(color='lightblue').encode(
            y=alt.Y('Opinions', sort=None, title='Opinions', axis=alt.Axis(labelLimit=300)),
            x=alt.X('Percentage', title='Percentage (%)'),
            tooltip=['Opinions', 'Percentage']
        ).properties(
            width=700,
            height=400,
            title=""
        )

        # Display the chart in Streamlit
        st.altair_chart(chart, use_container_width=True)

    with col2:
        st.markdown(
            """
            <div style="margin: 150px 50px;">
            <b>Conclusion:</b>
            In 2020, medical professionals largely agreed that climate change related issues will make people's
            mental conditions more frequent or severe.
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.markdown("LINK TO THE DATA")

    data_path = "share-believe-climate.csv"
    data = pd.read_csv(data_path)

    st.write("### Share of people who believe that climate change is a serious threat to the humanity")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div style="margin: 150px 50px;">
            Lorem ipsum dolor sit amet, consectetur adipiscing elit. Proin mollis a ex sit amet finibus. Aenean pulvinar ipsum venenatis laoreet blandit. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent in malesuada risus, id vulputate nulla. Donec sed ipsum a justo blandit tincidunt. Nullam et convallis diam. Morbi rutrum euismod dui at suscipit. In id dui lacus. In id lacus aliquam, ultrices libero id, volutpat arcu. Mauris in molestie nisi. Aenean volutpat erat ex, eu consectetur tortor commodo vel. Praesent massa nunc, aliquet id cursus eget, laoreet ut neque. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Etiam viverra sem tortor, placerat suscipit felis blandit vel.
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
    # Filter dataset for the most recent year
        latest_year = data['Year'].max()
        data_latest = data[data['Year'] == latest_year]

        # Rename columns for better readability
        data_latest = data_latest.rename(columns={
            'Entity': 'Country',
            'Code': 'Country Code',
            'Believe climate change is a serious threat to humanity': 'Belief (%)'
        })

        # Choropleth map
        fig = px.choropleth(
            data_latest,
            locations="Country Code",
            color="Belief (%)",
            hover_name="Country",
            hover_data={
                "Country Code": False
            },
            color_continuous_scale="Blues",
            labels={"Belief (%)": "% Belief"}
        )

        # Customize hover text to match the desired format with smaller percentage font
        fig.update_traces(
            hovertemplate=
                "<b>%{hovertext}</b><br>" +
                "%{customdata[0]}<br>" +
                "<span style='font-size:16px'><b>%{z:.1f}%</b></span><extra></extra>",
            customdata=data_latest[["Year"]]
        )

        fig.update_geos(
            showcoastlines=False,
            showland=True, landcolor="gray",
            showocean=False
        )

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
            dragmode=False,  # Disable dragging and panning
            margin=dict(t=0, b=0, l=0, r=0)
        )

        st.plotly_chart(fig, use_container_width=True)

    st.markdown("LINK TO THE DATA")

    st.markdown("### Personal revelance")
    st.markdown("""
        Depending on the extent to which we are personally confronted with the effects of climate change, 
        we can assess the importance of measures very differently. Those who experience the impacts first-hand often feel a 
        greater sense of urgency to act. This personal connection can influence how we priorities the issue.

        The graph visually represents the percentage of people in various European countries who perceive 
        climate change as the biggest problem, with higher percentages shown in warmer colors and lower percentages in cooler colors.

        The graphic illustrates the varying levels of concern about climate change across European countries, 
        with a color-coded map and a bar chart showing the level of concern on a scale of 1 to 10.
        """)
    
    col1, col2 = st.columns(2)

    with col1:

        # Streamlit app title
        st.markdown("### Perception of Climate Change as the Biggest Problem in Europe")

        # Updated data from the image
        data = {
            "Belgium": 49, "Bulgaria": 22, "Czech Republic": 27, "Denmark": 74, "Germany": 55,
            "Estonia": 29, "Ireland": 49, "Greece": 44, "Spain": 48, "France": 52,
            "Croatia": 42, "Italy": 45, "Cyprus": 39, "Latvia": 22, "Lithuania": 37,
            "Luxembourg": 57, "Hungary": 33, "Malta": 49, "Netherlands": 66, "Austria": 48,
            "Poland": 28, "Portugal": 43, "Romania": 31, "Slovenia": 42, "Slovakia": 26,
            "Finland": 55, "Sweden": 73
        }

        # Convert data to DataFrame
        df = pd.DataFrame(list(data.items()), columns=["Country", "Percentage"])

        # Country name mapping to match GeoJSON format
        country_name_mapping = {
            "Czech Republic": "Czechia"
        }
        df["Country"] = df["Country"].replace(country_name_mapping)

        # Fetch GeoJSON data
        GEOJSON_URL = "https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json"
        geojson_data = requests.get(GEOJSON_URL).json()

        # Create a folium map with a tileset that shows English names
        m = folium.Map(location=[54.5260, 15.2551], zoom_start=4, tiles="CartoDB Positron")

        # Create a color scale
        colormap = linear.RdYlGn_11.scale(df["Percentage"].min(), df["Percentage"].max())

        # Add choropleth layer to shade entire countries
        choropleth = folium.Choropleth(
            geo_data=geojson_data,
            name="choropleth",
            data=df,
            columns=["Country", "Percentage"],
            key_on="feature.properties.name",
            fill_color="RdYlGn",
            fill_opacity=0.7,
            line_opacity=0.2,
            legend_name="Perception (%)"
        ).add_to(m)

        # Merge data into GeoJSON for better tooltips
        for feature in geojson_data["features"]:
            country_name = feature["properties"]["name"]
            feature["properties"]["Percentage"] = data.get(country_name, "No Data")

        folium.GeoJson(
            geojson_data,
            tooltip=folium.GeoJsonTooltip(
                fields=["name", "Percentage"],
                aliases=["Country: ", "Percentage: "],
                localize=True
            )
        ).add_to(m)

        # Display the map in Streamlit
        st.components.v1.html(m._repr_html_(), height=600)

        # Add a table to show the percentage distribution
        st.subheader("Percentage Distribution by Country")
        st.dataframe(df.sort_values(by="Percentage", ascending=False))

        # Add a bar chart for better visualization
        st.subheader("Bar Chart of Percentage Distribution")
        st.bar_chart(df.set_index("Country"))

    with col2:

        # Streamlit app title
        st.markdown("### Perception of Climate Change in Europe")

        # Updated data
        climate_concern = {
            'Germany': 8, 'France': 7, 'Spain': 6, 'Italy': 7, 'United Kingdom': 6,
            'Poland': 5, 'Romania': 4, 'Netherlands': 7, 'Belgium': 6,
            'Greece': 8, 'Portugal': 7, 'Sweden': 6, 'Hungary': 5,
            'Austria': 6, 'Switzerland': 7, 'Denmark': 7, 'Finland': 6,
            'Norway': 6, 'Ireland': 6, 'Croatia': 5, 'Lithuania': 7, 'Slovakia': 8, 
            'Slovenia': 8, 'Bulgaria': 9, 'Liechtenstein': 5, 'Latvia': 10, 
            'Cyprus': 3, 'Estonia': 10,
        }

        # Convert data to DataFrame
        df = pd.DataFrame(list(climate_concern.items()), columns=["Country", "Concern Level"])

        # Define a slightly lighter color scale
        color_scale = LinearColormap(["lightgreen", "lightyellow", "lightsalmon", "lightcoral"], vmin=min(climate_concern.values()), vmax=max(climate_concern.values()))

        def custom_colormap(value):
            return color_scale(value)

        # Create a folium map with English labels
        m = folium.Map(location=[54.5260, 15.2551], zoom_start=4, tiles="CartoDB Positron")

        # Load GeoJSON data for world country borders
        GEOJSON_URL = "https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json"
        geojson_data = requests.get(GEOJSON_URL).json()

        # Apply custom colors using folium.GeoJson
        def style_function(feature):
            country_name = feature["properties"]["name"]
            concern_value = climate_concern.get(country_name, None)
            if concern_value is not None:
                return {
                    "fillColor": custom_colormap(concern_value),
                    "fillOpacity": 0.7,
                    "color": "black",
                    "weight": 0.5  # Thinner borders
                }
            else:
                return {"fillColor": "#3a3a3a", "fillOpacity": 0.85, "color": "black", "weight": 0.3}  # Shade out other countries

        # Apply tooltips with country name and concern level
        def tooltip_function(feature):
            country_name = feature["properties"]["name"]
            concern_value = climate_concern.get(country_name, None)
            if concern_value is not None:
                return f"<div style='text-align: center;'><b style='font-size:14px;'>{country_name}</b><br><span style='font-size:16px;'>{concern_value}</span></div>"
            return ""

        # Add the colored geojson layer with tooltips
        gj = folium.GeoJson(
            geojson_data,
            name="Climate Concern",
            style_function=style_function,
            tooltip=folium.GeoJsonTooltip(
                fields=["name"],
                aliases=[""],
                labels=False,
                sticky=True,
                localize=True,
                style="background-color: white; color: black; font-family: Arial; font-size: 14px;",
                html=True
            )
        )

        # Attach tooltips to each feature
        for feature in gj.data["features"]:
            country_name = feature["properties"]["name"]
            if country_name in climate_concern:
                feature["properties"]["tooltip"] = tooltip_function(feature)

        gj.add_to(m)

        # Add color bar
        color_scale.caption = "Climate Concern Level (1-10)"
        color_scale.add_to(m)

        # Display the map in Streamlit
        st.components.v1.html(m._repr_html_(), height=600)

        # Add a bar chart for percentage distribution
        st.subheader("Climate Concern Level by Country")
        fig = px.bar(
            df,
            x="Country",
            y="Concern Level",
            labels={"Concern Level": "Concern Level (1-10)", "Country": "Country"},
            title="Climate Concern Level Distribution",
            text="Concern Level",
            color="Concern Level",
            color_continuous_scale=px.colors.sequential.Viridis,
        )
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)