"""programm to create and interactive dashboard to visualize data from sporting data to get a clear
overview of the data and to be able to filter the data based on the exercise type and the date"""

#%%
import pandas as pd
import logging
import regex as re
import plotly.express as px
import plotly.graph_objects as go

logging.basicConfig(level=logging.INFO)

# %% function to read the data from the xls file
def read_data()->pd.DataFrame:
    '''Reads the data from the xls file and returns the data in a pandas dataframe, change the column names'''
    data = pd.read_excel(r'C:\Users\User\Documents\personal\Version2\Data.xlsx', sheet_name='Sports',dtype=str)
    columns = ['group', 'training_time', 'date', 'excercise', 
               'variation', 'weight', 'reps', 'total_time', 
               'distance','speed','slope','notes']
    data.columns = columns
    return data

# function to clean the data 
def clean_data(data:pd.DataFrame)->pd.DataFrame:
    '''for the first column 'group' fill the missing values with the previous value, ...
    for the second column replace NaN with string '1:00', ...
    for the third fill the NaN values with the previous value in the column'''
    data['group'] = data['group'].ffill()
    data['training_time'] = data['training_time'].fillna('1:00')
    data['date'] = data['date'].ffill()    
    #delete all ending spaces from all the columns
    data = data.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    #change the data in the date column from a string to a datetime object
    data['date'] = pd.to_datetime(data['date'])
    #fill the NaN values in the weight column with 80
    data['weight'] = data['weight'].fillna('80')
    #replace all the values in the weight column that are body with 80
    data['weight'] = data['weight'].replace('body', '80')
    #replace all nan values in reps with 1 
    data['reps'] = data['reps'].fillna('1')
    #change the data in the weight column from a string where the seperator is '-' to a list of strings
    data['weight'] = data['weight'].apply(lambda x: x.split('-'))
    #change the data in the reps column from a string where the seperator is '-' to a list of strings
    data['reps'] = data['reps'].apply(lambda x: x.split('-'))
    #replace all values in the reps column with the result of the expression given in the string 
    for i in range(len(data)):
        for j in range(len(data['reps'][i])):
            data['reps'][i][j] = eval(data['reps'][i][j])
    #for the columns total_time, distance, speed if one of these columns is NaN replace the value with value calculated from the other columns
    #for total_time calculate the total time from the speed and distance
    # for i in range(len(data)):
    #     if data['total_time'][i] == 'nan':
    #         if data['distance'][i] != 'nan' and data['speed'][i] != 'nan':
    #             data['total_time'][i] = str(int(data['distance'][i])/int(data['speed'][i])) 
    # #for distance calculate the distance from the total time and speed
    #     elif data['distance'][i] == 'nan':
    #         if data['total_time'][i] != 'nan' and data['speed'][i] != 'nan':
    #             data['distance'][i] = str(int(data['total_time'][i])*int(data['speed'][i]))
    # #for speed calculate the speed from the total time and distance
    #     elif data['speed'][i] == 'nan':
    #         if data['total_time'][i] != 'nan' and data['distance'][i] != 'nan':
    #             data['speed'][i] = str(int(data['distance'][i])/int(data['total_time'][i]))
    return data

# function to plot the time trend of the total time spent on a 3k run 
def plot_time_run(data:pd.DataFrame, distance = '3')->go.Figure:
    run_data = data.loc[data['excercise'] == 'Run']
    run_data = run_data.loc[run_data['distance'] == distance]  
    # Convert total time from MM:SS to minutes
    run_data['total_time'] = run_data['total_time'].apply(lambda x: int(x.split(':')[0]) + int(x.split(':')[1])/60)
    # Create the plot
    fig = go.Figure()
    fig = fig.add_trace(go.Scatter(x=run_data['date'], y=run_data['total_time'],line_shape = 'spline', marker = dict(size=15)))
    fig.update_xaxes(tickformat='%b-%d')
    fig.update_yaxes(title_text='Total time (minutes)')
    fig.update_xaxes(title_text='Date')
    fig.update_layout(title='Time trend for a ' + distance + 'k run')
    return fig 

# function to get the data for the weight trend of an excercise
def weight_trend_data(data:pd.DataFrame, excercise: str)->pd.DataFrame:
    excercise_data = data.loc[data['excercise'] == str(excercise)]
    excercise_data1  = excercise_data.copy()
    excercise_data = excercise_data.explode('weight')
    #if the data in the weight column is a list create a new row for each value in the list
    weight_explode = excercise_data1.explode('weight')['weight']
    reps_explode = excercise_data1.explode('reps')['reps']
    excercise_data['reps'] = reps_explode
    #change the data in the weight column from a string to a float
    excercise_data['weight'] = excercise_data['weight'].astype(float)
    #change the data in the reps column from a string to a float
    excercise_data['reps'] = excercise_data['reps'].astype(float)
    return excercise_data

def weight_trend_data_list(data:pd.DataFrame, excercise: list)->pd.DataFrame:
    excercise_data = {}
    excercise_data1 = {}
    for excercise in excercise:
        excercise_data[excercise] = data.loc[data['excercise'] == excercise]
        excercise_data1[excercise]  = excercise_data[excercise].copy()
        excercise_data[excercise] = excercise_data[excercise].explode('weight')
        #if the data in the weight column is a list create a new row for each value in the list
        weight_explode = excercise_data1[excercise].explode('weight')['weight']
        reps_explode = excercise_data1[excercise].explode('reps')['reps']
        excercise_data[excercise]['reps'] = reps_explode
        #change the data in the weight column from a string to a float
        excercise_data[excercise]['weight'] = excercise_data[excercise]['weight'].astype(float)
        #change the data in the reps column from a string to a float
        excercise_data[excercise]['reps'] = excercise_data[excercise]['reps'].astype(float)
    return excercise_data

def multi_plot_weight_trend(data: pd.DataFrame, excercises: list, show = False) -> go.Figure: 
    #make a px.scatter plot for each excercise in the list and add the plot to the list
    fig = go.Figure()
    for excercise in excercises: 
        excercise_data = weight_trend_data(data, excercise)
        #plot the data with the x axis spaced per day and the y axis the weight format x axis to only show day and month
        #Change to the marker color relative to the reps value and the size of the marker relative to the reps value
        fig.add_trace(go.Scatter(x=excercise_data['date'], y=excercise_data['weight'],
                                 marker = dict(size= excercise_data['reps']),
                                 mode='markers', name=excercise))
    fig.update_xaxes(tickformat='%b-%d')
    fig.update_yaxes(title_text='Weight (kg)')
    fig.update_xaxes(title_text='Date')
    fig.update_layout(title='Weight trend for ' + excercise)
    fig1 = fig
    #show the plot
    if show == True:
        fig.show()
    return fig1 


#%% read the data and clean the data
if __name__ == "__main__":
    data = read_data()
    data = clean_data(data)


    excercises = ['Deadlift', 'Bench press', 'Squat'] 
    fig = multi_plot_weight_trend(data, excercises, 1)

# %%
