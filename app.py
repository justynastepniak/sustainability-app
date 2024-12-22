import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
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

df = pd.read_csv('global_data_new.csv')

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
        options=["Home", "Global Overview", "Case Study 1", "Case Study 2"],  # required
        default_index=0,  # optional
    )

if selected == "Home":
    st.title(f"Title {selected}")

if selected == "Global Overview":
    st.title(f"{selected} - are residents of sustainable countries happier?")
    st.text("Lorem ipsum dolor sit amet, consectetur adipiscing elit. In convallis risus viverra ultricies ullamcorper. Quisque risus velit, dapibus sed ipsum a, placerat tincidunt nulla. Sed elit quam, volutpat eu vulputate id, sodales vel nisl. ")
    st.header("Global Happiness Score in 2023")
    st.text("What is Happiness Score (short)")
    display_map(df, 'happiness_score', 'YlGn', 1.86, 7.8)
    st.header("Global SDGI index in 2023")
    st.text("What is SDGI index")
    display_map(df, 'sdgi', 'YlGn', 40, 86.5)
    st.header("Conclusion of those maps")
    st.text("Copy text that correlation =/= causation and that poorer countries can't afford 'sustainable' practices. Lorem ipsum dolor sit amet, consectetur adipiscing elit. In convallis risus viverra ultricies ullamcorper. Quisque risus velit, dapibus sed ipsum a, placerat tincidunt nulla. Sed elit quam, volutpat eu vulputate id, sodales vel nisl. ")
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
    st.text("Copy text that Happiness corelates both with wealth and development of the country and that sustainability itself cannot be said to be a cause. Lorem ipsum dolor sit amet, consectetur adipiscing elit. In convallis risus viverra ultricies ullamcorper. Quisque risus velit, dapibus sed ipsum a, placerat tincidunt nulla. Sed elit quam, volutpat eu vulputate id, sodales vel nisl. ")
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
    st.text("Copy text Lorem ipsum dolor sit amet, consectetur adipiscing elit. In convallis risus viverra ultricies ullamcorper. Quisque risus velit, dapibus sed ipsum a, placerat tincidunt nulla. Sed elit quam, volutpat eu vulputate id, sodales vel nisl. ")
    st.header("Conclusion")
    st.text("Copy text that Happiness corelates both with wealth and development of the country and that sustainability itself cannot be said to be a cause. Lorem ipsum dolor sit amet, consectetur adipiscing elit. In convallis risus viverra ultricies ullamcorper. Quisque risus velit, dapibus sed ipsum a, placerat tincidunt nulla. Sed elit quam, volutpat eu vulputate id, sodales vel nisl. ")
    
if selected == "Case Study 1":
    st.title(f"Title {selected}")
    """CASE STUDY 1 CODE"""

if selected == "Case Study 2":
    st.title(f"Title {selected}")
    """CASE STUDY 2 CODE"""