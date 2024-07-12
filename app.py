"""streamlit app for the sports data visualisation"""
import streamlit as st
import pandas as pd
st.set_page_config(layout="wide")
st.set_option('deprecation.showPyplotGlobalUse', False)

#Use main.py functions in app.py
from main import DataLoader, ExerciseAnalysis, RunAnalysis

if  __name__ == '__main__':
    

    # Load and clean the data
    loader = DataLoader('Sports')
    data = loader.read_data()
    cleaned_data = loader.clean_data(data)

    # Perform run analysis
    running_data = RunAnalysis(cleaned_data)
    unique_running_data = running_data.unique_running_data()

    # Perform exercise analysis
    exercise_analysis = ExerciseAnalysis(cleaned_data)

    #Create a widget to display the weight trend for the excercise which the user inputs
    st.title('Sports data visualisation')    


    col1 ,col2 = st.columns(2)
    with col1:
        st.title('Running analysis')
        # multiselect widget to select the length of the run 
        st.header('Select the length of the run for which you want to see the time trend')
        selectbox_options = cleaned_data['distance'].unique()
        selectbox_options = selectbox_options[~pd.isnull(selectbox_options)]
        selectbox_options = ['Select all'] + selectbox_options.tolist()
        distances= st.selectbox('Select the length of the run', selectbox_options, index=1) 
        if distances == 'Select all':
            #plot the time trend for the excercise 'Run' for the distance selected by the user
            fig1 , ax1  = running_data.plot_pace_trend(distances)
            ax1.set_title(f'Pace trend for the excercise Run for {distances} km')
            st.pyplot(fig1)
        else:
            #plot the time trend for the excercise 'Run' for the distance selected by the user
            fig1 , ax1  = running_data.plot_pace_trend(distances)
            st.pyplot(fig1)
    
        



    with col2:
        st.title('Weight analysis')

        #table with the groups and the excercises in the data
        st.write('Groups and excercises in the data')
        unique_excercises = exercise_analysis.unique_exercise_data()
        st.write(unique_excercises)

        #Create a widget to display the weight trend for the excercise which the user inputs
        #get the unique excercises in the data except the excercise 'Run' and 'Walk' and 'Mountain walk'
        list_excercises = cleaned_data['exercise'].unique()
        list_excercises = [excercise for excercise in list_excercises 
                           if excercise not in ['Run', 'Walk', 'Mountain walk','Stretch']]
        list_excercises = ['Select excercise'] + list_excercises

 
        #create box 
        excercise = st.selectbox('Select the excercise for which you want to see the weight trend', list_excercises)

        #if the user selects an excercise
        if excercise != 'Select excercise':
            _weight_trend_data = exercise_analysis.weight_trend_data(excercise)
            st.write('Weight trend data for the excercise', excercise)
            #only display the data if the user clicks the button and hide the data if the user clicks the button again
            if st.checkbox('Show data'):
                st.write(_weight_trend_data)

            #plot the weight trend for the excercise
            fig , ax = exercise_analysis.plot_weight_trend(excercise)
            st.pyplot(fig)



