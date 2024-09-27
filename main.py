import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import mysql.connector
from datetime import datetime, timedelta
from sqlalchemy import create_engine
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import schedule
import time
import threading
import plotly.io as pio
import pymysql
from io import BytesIO
import base64
from PIL import Image
import io
from plotly.subplots import make_subplots

# Set page layout to wide and title
st.set_page_config(
    page_title="Data Visualization of IAQ Monitors of EDS People",
    page_icon="",
    layout='wide',
)

st.markdown("""
    <h1 style='text-align: center; font-size: 34px; background: linear-gradient(90deg, green, green, green, green, green, green, green);
    -webkit-background-clip: text;
    color: transparent;'>
    Data Visualization of IAQ Monitors of EDS People</h1>
    """, unsafe_allow_html=True)

st.markdown(
    """
    <style>
    /* Your updated CSS here */
    .stApp [class*="stIcon"] {
        display: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

button_style = """
    <style>
        .stButton>button {
            box-shadow: 1px 1px 1px rgba(0, 0, 0, 0.8);
        }
    </style>
"""

st.markdown("""
        <style>
        .stButton button {
            height: 30px;
            width: 166px;
        }
        </style>
    """, unsafe_allow_html=True)

# Initialize session state for script_choice if it does not exist
if 'script_choice' not in st.session_state:
    st.session_state.script_choice = "visual"  # Set default to "about"

# Set the default selected date to one day before the current date
default_date = datetime.now() - timedelta(days=1)

if st.button('Analytics'):
    st.session_state.script_choice = "visual"

#Based on the user selection, display appropriate input fields and run the script
if st.session_state.script_choice == "visual":
    host = "139.59.34.149"
    user = "neemdb"
    password = "(#&pxJ&p7JvhA7<B"
    database = "cabh_iaq_db"

    # Input fields for device IDs and date range
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_date = st.date_input("Select Date", value=default_date)
    with col2:
        time_interval = st.selectbox("⏰ Select Time Interval", ['1min', '15min', 'hour'], index=0)
    with col3:
        people = st.selectbox("Select People", ['Gurneet', 'Piyush', 'Sheetal', 'Lakshmi', 'Mariyam', 'Abhishek', 'Surender', 'Robin', 'Hines', 'EDS D Block', 'Nidhi', 'Manpreet', 'TT', 'Hisham'], index=0)
    
    # Initialize device IDs based on the selected person
    if people == 'Gurneet':
        id1 = '1203240077'  # Gurneet Mannat Room
        id2 = '1203240076'  # Gurneet Prabhash Room
    elif people == 'Piyush':
        id1 = '1201240079'  # Piyush Bedroom
        id2 = '1201240085'  # Piyush Living Room
    elif people == 'Sheetal':
        id1 = '1203240083'  # Sheetal Living Room
        id2 = None          # Add more IDs if necessary
    elif people == 'Lakshmi':
        id1 = '1201240072'  # Lakshmi Living Room
        id2 = '1201240077'  # Lakshmi Kitchen
    elif people == 'Mariyam':
        id1 = '1202240027'  # Mariyam Bedroom 1
        id2 = '1202240011'  # Mariyam Living Room
    elif people == 'Abhishek':
        id1 = '1201240074'  # Abhishek Living Room
        id2 = '1203240080'  # Abhishek Bedroom
    elif people == 'Surender':
        id1 = '1212230160'  # Surender Bedroom
        id2 = '1201240076'  # Surender Living Room
    elif people == 'Robin':
        id1 = '1202240009'  # Robin Bedroom
        id2 = '1202240008'  # Robin Living Room
    elif people == 'Hines':
        id1 = '1201240075'  # Hines Office 1
        id2 = '1201240078'  # Hines Office 2
    elif people == 'EDS D Block':
        id1 = '1202240025'
        id2 = '1202240026'
    elif people == 'Hisham':
        id1 = '1203240076'
        id2 = '1203240078'
    elif people == 'TT':
        id1 = '1201240073'
        id2 = None
    elif people == 'Nidhi': # Bedroom
        id1 = '1203240073'
        id2 = None
    elif people == 'Manpreet': # Drawing
        id1 = '1203240072'
        id2 = None
        
    # Convert Streamlit date input to string format for SQL query
    start_date_str = selected_date.strftime('%Y-%m-%d')  # Correct this to use selected_date
    end_date_str = selected_date.strftime('%Y-%m-%d')  # No change needed if only one day is selected

    connection_string = f"mysql+pymysql://{user}:{password}@{host}/{database}"
    engine = create_engine(connection_string)

    # Determine the table name based on the selected interval for Indoor data
    if time_interval == '1min':
        table_name = "reading_db"
    elif time_interval == '15min':
        table_name = "reading_15min"
    elif time_interval == 'hour':
        table_name = "reading_hour"

    # SQL query to fetch indoor data for the specified deviceID and date range
    query_indoor = f"""  
        SELECT * FROM {table_name}
        WHERE DATE(datetime) BETWEEN '{start_date_str}' AND '{end_date_str}';
    """

    # Fetch data from the database into DataFrames
    df = pd.read_sql(query_indoor, engine)

    # Close the connection
    # connection.close()
    engine.dispose()

    if df.empty:
        st.warning("No data available for the selected date and time interval.")
    else:
        # Proceed with visualizing data
        try:    
            if time_interval == "1min":
                # Ensure 'deviceID' column is treated as string and remove any leading/trailing spaces
                df['deviceID'] = df['deviceID'].astype(str).str.strip()
                
                # Defining different rooms' data
                Gurneet_Mannat_Room = df[df['deviceID'] == id1].copy()
                Gurneet_Prabhash_Room = df[df['deviceID'] == id2].copy() if id2 else None

                # Correcting datetime formats
                Gurneet_Mannat_Room['datetime'] = pd.to_datetime(Gurneet_Mannat_Room['datetime'], format='%Y-%m-%d %H:%M')
                Gurneet_Prabhash_Room['datetime'] = pd.to_datetime(Gurneet_Prabhash_Room['datetime'], format='%Y-%m-%d %H:%M')

                # Set 'datetime' as the DataFrame index
                Gurneet_Mannat_Room.set_index('datetime', inplace=True)
                Gurneet_Prabhash_Room.set_index('datetime', inplace=True)

                # Sort the index for each dataframe
                Gurneet_Mannat_Room = Gurneet_Mannat_Room.sort_index()
                Gurneet_Prabhash_Room = Gurneet_Prabhash_Room.sort_index()

                # Convert selected date to datetime and define the time range for filtering
                start_time = pd.to_datetime(selected_date).strftime('%Y-%m-%d') + ' 00:00:00'
                end_time = pd.to_datetime(selected_date).strftime('%Y-%m-%d') + ' 23:59:00'

                # Filter each dataframe to get the values for the 24-hour period
                gurneet_mannat_pm25 = Gurneet_Mannat_Room.loc[start_time:end_time, 'pm25']
                gurneet_prabhash_pm25 = Gurneet_Prabhash_Room.loc[start_time:end_time, 'pm25']

                gurneet_mannat_pm10 = Gurneet_Mannat_Room.loc[start_time:end_time, 'pm10']
                gurneet_prabhash_pm10 = Gurneet_Prabhash_Room.loc[start_time:end_time, 'pm10']

                gurneet_mannat_voc = Gurneet_Mannat_Room.loc[start_time:end_time, 'voc']
                gurneet_prabhash_voc = Gurneet_Prabhash_Room.loc[start_time:end_time, 'voc']

                gurneet_mannat_co2 = Gurneet_Mannat_Room.loc[start_time:end_time, 'co2']
                gurneet_prabhash_co2 = Gurneet_Prabhash_Room.loc[start_time:end_time, 'co2']

                # Create figures
                fig1, fig2, fig3, fig4 = go.Figure(), go.Figure(), go.Figure(), go.Figure()

                # Add traces for each dataframe with specified colors
                if people == 'Gurneet':
                    fig1.add_trace(go.Scatter(x=gurneet_mannat_pm25.index, y=gurneet_mannat_pm25, mode='lines', name='Mannat Room', line=dict(color='blue')))
                    fig1.add_trace(go.Scatter(x=gurneet_prabhash_pm25.index, y=gurneet_prabhash_pm25, mode='lines', name='Prabhash Room', line=dict(color='violet')))

                    fig2.add_trace(go.Scatter(x=gurneet_mannat_pm10.index, y=gurneet_mannat_pm10, mode='lines', name='Mannat Room', line=dict(color='blue')))
                    fig2.add_trace(go.Scatter(x=gurneet_prabhash_pm10.index, y=gurneet_prabhash_pm10, mode='lines', name='Prabhash Room PM10', line=dict(color='violet')))

                    fig3.add_trace(go.Scatter(x=gurneet_mannat_voc.index, y=gurneet_mannat_voc, mode='lines', name='Mannat Room', line=dict(color='blue')))
                    fig3.add_trace(go.Scatter(x=gurneet_prabhash_voc.index, y=gurneet_prabhash_voc, mode='lines', name='Prabhash Room', line=dict(color='violet')))

                    fig4.add_trace(go.Scatter(x=gurneet_mannat_co2.index, y=gurneet_mannat_co2, mode='lines', name='Mannat Room', line=dict(color='blue')))
                    fig4.add_trace(go.Scatter(x=gurneet_prabhash_co2.index, y=gurneet_prabhash_co2, mode='lines', name='Prabhash Room', line=dict(color='violet')))

                elif people == "Piyush":
                    fig1.add_trace(go.Scatter(x=gurneet_mannat_pm25.index, y=gurneet_mannat_pm25, mode='lines', name='Bedroom', line=dict(color='blue')))
                    fig1.add_trace(go.Scatter(x=gurneet_prabhash_pm25.index, y=gurneet_prabhash_pm25, mode='lines', name='Living', line=dict(color='violet')))

                    fig2.add_trace(go.Scatter(x=gurneet_mannat_pm10.index, y=gurneet_mannat_pm10, mode='lines', name='Bedroom', line=dict(color='blue')))
                    fig2.add_trace(go.Scatter(x=gurneet_prabhash_pm10.index, y=gurneet_prabhash_pm10, mode='lines', name='Living', line=dict(color='violet')))

                    fig3.add_trace(go.Scatter(x=gurneet_mannat_voc.index, y=gurneet_mannat_voc, mode='lines', name='Bedroom', line=dict(color='blue')))
                    fig3.add_trace(go.Scatter(x=gurneet_prabhash_voc.index, y=gurneet_prabhash_voc, mode='lines', name='Living', line=dict(color='violet')))

                    fig4.add_trace(go.Scatter(x=gurneet_mannat_co2.index, y=gurneet_mannat_co2, mode='lines', name='Bedroom', line=dict(color='blue')))
                    fig4.add_trace(go.Scatter(x=gurneet_prabhash_co2.index, y=gurneet_prabhash_co2, mode='lines', name='Living', line=dict(color='violet')))

                elif people == "Robin":
                    fig1.add_trace(go.Scatter(x=gurneet_mannat_pm25.index, y=gurneet_mannat_pm25, mode='lines', name='Bedroom', line=dict(color='blue')))
                    fig1.add_trace(go.Scatter(x=gurneet_prabhash_pm25.index, y=gurneet_prabhash_pm25, mode='lines', name='Living', line=dict(color='violet')))

                    fig2.add_trace(go.Scatter(x=gurneet_mannat_pm10.index, y=gurneet_mannat_pm10, mode='lines', name='Bedroom', line=dict(color='blue')))
                    fig2.add_trace(go.Scatter(x=gurneet_prabhash_pm10.index, y=gurneet_prabhash_pm10, mode='lines', name='Living', line=dict(color='violet')))

                    fig3.add_trace(go.Scatter(x=gurneet_mannat_voc.index, y=gurneet_mannat_voc, mode='lines', name='Bedroom', line=dict(color='blue')))
                    fig3.add_trace(go.Scatter(x=gurneet_prabhash_voc.index, y=gurneet_prabhash_voc, mode='lines', name='Living', line=dict(color='violet')))

                    fig4.add_trace(go.Scatter(x=gurneet_mannat_co2.index, y=gurneet_mannat_co2, mode='lines', name='Bedroom', line=dict(color='blue')))
                    fig4.add_trace(go.Scatter(x=gurneet_prabhash_co2.index, y=gurneet_prabhash_co2, mode='lines', name='Living', line=dict(color='violet')))

                elif people == "Surender":
                    fig1.add_trace(go.Scatter(x=gurneet_mannat_pm25.index, y=gurneet_mannat_pm25, mode='lines', name='Bedroom', line=dict(color='blue')))
                    fig1.add_trace(go.Scatter(x=gurneet_prabhash_pm25.index, y=gurneet_prabhash_pm25, mode='lines', name='Living', line=dict(color='violet')))

                    fig2.add_trace(go.Scatter(x=gurneet_mannat_pm10.index, y=gurneet_mannat_pm10, mode='lines', name='Bedroom', line=dict(color='blue')))
                    fig2.add_trace(go.Scatter(x=gurneet_prabhash_pm10.index, y=gurneet_prabhash_pm10, mode='lines', name='Living', line=dict(color='violet')))

                    fig3.add_trace(go.Scatter(x=gurneet_mannat_voc.index, y=gurneet_mannat_voc, mode='lines', name='Bedroom', line=dict(color='blue')))
                    fig3.add_trace(go.Scatter(x=gurneet_prabhash_voc.index, y=gurneet_prabhash_voc, mode='lines', name='Living', line=dict(color='violet')))

                    fig4.add_trace(go.Scatter(x=gurneet_mannat_co2.index, y=gurneet_mannat_co2, mode='lines', name='Bedroom', line=dict(color='blue')))
                    fig4.add_trace(go.Scatter(x=gurneet_prabhash_co2.index, y=gurneet_prabhash_co2, mode='lines', name='Living', line=dict(color='violet')))

                elif people == "EDS D Block":
                    fig1.add_trace(go.Scatter(x=gurneet_mannat_pm25.index, y=gurneet_mannat_pm25, mode='lines', name='EDS Out', line=dict(color='blue')))
                    fig1.add_trace(go.Scatter(x=gurneet_prabhash_pm25.index, y=gurneet_prabhash_pm25, mode='lines', name='Conference', line=dict(color='violet')))

                    fig2.add_trace(go.Scatter(x=gurneet_mannat_pm10.index, y=gurneet_mannat_pm10, mode='lines', name='EDS Out', line=dict(color='blue')))
                    fig2.add_trace(go.Scatter(x=gurneet_prabhash_pm10.index, y=gurneet_prabhash_pm10, mode='lines', name='Conference', line=dict(color='violet')))

                    fig3.add_trace(go.Scatter(x=gurneet_mannat_voc.index, y=gurneet_mannat_voc, mode='lines', name='EDS Out', line=dict(color='blue')))
                    fig3.add_trace(go.Scatter(x=gurneet_prabhash_voc.index, y=gurneet_prabhash_voc, mode='lines', name='Conference', line=dict(color='violet')))

                    fig4.add_trace(go.Scatter(x=gurneet_mannat_co2.index, y=gurneet_mannat_co2, mode='lines', name='EDS Out', line=dict(color='blue')))
                    fig4.add_trace(go.Scatter(x=gurneet_prabhash_co2.index, y=gurneet_prabhash_co2, mode='lines', name='Conference', line=dict(color='violet')))

                elif people == "Piyush":
                    fig1.add_trace(go.Scatter(x=gurneet_prabhash_pm25.index, y=gurneet_prabhash_pm25, mode='lines', name='Living', line=dict(color='red')))
                    fig1.add_trace(go.Scatter(x=gurneet_mannat_pm25.index, y=gurneet_mannat_pm25, mode='lines', name='Bedroom', line=dict(color='blue')))
                    
                    fig2.add_trace(go.Scatter(x=gurneet_prabhash_pm10.index, y=gurneet_prabhash_pm10, mode='lines', name='Living', line=dict(color='red')))
                    fig2.add_trace(go.Scatter(x=gurneet_mannat_pm10.index, y=gurneet_mannat_pm10, mode='lines', name='Bedroom', line=dict(color='blue')))
                    
                    fig3.add_trace(go.Scatter(x=gurneet_prabhash_voc.index, y=gurneet_prabhash_voc, mode='lines', name='Living', line=dict(color='red')))
                    fig3.add_trace(go.Scatter(x=gurneet_mannat_voc.index, y=gurneet_mannat_voc, mode='lines', name='Bedroom', line=dict(color='blue')))
            
                    fig4.add_trace(go.Scatter(x=gurneet_prabhash_co2.index, y=gurneet_prabhash_co2, mode='lines', name='Living', line=dict(color='red')))
                    fig4.add_trace(go.Scatter(x=gurneet_mannat_co2.index, y=gurneet_mannat_co2, mode='lines', name='Bedroom', line=dict(color='blue')))
            
                elif people == "Lakshmi":
                    fig1.add_trace(go.Scatter(x=gurneet_mannat_pm25.index, y=gurneet_mannat_pm25, mode='lines', name='Living', line=dict(color='blue')))
                    fig1.add_trace(go.Scatter(x=gurneet_prabhash_pm25.index, y=gurneet_prabhash_pm25, mode='lines', name='Kitchen', line=dict(color='violet')))

                    fig2.add_trace(go.Scatter(x=gurneet_mannat_pm10.index, y=gurneet_mannat_pm10, mode='lines', name='Living', line=dict(color='blue')))
                    fig2.add_trace(go.Scatter(x=gurneet_prabhash_pm10.index, y=gurneet_prabhash_pm10, mode='lines', name='Kitchen', line=dict(color='violet')))

                    fig3.add_trace(go.Scatter(x=gurneet_mannat_voc.index, y=gurneet_mannat_voc, mode='lines', name='Living', line=dict(color='blue')))
                    fig3.add_trace(go.Scatter(x=gurneet_prabhash_voc.index, y=gurneet_prabhash_voc, mode='lines', name='Kitchen', line=dict(color='violet')))

                    fig4.add_trace(go.Scatter(x=gurneet_mannat_co2.index, y=gurneet_mannat_co2, mode='lines', name='Living', line=dict(color='blue')))
                    fig4.add_trace(go.Scatter(x=gurneet_prabhash_co2.index, y=gurneet_prabhash_co2, mode='lines', name='Kitchen', line=dict(color='violet')))

                elif people == "Manpreet":
                    fig1.add_trace(go.Scatter(x=gurneet_mannat_pm25.index, y=gurneet_mannat_pm25, mode='lines', name='Drawing', line=dict(color='blue')))
                    # fig1.add_trace(go.Scatter(x=gurneet_prabhash_pm25.index, y=gurneet_prabhash_pm25, mode='lines', name='Kitchen', line=dict(color='violet')))

                    fig2.add_trace(go.Scatter(x=gurneet_mannat_pm10.index, y=gurneet_mannat_pm10, mode='lines', name='Drawing', line=dict(color='blue')))
                    # fig2.add_trace(go.Scatter(x=gurneet_prabhash_pm10.index, y=gurneet_prabhash_pm10, mode='lines', name='Kitchen', line=dict(color='violet')))

                    fig3.add_trace(go.Scatter(x=gurneet_mannat_voc.index, y=gurneet_mannat_voc, mode='lines', name='Drawing', line=dict(color='blue')))
                    # fig3.add_trace(go.Scatter(x=gurneet_prabhash_voc.index, y=gurneet_prabhash_voc, mode='lines', name='Kitchen', line=dict(color='violet')))

                    fig4.add_trace(go.Scatter(x=gurneet_mannat_co2.index, y=gurneet_mannat_co2, mode='lines', name='Drawing', line=dict(color='blue')))
                    # fig4.add_trace(go.Scatter(x=gurneet_prabhash_co2.index, y=gurneet_prabhash_co2, mode='lines', name='Kitchen', line=dict(color='violet')))

                elif people == "Nidhi":
                    fig1.add_trace(go.Scatter(x=gurneet_mannat_pm25.index, y=gurneet_mannat_pm25, mode='lines', name='Bedroom', line=dict(color='blue')))
                    # fig1.add_trace(go.Scatter(x=gurneet_prabhash_pm25.index, y=gurneet_prabhash_pm25, mode='lines', name='Kitchen', line=dict(color='violet')))

                    fig2.add_trace(go.Scatter(x=gurneet_mannat_pm10.index, y=gurneet_mannat_pm10, mode='lines', name='Bedroom', line=dict(color='blue')))
                    # fig2.add_trace(go.Scatter(x=gurneet_prabhash_pm10.index, y=gurneet_prabhash_pm10, mode='lines', name='Kitchen', line=dict(color='violet')))

                    fig3.add_trace(go.Scatter(x=gurneet_mannat_voc.index, y=gurneet_mannat_voc, mode='lines', name='Bedroom', line=dict(color='blue')))
                    # fig3.add_trace(go.Scatter(x=gurneet_prabhash_voc.index, y=gurneet_prabhash_voc, mode='lines', name='Kitchen', line=dict(color='violet')))

                    fig4.add_trace(go.Scatter(x=gurneet_mannat_co2.index, y=gurneet_mannat_co2, mode='lines', name='Bedroom', line=dict(color='blue')))
                    # fig4.add_trace(go.Scatter(x=gurneet_prabhash_co2.index, y=gurneet_prabhash_co2, mode='lines', name='Kitchen', line=dict(color='violet')))

                elif people == "TT": # Home
                    fig1.add_trace(go.Scatter(x=gurneet_mannat_pm25.index, y=gurneet_mannat_pm25, mode='lines', name='Home', line=dict(color='blue')))
                    # fig1.add_trace(go.Scatter(x=gurneet_prabhash_pm25.index, y=gurneet_prabhash_pm25, mode='lines', name='Kitchen', line=dict(color='violet')))

                    fig2.add_trace(go.Scatter(x=gurneet_mannat_pm10.index, y=gurneet_mannat_pm10, mode='lines', name='Home', line=dict(color='blue')))
                    # fig2.add_trace(go.Scatter(x=gurneet_prabhash_pm10.index, y=gurneet_prabhash_pm10, mode='lines', name='Kitchen', line=dict(color='violet')))

                    fig3.add_trace(go.Scatter(x=gurneet_mannat_voc.index, y=gurneet_mannat_voc, mode='lines', name='Home', line=dict(color='blue')))
                    # fig3.add_trace(go.Scatter(x=gurneet_prabhash_voc.index, y=gurneet_prabhash_voc, mode='lines', name='Kitchen', line=dict(color='violet')))

                    fig4.add_trace(go.Scatter(x=gurneet_mannat_co2.index, y=gurneet_mannat_co2, mode='lines', name='Home', line=dict(color='blue')))
                    # fig4.add_trace(go.Scatter(x=gurneet_prabhash_co2.index, y=gurneet_prabhash_co2, mode='lines', name='Kitchen', line=dict(color='violet')))

                elif people == "Sheetal": # Home
                    fig1.add_trace(go.Scatter(x=gurneet_mannat_pm25.index, y=gurneet_mannat_pm25, mode='lines', name='Living', line=dict(color='blue')))
                    # fig1.add_trace(go.Scatter(x=gurneet_prabhash_pm25.index, y=gurneet_prabhash_pm25, mode='lines', name='Kitchen', line=dict(color='violet')))

                    fig2.add_trace(go.Scatter(x=gurneet_mannat_pm10.index, y=gurneet_mannat_pm10, mode='lines', name='Living', line=dict(color='blue')))
                    # fig2.add_trace(go.Scatter(x=gurneet_prabhash_pm10.index, y=gurneet_prabhash_pm10, mode='lines', name='Kitchen', line=dict(color='violet')))

                    fig3.add_trace(go.Scatter(x=gurneet_mannat_voc.index, y=gurneet_mannat_voc, mode='lines', name='Living', line=dict(color='blue')))
                    # fig3.add_trace(go.Scatter(x=gurneet_prabhash_voc.index, y=gurneet_prabhash_voc, mode='lines', name='Kitchen', line=dict(color='violet')))

                    fig4.add_trace(go.Scatter(x=gurneet_mannat_co2.index, y=gurneet_mannat_co2, mode='lines', name='Living', line=dict(color='blue')))
                    # fig4.add_trace(go.Scatter(x=gurneet_prabhash_co2.index, y=gurneet_prabhash_co2, mode='lines', name='Kitchen', line=dict(color='violet')))

                elif people == "Hisham":
                    fig1.add_trace(go.Scatter(x=gurneet_prabhash_pm25.index, y=gurneet_prabhash_pm25, mode='lines', name='Living', line=dict(color='red')))
                    fig1.add_trace(go.Scatter(x=gurneet_mannat_pm25.index, y=gurneet_mannat_pm25, mode='lines', name='Bedroom', line=dict(color='blue')))
                    
                    fig2.add_trace(go.Scatter(x=gurneet_prabhash_pm10.index, y=gurneet_prabhash_pm10, mode='lines', name='Living', line=dict(color='red')))
                    fig2.add_trace(go.Scatter(x=gurneet_mannat_pm10.index, y=gurneet_mannat_pm10, mode='lines', name='Bedroom', line=dict(color='blue')))
                    
                    fig3.add_trace(go.Scatter(x=gurneet_prabhash_voc.index, y=gurneet_prabhash_voc, mode='lines', name='Living', line=dict(color='red')))
                    fig3.add_trace(go.Scatter(x=gurneet_mannat_voc.index, y=gurneet_mannat_voc, mode='lines', name='Bedroom', line=dict(color='blue')))
            
                    fig4.add_trace(go.Scatter(x=gurneet_prabhash_co2.index, y=gurneet_prabhash_co2, mode='lines', name='Living', line=dict(color='red')))
                    fig4.add_trace(go.Scatter(x=gurneet_mannat_co2.index, y=gurneet_mannat_co2, mode='lines', name='Bedroom', line=dict(color='blue')))
            
                elif people == "Mariyam":
                    fig1.add_trace(go.Scatter(x=gurneet_prabhash_pm25.index, y=gurneet_prabhash_pm25, mode='lines', name='BR1', line=dict(color='red')))
                    fig1.add_trace(go.Scatter(x=gurneet_mannat_pm25.index, y=gurneet_mannat_pm25, mode='lines', name='LR1', line=dict(color='blue')))
                    
                    fig2.add_trace(go.Scatter(x=gurneet_prabhash_pm10.index, y=gurneet_prabhash_pm10, mode='lines', name='BR1', line=dict(color='red')))
                    fig2.add_trace(go.Scatter(x=gurneet_mannat_pm10.index, y=gurneet_mannat_pm10, mode='lines', name='LR1', line=dict(color='blue')))
                    
                    fig3.add_trace(go.Scatter(x=gurneet_prabhash_voc.index, y=gurneet_prabhash_voc, mode='lines', name='BR1', line=dict(color='red')))
                    fig3.add_trace(go.Scatter(x=gurneet_mannat_voc.index, y=gurneet_mannat_voc, mode='lines', name='LR1', line=dict(color='blue')))
            
                    fig4.add_trace(go.Scatter(x=gurneet_prabhash_co2.index, y=gurneet_prabhash_co2, mode='lines', name='BR1', line=dict(color='red')))
                    fig4.add_trace(go.Scatter(x=gurneet_mannat_co2.index, y=gurneet_mannat_co2, mode='lines', name='LR1', line=dict(color='blue')))
            
                # Add horizontal dotted threshold lines
                threshold_lines = [(25, 'PM2.5', fig1), (50, 'PM10', fig2), (500, 'VOC', fig3), (1000, 'CO2', fig4)]
                for threshold, name, fig in threshold_lines:
                    fig.add_trace(go.Scatter(
                        x=[start_time, end_time], y=[threshold, threshold],
                        mode="lines", line=dict(color="black", width=2, dash="dot"),
                        name=f"Threshold {name}"
                    ))
            
                # Update layouts for all figures with appropriate y-axis titles
                for fig, title in zip([fig1, fig2, fig3, fig4], ['PM2.5', 'PM10', 'VOC', 'CO2']):
                    # Check for CO2 to set y-axis units
                    yaxis_title = f'{title} Concentration (ppm)' if title == 'CO2' else f'{title} Concentration (µg/m³)'
                    
                    fig.update_layout(
                        title=f'🔴 {title} Levels in Various Locations',
                        xaxis_title='Date & Time',
                        yaxis_title=yaxis_title,
                        legend=dict(orientation="h", yanchor="bottom", y=-0.5, xanchor="center", x=0.5),
                        hovermode='x unified'
                    )

                    # Display the figure
                    st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.info(f"🚨 Please upload right file for choosen Time Interval!")

st.markdown('<hr style="border:1px solid black">', unsafe_allow_html=True)
st.markdown(
    """
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
    <style>
        .footer {
            background-color: #f8f9fa;
            padding: 20px 0;
            color: #333;
            display: flex;
            justify-content: space-between;
            align-items: center;
            text-align: center;
        }
        .footer .logo {
            flex: 1;
        }
        .footer .logo img {
            max-width: 150px;
            height: auto;
        }
        .footer .social-media {
            flex: 2;
        }
        .footer .social-media p {
            margin: 0;
            font-size: 16px;
        }
        .footer .icons {
            margin-top: 10px;
        }
        .footer .icons a {
            margin: 0 10px;
            color: #666;
            text-decoration: none;
            transition: color 0.3s ease;
        }
        .footer .icons a:hover {
            color: #0077b5; /* LinkedIn color as default */
        }
        .footer .icons a .fab {
            font-size: 28px;
        }
        .footer .additional-content {
            margin-top: 10px;
        }
        .footer .additional-content h4 {
            margin: 0;
            font-size: 18px;
            color: #007bff;
        }
        .footer .additional-content p {
            margin: 5px 0;
            font-size: 16px;
        }
    </style>
   <div class="footer">
        <div class="social-media" style="flex: 2;">
            <p>&copy; 2024. All Rights Reserved</p>
            <div class="icons">
                <a href="https://twitter.com/edsglobal?lang=en" target="_blank"><i class="fab fa-twitter" style="color: #1DA1F2;"></i></a>
                <a href="https://www.facebook.com/Environmental.Design.Solutions/" target="_blank"><i class="fab fa-facebook" style="color: #4267B2;"></i></a>
                <a href="https://www.instagram.com/eds_global/?hl=en" target="_blank"><i class="fab fa-instagram" style="color: #E1306C;"></i></a>
                <a href="https://www.linkedin.com/company/environmental-design-solutions/" target="_blank"><i class="fab fa-linkedin" style="color: #0077b5;"></i></a>
            </div>
            <div class="additional-content">
                <h4>Contact Us</h4>
                <p>Email: info@edsglobal.com | Phone: +123 456 7890</p>
                <p>Follow us on social media for the latest updates and news.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True
)
