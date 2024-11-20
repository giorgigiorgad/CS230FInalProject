"""
Name: Giorgi Giorgadze
CS230: Section 005
Data: Skyscrapers
URL:
Description: This program provides the data analysis of skyscrapers in the United States, by selecting the city you can see
how many building are there, the year it was done, and more. You can see graph of the tallest buildings and map where the
building are located.
"""

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import altair as alt
import pydeck as pdk

# Load your dataset
df = pd.read_csv('skyscrapers.csv')

# Ensure the dataset has the necessary columns
required_columns = ['location.city', 'statistics.height', 'name', 'location.latitude', 'location.longitude', 'status.completed.year']
if not all(col in df.columns for col in required_columns):
    st.error(f"Dataset must contain the following columns: {', '.join(required_columns)}")
else:
    st.title("Skyscraper Explorer")

    st.sidebar.header("Navigation")

    # Sidebar Filters: Multi-select for cities
    city_list = sorted(df['location.city'].dropna().unique())
    # Ensure default values exist in the options
    default_cities = [city for city in ["Boston", "New York"] if city in city_list]
    selected_cities = st.sidebar.multiselect("Select Cities", city_list, default=default_cities)  # Use valid default cities

    # Filter dataset based on selected cities
    if selected_cities:
        city_data = df[df['location.city'].isin(selected_cities)]
    else:
        city_data = df  # Show all data if no city is selected

    # Navigation in Sidebar
    navigation = st.sidebar.radio(
        "Go to",
        ("Completed Skyscrapers", "Tallest Skyscrapers", "Map of Skyscrapers", "Skyscraper Distribution")
    )

    if navigation == "Completed Skyscrapers":
        st.subheader(f"Completed Skyscrapers in {', '.join(selected_cities) if selected_cities else 'All Cities'}")
        st.dataframe(city_data)


    elif navigation == "Tallest Skyscrapers":

        st.subheader(f"Tallest Skyscrapers in {', '.join(selected_cities) if selected_cities else 'All Cities'}")

        if not city_data.empty:

            # Ensure height column is numeric

            city_data['statistics.height'] = pd.to_numeric(city_data['statistics.height'], errors='coerce')

            city_data = city_data.dropna(subset=['statistics.height'])


            # Function to calculate average height for each city

            def calculate_average_heights(data):

                """

                Calculate the average height of skyscrapers for each selected city.

                :param data: DataFrame containing skyscraper data

                :return: DataFrame with city and their average heights

                """

                avg_heights = data.groupby('location.city')['statistics.height'].mean().reset_index()

                avg_heights.columns = ['City', 'Average Height (m)']

                return avg_heights


            # Calculate average heights for selected cities

            average_heights = calculate_average_heights(city_data)

            # Interactive slider for top skyscrapers

            top_n = st.slider("Select the number of top skyscrapers to display", min_value=1, max_value=len(city_data),
                              value=5)

            top_skyscrapers = city_data.nlargest(top_n, 'statistics.height')

            st.write(
                f"Top {top_n} tallest skyscrapers in {', '.join(selected_cities) if selected_cities else 'All Cities'}:")

            st.dataframe(top_skyscrapers[['name', 'location.city', 'statistics.height']].reset_index(drop=True))

            # Horizontal Bar Chart with Matplotlib

            fig, ax = plt.subplots(figsize=(8, 6))

            ax.barh(top_skyscrapers['name'], top_skyscrapers['statistics.height'], color='green')

            ax.set_xlabel("Height (m)", fontsize=12)

            ax.set_ylabel("Building Name", fontsize=12)

            ax.set_title(
                f"Top {top_n} Tallest Skyscrapers in {', '.join(selected_cities) if selected_cities else 'All Cities'}",
                fontsize=14)

            ax.invert_yaxis()  # To display the tallest building at the top

            st.pyplot(fig)

            # Display the average heights as a separate graph for comparison

            st.write("### Average Heights of Skyscrapers by City")

            fig, ax = plt.subplots(figsize=(8, 6))

            ax.bar(average_heights['City'], average_heights['Average Height (m)'], color='green')

            ax.set_xlabel("City", fontsize=12)

            ax.set_ylabel("Average Height (m)", fontsize=12)

            ax.set_title("Comparison of Average Heights Across Selected Cities", fontsize=14)

            plt.xticks(rotation=45)

            st.pyplot(fig)


        else:

            st.write("No skyscrapers found for the selected cities.")


    elif navigation == "Map of Skyscrapers":
        st.subheader(f"Map of Skyscrapers in {', '.join(selected_cities) if selected_cities else 'All Cities'}")
        if not city_data.empty:
            # Check for latitude/longitude values
            city_data = city_data.dropna(subset=['location.latitude', 'location.longitude'])

            # Advanced Map Visualization with PyDeck
            map_data = city_data[['name', 'location.latitude', 'location.longitude', 'statistics.height']].dropna()
            map_data.rename(columns={'location.latitude': 'lat', 'location.longitude': 'lon'}, inplace=True)

            layer = pdk.Layer(
                "ScatterplotLayer",
                data=map_data,
                get_position='[lon, lat]',
                get_radius=500,
                get_fill_color='[0, 128, 0, 160]',  # Green color
                pickable=True,
            )
            view_state = pdk.ViewState(
                latitude=map_data['lat'].mean(),
                longitude=map_data['lon'].mean(),
                zoom=5,
                pitch=50
            )
            deck = pdk.Deck(
                layers=[layer],
                initial_view_state=view_state,
                tooltip={"text": "{name}\nHeight: {statistics.height} meters"}
            )

            st.pydeck_chart(deck)
        else:
            st.write("No skyscrapers found for the selected cities.")


    elif navigation == "Skyscraper Distribution":
        st.subheader(f"Skyscraper Distribution: {', '.join(selected_cities) if selected_cities else 'All Cities'}")

        if not city_data.empty:
            # Group data by city and count the number of skyscrapers
            distribution_data = city_data['location.city'].value_counts().reset_index()
            distribution_data.columns = ['City', 'Count']

            # Pie Chart with Matplotlib
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.pie(
                distribution_data['Count'],
                labels=distribution_data['City'],
                autopct='%1.2f%%',
                startangle=90,
                colors=plt.cm.tab10.colors  # Use a preset color palette
            )
            ax.set_title(f"Skyscraper Distribution: {', '.join(selected_cities) if selected_cities else 'All Cities'}",
                         fontsize=14)

            st.pyplot(fig)

            # Display the raw data for transparency
            st.write("Skyscraper Counts by City:")
            st.dataframe(distribution_data)
        else:
            st.write("No skyscrapers found for the selected cities.")
