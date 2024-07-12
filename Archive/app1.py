"""streamlit app for the sports data visualisation"""
import streamlit as st
st.set_page_config(layout="wide")
st.set_option('deprecation.showPyplotGlobalUse', False)
import pandas as pd
import matplotlib.pyplot as plt
import logging
import regex as re

logging.basicConfig(level=logging.INFO)

#Use main.py functions in app.py
#from main import read_data, clean_data, weight_trend_data, plot_time_trend_run, plot_weight_trend, unique_excercise_data

from main import DataLoader, ExerciseAnalysis

if  __name__ == '__main__':

    # Load and clean the data
    loader = DataLoader(r"C:\Users\User\Documents\Version2\Data.xlsx", 'Sports')
    data = loader.read_data()
    cleaned_data = loader.clean_data(data)
    #Create a widget to display the weight trend for the excercise which the user inputs
    st.title('Sports data visualisation')    





    col1 ,col2 = st.columns(2)
    with col1:
        st.title('Running analysis')
        # multiselect widget to select the length of the run 
        st.header('Select the length of the run for which you want to see the time trend')
        distances= st.multiselect('Select the length of the run', data['distance'].unique(), default = ['3']) 
        if type(distances) == str:
            #plot the time trend for the excercise 'Run' for the distance selected by the user
            fig1 , ax1  = ExerciseAnalysis.plot_time_trend_run(distances)
            st.pyplot(fig1)
        else:
            for distance in distances:
                #plot the time trend for the excercise 'Run' for the distance selected by the user
                fig1 , ax1  = ExerciseAnalysis.plot_time_trend_run(data,distance)
                ax1.set_title(f'Time trend for the excercise Run for {distance} km')
                st.pyplot(fig1)
    
        



    with col2:
        st.title('Weight analysis')

        #table with the groups and the excercises in the data
        st.write('Groups and excercises in the data')
        unique_excercises = ExerciseAnalysis.unique_excercise_data(data)
        st.write(unique_excercises)

        #Create a widget to display the weight trend for the excercise which the user inputs
        #get the unique excercises in the data except the excercise 'Run' and 'Walk' and 'Mountain walk'
        list_excercises = data['excercise'].unique()
        list_excercises = [excercise for excercise in list_excercises 
                           if excercise not in ['Run', 'Walk', 'Mountain walk','Stretch']]
        list_excercises = ['Select excercise'] + list_excercises


        #create box 
        excercise = st.selectbox('Select the excercise for which you want to see the weight trend', list_excercises)

        #if the user selects an excercise
        if excercise != 'Select excercise':
            weight_trend_data = ExerciseAnalysis.weight_trend_data(data, excercise)
            st.write('Weight trend data for the excercise', excercise)
            #only display the data if the user clicks the button and hide the data if the user clicks the button again
            if st.checkbox('Show data'):
                st.write(weight_trend_data)

            #plot the weight trend for the excercise
            fig , ax = ExerciseAnalysis.plot_weight_trend(weight_trend_data, excercise)
            st.pyplot(fig)



