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

    

    col1 ,col2 = st.columns(2)
    with col1:
        st.title('Running Performance')
        st.markdown('In this section, we will analyze the running performance based on the data obtained during training.\
                    The training mostly consist of running exercises. We will analyze the pace trend for each distance.')
        
        #table with the unique distances in the data
        st.write(unique_running_data)

        # multiselect widget to select the length of the run 
        st.header('Select the length of the run for which you want to see the time trend')
        selectbox_options = cleaned_data['distance'].unique()
        selectbox_options = selectbox_options[~pd.isnull(selectbox_options)]
        selectbox_options = ['Select all'] + selectbox_options.tolist()
        distances= st.selectbox('Select the length of the run', selectbox_options, index=1) 
        if distances == 'Select all':
            #plot the time trend for the exercise 'Run' for the distance selected by the user
            distances = unique_running_data['Distance (km)'].astype(str).tolist()
            fig1 , ax1  = running_data.plot_pace_trend(distances)
            ax1.set_title(f'Pace trend for the exercise Run for distances') 
            st.pyplot(fig1)
        else:
            #plot the time trend for the exercise 'Run' for the distance selected by the user
            fig1 , ax1  = running_data.plot_pace_trend(distances)
            st.pyplot(fig1)
    
        



    with col2:
        st.title('Athletic Performance')
        st.write('In this section, we will analyze the athletic performance based on the data obtained during training.\
                 The training mostly consist of weighted exercises in the gym. Where for each exercise,\
                 the weight lifted is recorded. We will analyze the weight trend for each exercise.') 

        st.header('Group exercise performance')
        #table with the groups in the data
        group_exercise_data = exercise_analysis.group_exercise_data()
        st.write(group_exercise_data)

        #table with the groups and the exercises in the data
        st.header('Exercise analysis')
        if  st.button('Click to see the groups and exercises in the data'): 
            unique_exercises = exercise_analysis.unique_exercise_data()
            st.write(unique_exercises)

        #Create a widget to display the weight trend for the exercise which the user inputs
        #get the unique exercises in the data except the exercise 'Run' and 'Walk' and 'Mountain walk'
        list_exercises = cleaned_data['exercise'].unique()
        list_exercises = [exercise for exercise in list_exercises 
                           if exercise not in ['Run', 'Walk', 'Mountain walk','Stretch']]
        list_exercises = ['Select exercise'] + list_exercises

 
        #create box 
        exercise = st.selectbox('', list_exercises)

        #if the user selects an exercise
        if exercise != 'Select exercise':
            _weight_trend_data = exercise_analysis.weight_trend_data(exercise)
            st.write('Weight trend data for the exercise', exercise)
            #only display the data if the user clicks the button and hide the data if the user clicks the button again
            if st.checkbox('Show data'):
                st.write(_weight_trend_data)

            #plot the weight trend for the exercise
            fig , ax = exercise_analysis.plot_weight_trend(exercise)
            st.pyplot(fig)



