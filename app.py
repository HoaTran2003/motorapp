# -*- coding: utf-8 -*-
"""
Created on Tue May 14 15:56:27 2024

@author: vanho
"""

import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px


# Title and Introduction
st.title("Motor Collision NYC Data Analysis")
st.markdown("""
### Welcome to the NYC Motor Collision Analysis Dashboard
Every year, thousands of motor vehicle collisions occur on the bustling streets of New York City, impacting the lives of residents, commuters, and visitors. Understanding these collisions' patterns can help city planners, policymakers, and citizens make informed decisions to improve safety and reduce accident rates. This dashboard leverages real data to shed light on the critical aspects of motor vehicle collisions in NYC, providing a visual and interactive way to explore this vital issue.
""")

# Sidebar for filters
st.sidebar.title("Filter Options")
st.sidebar.markdown("Use these filters to refine your analysis")

# Load Data
data_url = r"C:\Users\vanho\Desktop\ML\Motor\data.csv"

@st.cache_data(persist=True)
def load_data(nrows):
    # Function used to clean and load the dataset
    try:
        data = pd.read_csv(data_url, nrows=nrows)
        data['CRASH_DATE_CRASH_TIME'] = pd.to_datetime(data['CRASH_DATE'] + ' ' + data['CRASH_TIME'])
        data.dropna(subset=['LATITUDE', 'LONGITUDE'], inplace=True)
        data.rename(str.lower, axis='columns', inplace=True)
        data.rename(columns={'crash_date_crash_time': 'date/time'}, inplace=True)
        return data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

data = load_data(100000)

# Filters for data exploration
st.sidebar.header("Filter Data")


# Map Data Viz: Most Injured People
st.header("Where are the most people injured in NYC?")
st.markdown("""
To understand the spatial distribution of collisions, we start by identifying locations where the highest number of people are injured. This can help identify hotspots for accidents and prioritize safety measures.
""")
injured_people = st.sidebar.slider("Number of people injured in vehicle collision", 0, 19)
st.map(data.query("injured_persons >= @injured_people")[["latitude", "longitude"]].dropna(how="any"))

# Interactive Table: How Many Collisions?
st.header("How many collisions occur during a given time of day?")
st.markdown("""
Time of day plays a significant role in the frequency of motor vehicle collisions. By examining collisions at different hours, we can identify patterns and times with higher risks.
""")
hour = st.sidebar.slider("Hour to look at", 0, 23)
original_data = data
data = data[data['date/time'].dt.hour == hour]

# 3D Interactive Map
st.markdown(f"### Vehicle collisions between {hour}:00 and {(hour+1) % 24}:00")
midpoint = (np.average(data['latitude']), np.average(data['longitude']))

st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 11,
        "pitch": 50,
    },
    layers=[
        pdk.Layer(
            "HexagonLayer",
            data=data[['date/time', 'latitude', 'longitude']],
            get_position=['longitude', 'latitude'],
            radius=100,
            extruded=True,
            pickable=True,
            elevation_scale=4,
            elevation_range=[0, 1000],
        )
    ]
))

# Bar Charts and Histograms
st.subheader(f"Breakdown by minute between {hour}:00 and {(hour + 1) % 24}:00")
filtered = data[
    (data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour < (hour + 1))
]
hist = np.histogram(filtered['date/time'].dt.minute, bins=60, range=(0, 60))[0]
chart_data = pd.DataFrame({"minute": range(60), "crashes": hist})
fig = px.bar(chart_data, x='minute', y='crashes', hover_data=['minute', 'crashes'], height=400)
st.write(fig)

# Top 5 Dangerous Streets by Affected Class
st.header("Top 5 dangerous streets by affected class")
st.markdown("""
Identifying the most dangerous streets for different groups (pedestrians, cyclists, motorists) helps target interventions where they are most needed.
""")
select = st.selectbox('Affected class', ['Pedestrians', 'Cyclists', 'Motorists'])

if select == 'Pedestrians':
    st.write(original_data.query("injured_pedestrians >= 1")[["on_street_name", "injured_pedestrians"]]
             .sort_values(by=['injured_pedestrians'], ascending=False).dropna(how="any")[:5])

elif select == 'Cyclists':
    st.write(original_data.query("injured_cyclists >= 1")[["on_street_name", "injured_cyclists"]]
             .sort_values(by=['injured_cyclists'], ascending=False).dropna(how="any")[:5])

else:
    st.write(original_data.query("injured_motorists >= 1")[["on_street_name", "injured_motorists"]]
             .sort_values(by=['injured_motorists'], ascending=False).dropna(how="any")[:5])

# Time series analysis
st.header("Collision Trends Over Time")
st.markdown("""
Understanding trends over time is crucial for evaluating the effectiveness of safety measures and identifying periods with higher collision rates.
""")
time_series_data = original_data.set_index('date/time').resample('M').size().reset_index(name='collisions')
fig = px.line(time_series_data, x='date/time', y='collisions', title='Monthly Collision Trends')
st.plotly_chart(fig)

# Checkbox to display raw data
if st.checkbox("Show Raw Data", False): 
    st.subheader('Raw Data')
    st.write(data)
