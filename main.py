"""programm to create and interactive dashboard to visualize data from sporting data to get a clear
overview of the data and to be able to filter the data based on the exercise type and the date"""

#%%
import pandas as pd
import matplotlib.pyplot as plt
import logging
import regex as re
import matplotlib.dates as mdates

plt.style.use('bmh')
logging.basicConfig(level=logging.INFO)

# %% function to read the data from the xls file
def read_data()->pd.DataFrame:
    '''Reads the data from the xls file and returns the data in a pandas dataframe, change the column names'''
    data = pd.read_excel(r"C:\Users\User\Documents\Version2\Data.xlsx", sheet_name='Sports',dtype=str)
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
def plot_time_trend_run(data:pd.DataFrame, distance:str = 3)->list:
    # plot the time needed for the excercise run for 3km
    run_data = data.loc[data['excercise'] == 'Run']
    run_data = run_data.loc[run_data['distance'] == distance]
    # plot the data with the x axis spaced per day and the y axis the total time format x axis to only show day and month
    #Change total time from MM:SS to minutes
    run_data['total_time'] = run_data['total_time'].apply(lambda x: int(x.split(':')[0]) + int(x.split(':')[1])/60)
    fig, ax = plt.subplots()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
    plt.plot(run_data['date'], run_data['total_time'], 'r-')
    plt.xlabel('Date')
    plt.ylabel('Total time (min)')
    plt.title('Total time spent running for 3km')
    plt.xticks(rotation=45)
    plt.show()
    return fig, ax



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
    fig, ax = plt.subplots()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
    plt.scatter(excercise_data['date'], excercise_data['weight'],
                 s=excercise_data['reps']*10, c=excercise_data['reps'], 
                 cmap='rainbow', alpha=0.5)
    plt.xlabel('Date')
    plt.ylabel('Weight (kg)')
    plt.colorbar(label='Reps')
    plt.title(f'Weight trend of the excercise {excercise}')
    plt.xticks(rotation=45)
    if show == True:
        plt.show()
    return fig, ax 


#%% read the data and clean the data
if __name__ == "__main__":
    data = read_data()
    data = clean_data(data)
    plot_time_trend_run_3k(data)
    plot_weight_trend(data, 'Deadlift',1)
    
  

# %%
