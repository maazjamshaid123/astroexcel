import streamlit as st
import ephem
from datetime import datetime
import pytz
import pandas as pd

class CelestialAnglesCalculator:
    st.set_page_config(page_title='Celestial Object Angles Calculator')

    def __init__(self, latitude, longitude, date, time):
        """
        Initializes the CelestialAnglesCalculator with the provided latitude, longitude, date, and time.
        
        Parameters:
        ----------
        latitude (float): Latitude of the observer's location.
        longitude (float): Longitude of the observer's location.
        date (str): Date in 'YYYY-MM-DD' format.
        time (str): Time in 'HH:MM' format.
        
        Variables:
        ---------
        self.latitude (float): Latitude of the observer's location.
        self.longitude (float): Longitude of the observer's location.
        self.date (str): Date in 'YYYY-MM-DD' format.
        self.time (str): Time in 'HH:MM' format.
        self.pst (timezone): PST timezone information.
        self.utc (timezone): UTC timezone information.
        self.date_time_pst (datetime): Localized date and time in PST.
        self.date_time_utc (datetime): Localized date and time in UTC.
        self.observer (ephem.Observer): PyEphem observer object.
        """
        self.latitude = latitude
        self.longitude = longitude
        self.date = date
        self.time = time
        self.pst = pytz.timezone('Asia/Karachi')
        self.utc = pytz.utc
        self.date_time_pst = datetime.strptime(date + ' ' + time, '%Y-%m-%d %H:%M')
        self.date_time_pst = self.pst.localize(self.date_time_pst)
        self.date_time_utc = self.date_time_pst.astimezone(self.utc)
        self.observer = ephem.Observer()
        self.observer.lat = str(latitude)
        self.observer.long = str(longitude)
        self.observer.date = self.date_time_utc

    def calculate_angles(self):
        """
        Calculates the azimuth and elevation angles for a set of celestial objects.
        
        Variables:
        ---------
        data (dict): Dictionary to store celestial object names and their calculated azimuth and elevation angles.
        celestial_objects (list): List of celestial objects to calculate angles for.
        obj_name (str): Name of the current celestial object.
        obj (ephem.Body): PyEphem object for the current celestial object.
        az (float): Azimuth angle in degrees.
        alt (float): Elevation angle in degrees.
        
        Returns:
        -------
        pd.DataFrame: DataFrame containing the celestial objects and their corresponding azimuth and elevation angles.
        """
        data = {
            'Object': [],
            'Azimuth (degrees)': [],
            'Elevation (degrees)': []
        }
        celestial_objects = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn']
        for obj_name in celestial_objects:
            obj = getattr(ephem, obj_name)()
            obj.compute(self.observer)

            az = obj.az * 180.0 / ephem.pi
            alt = obj.alt * 180.0 / ephem.pi

            data['Object'].append(obj_name)
            data['Azimuth (degrees)'].append(az)
            data['Elevation (degrees)'].append(alt)

        return pd.DataFrame(data)

st.title('Celestial Object Angles Calculator')

latitude = st.text_input('Enter Latitude (degrees):', '35.6895')
longitude = st.text_input('Enter Longitude (degrees):', '139.6917')
date = st.date_input('Enter Date:')
time = st.time_input('Enter Time (PST):')

if st.button('Calculate Angles'):
    try:
        calculator = CelestialAnglesCalculator(float(latitude), float(longitude), date.strftime('%Y-%m-%d'), time.strftime('%H:%M'))
        df = calculator.calculate_angles()
        st.success('Angles calculated!')
        st.table(df)
    except Exception as e:
        st.error(f'An error occurred: {e}')
