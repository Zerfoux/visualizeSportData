"""programm to create and interactive dashboard to visualize data from sporting data to get a clear
overview of the data and to be able to filter the data based on the exercise type and the date"""

#%%
import pandas as pd
import logging
import regex as re
import plotly.express as px

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
    return data

# function to plot the time trend of the total time spent on a 3k run 
def plot_time_trend_run_3k(data:pd.DataFrame):
    run_data = data.loc[data['excercise'] == 'Run']
    run_data = run_data.loc[run_data['distance'] == '3']  
    # Convert total time from MM:SS to minutes
    run_data['total_time'] = run_data['total_time'].apply(lambda x: int(x.split(':')[0]) + int(x.split(':')[1])/60)
    # Create the plot
    fig = px.line(run_data, x='date', y='total_time', title='Total time spent running for 3km',
                  labels={'date': 'Date', 'total_time': 'Total time (min)'})
    # Update the x-axis format
    fig.update_xaxes(tickformat='%b-%d')
    return fig



# function to get the data for the weight trend of an excercise
def weight_trend_data(data:pd.DataFrame, excercise: str)->pd.DataFrame:
    excercise_data = data.loc[data['excercise'] == excercise]
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

def plot_weight_trend(data:pd.DataFrame, excercise: str, show = False )-> list: 
    excercise_data = weight_trend_data(data, excercise)
    #plot the data with the x axis spaced per day and the y axis the weight format x axis to only show day and month
    #Change to the marker color relative to the reps value and the size of the marker relative to the reps value
    fig = px.scatter(excercise_data, x='date', y='weight', color='reps', size='reps', title='Weight trend for ' + excercise,
                     labels={'date': 'Date', 'weight': 'Weight (kg)', 'reps': 'Reps'})
    fig.update_xaxes(tickformat='%b-%d')
    fig.update_traces(marker=dict(line=dict(width=1, color='DarkSlateGrey')))
    #show the plot
    if show == True:
        fig.show()
    return fig  


#%% read the data and clean the data
if __name__ == "__main__":
    data = read_data()
    data = clean_data(data)
    plot_time_trend_run_3k(data)
    plot_weight_trend(data, 'Deadlift',1)


# %%
