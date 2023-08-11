import streamlit as st
import ephem
from datetime import datetime
import pytz

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

    # Open the Excel file
    workbook = openpyxl.load_workbook('celestial_angles.xlsx')
    sheet = workbook.active

    # Write user-provided input to Excel
    sheet['A12'] = 'Latitude (degrees)'
    sheet['A13'] = 'Longitude (degrees)'
    sheet['A14'] = 'Date'
    sheet['A15'] = 'Time (IST)'
    sheet['B12'] = latitude
    sheet['B13'] = longitude
    sheet['B14'] = date_time_ist.strftime('%Y-%m-%d %H:%M')
    sheet['B15'] = date_time_ist.strftime('%H:%M')

    # Calculate and write the angles for each object
    celestial_objects = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'North Node', 'South Node']
    for i, obj_name in enumerate(celestial_objects):
        if obj_name == 'North Node':
            obj_north = getattr(ephem, 'Moon')(observer)
            obj_north.compute(observer)
            sheet.cell(i+2, 1, 'Node (Asc)')
            # Get azimuth and elevation in degrees
            az_north = obj_north.az * 180.0 / ephem.pi
            alt_north = obj_north.alt * 180.0 / ephem.pi
            sheet.cell(i+2, 2, az_north)
            sheet.cell(i+2, 3, alt_north)
        elif obj_name == 'South Node':
            # Calculate South Node (Descending Lunar Node) based on North Node position
            obj_south = getattr(ephem, 'Moon')(observer)
            obj_south.compute(observer)
            az_north = obj_north.az * 180.0 / ephem.pi
            alt_north = obj_north.alt * 180.0 / ephem.pi
            az_south = (az_north + 180.0) % 360.0
            alt_south = alt_north * -1.0
            sheet.cell(i+2, 1, 'Node (Dec)')
            sheet.cell(i+2, 2, az_south)
            sheet.cell(i+2, 3, alt_south)
        else:
            obj = getattr(ephem, obj_name)()
            obj.compute(observer)
            sheet.cell(i+2, 1, obj_name)
            # Get azimuth and elevation in degrees
            az = obj.az * 180.0 / ephem.pi
            alt = obj.alt * 180.0 / ephem.pi
            sheet.cell(i+2, 2, az)
            sheet.cell(i+2, 3, alt)

    # Save the Excel file
    workbook.save('celestial_angles.xlsx')

# Streamlit UI
st.title('Celestial Object Angles Calculator')

# User input
latitude = st.text_input('Enter Latitude (degrees):', '35.6895')
longitude = st.text_input('Enter Longitude (degrees):', '139.6917')
date = st.date_input('Enter Date:')
time = st.time_input('Enter Time (IST):')

# Calculate angles
if st.button('Calculate Angles'):
    try:
        # Call the function to calculate angles and update the Excel file
        calculate_angles(float(latitude), float(longitude), date.strftime('%Y-%m-%d'), time.strftime('%H:%M'))
        st.success('Angles calculated and saved in celestial_angles.xlsx!')
    except Exception as e:
        st.error(f'An error occurred: {e}')
