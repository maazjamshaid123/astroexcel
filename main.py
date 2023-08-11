!pip install streamlit

import streamlit as st
import pandas as pd
import ephem
from datetime import datetime
import pytz
import openpyxl
from io import BytesIO

# Function to calculate azimuth and elevation angles
def calculate_angles(latitude, longitude, date, time):
    # Combine the provided date and time
    date_time_ist = datetime.strptime(date + ' ' + time, '%Y-%m-%d %H:%M')

    # Convert user-provided IST datetime to UTC
    ist = pytz.timezone('Asia/Kolkata')
    utc = pytz.utc
    date_time_ist = ist.localize(date_time_ist)
    date_time_utc = date_time_ist.astimezone(utc)

    # Create a PyEphem observer object
    observer = ephem.Observer()
    observer.lat = str(latitude)
    observer.long = str(longitude)

    # Create a new DataFrame to store results
    results = pd.DataFrame(columns=['Object', 'Azimuth', 'Elevation'])

    # Calculate and write the angles for each object
    celestial_objects = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'North Node', 'South Node']
    for obj_name in celestial_objects:
        if obj_name == 'North Node':
            obj_north = getattr(ephem, 'Moon')(observer)
            obj_north.compute(observer)
            azimuth_north = obj_north.az * 180.0 / ephem.pi
            elevation_north = obj_north.alt * 180.0 / ephem.pi
            results = results.append({'Object': 'Node (Asc)', 'Azimuth': azimuth_north, 'Elevation': elevation_north}, ignore_index=True)
        elif obj_name == 'South Node':
            # Calculate South Node (Descending Lunar Node) based on North Node position
            obj_south = getattr(ephem, 'Moon')(observer)
            obj_south.compute(observer)
            azimuth_north = obj_north.az * 180.0 / ephem.pi
            elevation_north = obj_north.alt * 180.0 / ephem.pi
            azimuth_south = (azimuth_north + 180.0) % 360.0
            elevation_south = elevation_north * -1.0
            results = results.append({'Object': 'Node (Dec)', 'Azimuth': azimuth_south, 'Elevation': elevation_south}, ignore_index=True)
        else:
            obj = getattr(ephem, obj_name)()
            obj.compute(observer)
            azimuth = obj.az * 180.0 / ephem.pi
            elevation = obj.alt * 180.0 / ephem.pi
            results = results.append({'Object': obj_name, 'Azimuth': azimuth, 'Elevation': elevation}, ignore_index=True)

    # Save the results to an Excel file
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        results.to_excel(writer, index=False, sheet_name='Celestial Angles')
    output.seek(0)
    return output

# Streamlit UI
st.title('Celestial Object Angles Calculator')
st.write('Enter your location and date/time (IST) to calculate azimuth and elevation angles.')

latitude = st.number_input('Latitude (degrees):', -90.0, 90.0, 35.6895)
longitude = st.number_input('Longitude (degrees):', -180.0, 180.0, 139.6917)
date = st.date_input('Date (IST):')
time = st.time_input('Time (IST):')

if st.button('Calculate Angles'):
    # Call the function to calculate angles and generate Excel file
    excel_file = calculate_angles(latitude, longitude, date.strftime('%Y-%m-%d'), time.strftime('%H:%M'))
    st.success('Angles calculated! You can download the Excel file below.')
    st.download_button('Download Excel File', excel_file, file_name='celestial_angles.xlsx', key='excel-download')

# Display the calculated results in a DataFrame
st.subheader('Calculated Angles:')
if 'excel_file' in locals():
    df = pd.read_excel(excel_file)
    st.write(df)
