# %% test file to import the 'Sports' page from the data xls file and modify to column names
import pandas as pd
#start logging 
import logging
logging.basicConfig(level=logging.DEBUG)


# %% function to read the data from the xls file
def read_data()->pd.DataFrame:
    '''Reads the data from the xls file and returns the data in a pandas dataframe, change the column names'''
    data = pd.read_excel(r'C:\Users\User\Documents\personal\Version2\Data.xlsx', sheet_name='Sports')
    columns = ['group', 'training_time', 'date', 'excercise', 'variation', 'weight', 'reps', 'total_time', 'distance','speed','slope','notes']
    data.columns = columns
    return data

#%% function to clean the data 
def clean_data(data:pd.DataFrame)->pd.DataFrame:
    '''for the first column 'group' fill the missing values with the previous value, ...
    for the second column replace NaN with string '1:00', ...
    for the third fill the NaN values with the previous value in the column'''
    data['group'] = data['group'].fillna(method='ffill')
    data['training_time'] = data['training_time'].fillna('1:00')
    data['date'] = data['date'].fillna(method='ffill')    
    return data

#%%run file to test the function
if __name__ == "__main__":
    data = read_data()
    logging.info(data.head())
    data = clean_data(data)
    logging.info(data.head())
# %%
