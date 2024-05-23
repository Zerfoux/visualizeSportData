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
from main import read_data, clean_data, weight_trend_data, plot_time_trend_run_3k, multi_plot_weight_trend



if  __name__ == '__main__':

    #read the data
    data = read_data()
    #clean the data
    data = clean_data(data)
    #Create a widget to display the weight trend for the excercise which the user inputs
    st.title('Sports data visualisation')    

    col1 ,col2 = st.columns(2)
    with col1:
        #Create a widget to display the time trend for the excercise 'Run' for 3km
        st.header('Time trend for the excercise Run for 3km')
        st.plotly_chart(plot_time_trend_run_3k(data)) 
        

    with col2:
        #Create a widget to display the weight trend for the excercise which the user inputs
        #get the unique excercises in the data except the excercise 'Run' and 'Walk' and 'Mountain walk'
        list_excercises = data['excercise'].unique()
        list_excercises = [excercise for excercise in list_excercises 
                           if excercise not in ['Run', 'Walk', 'Mountain walk','Stretch']]


        #create a checkbox widget to select the excercise for which the user wants to see the weight trend
        excercises = st.multiselect('Select the excercise for which you want to see the weight trend', list_excercises)
        #if the user selects an excercise
        
        if len(excercises) > 1:
            st.plotly_chart(multi_plot_weight_trend(data, excercises))

        elif len(excercises) == 1:
            weight_trend_data = weight_trend_data(data, excercises[0])
            st.write('Weight trend data for the excercise', excercises[0])
            
            #only display the data if the user clicks the button and hide the data if the user clicks the button again
            if st.checkbox('Show data'):
                st.write(weight_trend_data)
            #plot the weight trend for the excercise
            st.plotly_chart(multi_plot_weight_trend(data, excercises))    


