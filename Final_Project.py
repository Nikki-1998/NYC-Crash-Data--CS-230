"""
Name:       Nickarlet Jeffrey
CS230:      Section SN5
Data:       nyc_veh_crash_sample
URL:        Link to your web application online (see extra credit)

Description:

This program will be analyzing the NYC crash data to create:

1. A pie chart which showcases the top ten reasons for accidents occurring a selected NYC borough. The user can choose
the which borough they will like to analyze. This is an exploding pie chart where the slice with the largest percentage
explodes. The user can select the value by which they will like the slice to explode by.

2. A map for the selected borough from above which maps out the accident that occurred in the selected borough

3. A bar chart that shows the percentage of accidents that occurred at a particular time during a particular period of
dates.

"""

import pydeck as pdk
import streamlit as st
import datetime as dt
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import base64


# Styling the streamlit page
main_bg = "main_background.jpg"
main_bg_ext = "jpg"

st.markdown(
    f"""
    <style>
    .reportview-container {{
        background: url(data:image/{main_bg_ext};base64,{base64.b64encode(open(main_bg, "rb").read()).decode()})
    }}

        </style>
        """,
        unsafe_allow_html=True
    )


car_crash = pd.read_csv('nyc_veh_crash_data.csv')

# Dropping unnecessary columns from the dataset
car_crash.drop(['ZIP CODE','LOCATION','VEHICLE 1 TYPE','VEHICLE 2 TYPE','VEHICLE 3 TYPE', 'VEHICLE 4 TYPE'],inplace=True,axis=1)
car_crash.drop(['VEHICLE 5 TYPE','VEHICLE 2 FACTOR','VEHICLE 3 FACTOR','VEHICLE 4 FACTOR','VEHICLE 5 FACTOR'],inplace=True,axis=1)
car_crash.drop(['ON STREET NAME','CROSS STREET NAME','OFF STREET NAME','PERSONS INJURED','PERSONS KILLED','MOTORISTS KILLED'],inplace=True,axis=1)
car_crash.drop(['PEDESTRIANS INJURED','PEDESTRIANS KILLED','CYCLISTS INJURED','CYCLISTS KILLED','MOTORISTS INJURED'],inplace=True,axis=1)


# Converting DATE column to DATETIME object
date = pd.to_datetime(car_crash['DATE'])
car_crash.drop(["DATE"],inplace=True,axis=1)
car_crash["DATE"] = date

def second_item (e):
    return e[1]

st.header("Analysis of Car Crash Data in New York City")

st.subheader("Pie Chart showing the top ten reasons for accidents occurring in a selected borough.  ")

st.write("""
The following Pie Chart and dataframe shows the top ten reasons for accidents occurring in a selected borough. 
        """)

def pie_chart(selected_borough, column, explosion = 0.25):
    plt.clf()
    select_borough = selected_borough.upper()
    df = car_crash[car_crash['BOROUGH'] == select_borough]
    accident_word_list = []
    frequency_word_list = []
    factor_count = df.groupby(column)['DATE'].count()
    factor_dictionary = factor_count.to_dict()
    sorted_dict = sorted(factor_dictionary.items(), key=second_item, reverse = True)
    top_eleven_reasons = sorted_dict[:11]
    for item in top_eleven_reasons:
        accident_word_list.append(item[0])
        frequency_word_list.append(item[1])

    accident_factors = accident_word_list[1:]
    factor_frequency = frequency_word_list[1:]
    explode = (explosion, 0, 0, 0, 0, 0, 0, 0, 0, 0,)
    plt.pie(factor_frequency, labels = accident_factors, explode=explode, autopct="%1.1f%%")
    plt.title("Reasons for Vehicular accidents in NY")
    plt.axis('equal')

    df = pd.DataFrame(sorted_dict, columns=["Reasons for Accidents", "Frequency"])
    st.dataframe(df)
    return plt


def map(selected_borough):
    borough_df = car_crash[car_crash['BOROUGH'] == selected_borough.upper()]
    st.write(borough_df)

    borough_results = borough_df.dropna()

    lat = borough_results["LATITUDE"]
    lon = borough_results["LONGITUDE"]

    borough_results.drop(["LATITUDE", "LONGITUDE"], inplace=True, axis=1)
    borough_results["lat"] = pd.to_numeric(lat)
    borough_results["lon"] = pd.to_numeric(lon)


    view_state = pdk.ViewState(
    latitude = borough_results['lat'].mean(),
    longitude = borough_results['lon'].mean(),
    zoom=12,
    pitch=0.5)

    layer1 = pdk.Layer('ScatterplotLayer',
                  data =borough_results,
                  get_position ='[lon, lat]',
                  get_radius =80,
                  get_color =[100, 50, 105],
                  pickable =True
                  )

    map = pdk.Deck(
    map_style='mapbox://styles/mapbox/satellite-streets-v11',
    initial_view_state=view_state,
    layers=[layer1],
    )
    st.subheader("Map showing the  accidents occurring in a selected borough based on recorded locations")
    st.write("""
    The following map shows the  accidents occurring in a selected borough based on recorded locations. 
        """)
    return map

def barchart(min_date, max_date,time_frame, color):
    plt.clf()
    time_period = []
    time = car_crash['TIME']
    for item in time:
        if len(item) == 4:
            if int(item[0]) >= 7:
                time_period.append("morning")
            elif int(item[0]) < 7:
                time_period.append("night")
        elif len(item) == 5:
            if int(item[:2]) < 12:
                time_period.append("morning")
            elif int(item[:2]) < 18:
                time_period.append("afternoon")
            else:
                time_period.append("evening")

    car_crash["Time_Period"] = time_period
    Date_time_accident = pd.DataFrame(car_crash[["DATE", "TIME", "BOROUGH","Time_Period"]])

    mask = (Date_time_accident['DATE'] > min_date) & (Date_time_accident['DATE'] < max_date)
    date_grouping = Date_time_accident.loc[mask]
    results = date_grouping[date_grouping['Time_Period'] == time_frame]
    borough_count = results.groupby('BOROUGH')['DATE'].count()
    borough_count.plot(kind ='bar', color = color)
    min_title_date = str(min_date)
    max_accident_count = borough_count.max()
    plt.yticks((np.arange(0, max_accident_count, 1)))
    min_title_index = min_title_date[:11]
    max_title_date = str(max_date)
    max_title_index = max_title_date[:11]
    plt.title(f"Accidents that occurred in the {time_frame} during {min_title_index} and {max_title_index} in the Boroughs")
    boroughs = borough_count.index
    plt.xlabel("Boroughs")
    plt.ylabel(f"Accidents that occurred in {time_frame}")
    n_borough = len(boroughs)
    xtiks = np.arange(1, n_borough, n_borough // 4)
    xtiks_labels = [boroughs[i] for i in xtiks]
    plt.xticks(rotation=60)
    st.subheader("""
    Bar Chart showing the frequency of accidents which has occurred between a particular timeframe for a specified number of days
     """)
    st.write("""
    The following Bar Chart and dataframe shows the frequency of accidents which has occurred between a particular
    timeframe (morning/evening/night) for a specified date grouping
        """)
    st.write(borough_count)
    return plt




def main ():
    explode_factor = st.sidebar.number_input("What factor do you want the slice to explode by:", 0.0, 1.5, 0.25)
    New_York_Boroughs = {'Bronx': 1, 'Brooklyn': 2, 'Manhattan': 3, 'Queens': 4, 'Staten Island': 5}
    selected_borough = st.sidebar.radio('Select Borough to view accidents:', list(New_York_Boroughs.keys()))
    output_pie_chart = pie_chart(selected_borough,'VEHICLE 1 FACTOR', explode_factor)
    st.pyplot(output_pie_chart)
    st.write("\n")
    st.write("\n")
    st.pydeck_chart(map(selected_borough))
    st.write("\n")
    st.write("\n")
    min_dates = car_crash.groupby('VEHICLE 1 FACTOR')['DATE'].min()
    min_date = min_dates.head(5)
    min_date_list =[]
    for date in min_date:
        day = str(date)
        min_date_list.append(day[:11])
    start_date = st.sidebar.radio("Select the starting date", min_date_list)
    begin_date = pd.to_datetime(start_date)
    days = st.sidebar.number_input("How many days do you want:", 0, 60, 15)
    end_date = begin_date + dt.timedelta(days=days)

    time_frames = {"morning": 1, "afternoon": 2, "evening": 3, "night": 4}
    requested_time_frame = st.sidebar.selectbox("Time period", list(time_frames.keys()))

    colours = ("yellow", "cyan", "blue", "purple", "orange", "red", "green", "pink", "black")
    selected_color = st.sidebar.selectbox("Select a color for the chart", colours)
    st.write("\n")
    st.write("\n")
    output_bar_chart = barchart(begin_date, end_date, requested_time_frame, selected_color)
    st.pyplot(output_bar_chart)

main()

