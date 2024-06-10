"""Basic visualisation of gym excercise data"""
#%% 
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

#start logging 
import logging
logging.basicConfig(level=logging.INFO)


#%% Load data
data = pd.read_csv("sportData.csv", delimiter=';')

#%% modify data to fill al NaN values with the preceding value in the column
data['group'].fillna(method='ffill', inplace=True)
# same for column 'Date
data['date'].fillna(method='ffill', inplace=True)

logging.info(data['exercise'])

#%% Plot the total time spent on a 3k run
#find all value of 'date' column where column 'excerciece' is 'run'
run_data = data.loc[data['exercise'] == 'Run ']

#Plot the total time spent running only where the 'distance' is 3
run_data = run_data.loc[run_data['distance'] == 3]

#%% Plot the total time spent on a 3k run
#plot on the x-axis the 'date' and on the y-axis the 'totalTime'
plt.plot(run_data['date'], run_data['totalTime'], 'ro')
plt.xlabel('Date')
plt.ylabel('Total time (min)')
plt.title('Total time spent running for 3km')
plt.show()




# %%
