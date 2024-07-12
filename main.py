#%%
import pandas as pd
import matplotlib.pyplot as plt
import logging
import matplotlib.dates as mdates
from typing import Tuple, List



plt.style.use('bmh')
logging.basicConfig(level=logging.INFO)

class DataLoader:
    def __init__(self, sheet_name: str) -> None:
        self.sheet_name = sheet_name

    def update_data(self, file_path, sheet_name: str) -> None:
        data = pd.read_excel(file_path, sheet_name=self.sheet_name, dtype=str)
        # Save the data in specific location
        data.to_excel('data.xlsx',sheet_name=sheet_name, index=False)

    def read_data(self) -> pd.DataFrame:
        data = pd.read_excel('data.xlsx', sheet_name=self.sheet_name, dtype=str)
        columns = ['group', 'training_time', 'date', 'exercise', 'variation', 'weight', 'reps', 'total_time', 'distance', 'speed', 'slope', 'notes']
        data.columns = columns
        return data

    def clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        # Forward fill the 'group' and 'date' columns to handle missing values
        data['group'] = data['group'].ffill()
        data['date'] = pd.to_datetime(data['date'].ffill())

        # Fill NaN values in 'training_time' with '1:00'
        data['training_time'] = data['training_time'].fillna('1:00')

        # Strip whitespace from all string columns
        data = data.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

        # Fill NaN values in 'weight' with '80' and replace 'body' with '80'
        data['weight'] = data['weight'].fillna('80').replace('body', '80')
        
        # Fill NaN values in 'reps' with '1'
        data['reps'] = data['reps'].fillna('0')
        
        # Split 'weight' and 'reps' columns by '-' and convert to lists
        data['weight'] = data['weight'].apply(lambda x: list(map(float, x.split('-'))))
        data['reps'] = data['reps'].apply(lambda x: list(map(eval, x.split('-'))))        
        return data

    


class ExerciseAnalysis:
    def __init__(self, data: pd.DataFrame) -> None:
        self.data = data

    def weight_trend_data(self, exercise: str) -> pd.DataFrame:
        exercise_data = self.data.loc[self.data['exercise'] == exercise]
        exercise_data1 = exercise_data.copy()
        exercise_data = exercise_data.explode('weight')
        reps_explode = exercise_data1.explode('reps')['reps']
        exercise_data['reps'] = reps_explode
        exercise_data['weight'] = exercise_data['weight'].astype(float)
        exercise_data['reps'] = exercise_data['reps'].astype(float)
        return exercise_data

    def plot_weight_trend(self, exercise: str, show: bool = False) -> Tuple[plt.Figure, plt.Axes]:
        exercise_data = self.weight_trend_data(exercise)
        fig, ax = plt.subplots()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
        ax.scatter(exercise_data['date'], exercise_data['weight'], s=exercise_data['reps']*10, c=exercise_data['reps'], cmap='rainbow', alpha=0.5)
        ax.set_xlabel('Date')
        ax.set_ylabel('Weight (kg)')
        colorbar = plt.colorbar(ax.collections[0])
        colorbar.set_label('Reps')
        ax.set_title(f'Weight trend of the exercise {exercise}')
        ax.set_xticklabels(ax.get_xticks(), rotation=45)
        if show:
            plt.show()
        return fig, ax

    def unique_exercise_data(self) -> pd.DataFrame:
        unique_exercises = self.data['exercise'].unique()
        unique_exercises = [exercise for exercise in unique_exercises if exercise not in ['Run', 'Walk', 'Mountain walk', 'Stretch']]
        unique_exercise_data = pd.DataFrame()
        unique_exercise_data['exercise'] = unique_exercises

        for exercise in unique_exercises:
            unique_exercise_data.loc[unique_exercise_data['exercise'] == exercise, 'count'] = \
                len(self.data.loc[self.data['exercise'] == exercise])
        
        for exercise in unique_exercises:
            try:
                exercise_data = self.weight_trend_data(exercise)
                max_weight = exercise_data['weight'].max()
                unique_exercise_data.loc[unique_exercise_data['exercise'] == exercise, 'max_weight'] = max_weight
                unique_exercise_data.loc[unique_exercise_data['exercise'] == exercise, 'max_weight_reps'] =\
                      exercise_data.loc[exercise_data['weight'] == max_weight, 'reps'].values[0]
            except:
                pass

        return unique_exercise_data

class RunAnalysis:
    def __init__(self, data: pd.DataFrame) -> None:
        self.data = data


    def running_data(self) -> pd.DataFrame:
        # Find all Run exercises in the data
        running_data = self.data.loc[self.data['exercise'] == 'Run'].copy()
        # Change the format of the total time 
        running_data.loc[:, 'total_time'] = running_data['total_time'].astype(str)
        # Convert 'total_time' from MM:ss to seconds
        if 'total_time_delta' not in running_data.columns:
            running_data['total_time_delta'] = pd.Series(dtype='timedelta64[ns]')       
        running_data.loc[:, 'total_time_delta'] = running_data['total_time'].apply(
            lambda x: int(x.split(':')[0]) * 60 + int(x.split(':')[1]) if x != 'nan' else 0
        )
        # Ensure 'total_time_delta' column is of type 'timedelta64[ns]' before assignment
        running_data.loc[:, 'total_time_delta'] = pd.to_timedelta(running_data['total_time_delta'], unit='s')
            # Calculate speed and distance based on available data
        for k, v in running_data.loc[:, ['date', 'total_time_delta', 'distance', 'speed']].iterrows():
            if v['total_time_delta'] != pd.Timedelta(seconds=0) and pd.notnull(v['distance']):
                running_data.loc[k, 'speed'] = float(v['distance']) / (float(v['total_time_delta'].seconds) / 3600)
            elif v['total_time_delta'] != pd.Timedelta(seconds=0) and pd.notnull(v['speed']):
                pass # speed is already calculated
            #     # Ensure 'v['speed']' is treated as a float
            #     speed_as_float = float(v['speed'])
            #     running_data.loc[k, 'distance'] = speed_as_float * (v['total_time_delta'].seconds / 3600)   
            elif pd.notnull(v['distance']) and pd.notnull(v['speed']):
                running_data.loc[k, 'total_time_delta'] = pd.Timedelta(seconds=(v['distance'] / v['speed']) * 3600)
            else:
                logging.warning(f"Row {k} has missing values for 'total_time_delta', 'distance', and 'speed'")

            # Calculate pace for each row
            total_seconds = running_data['total_time_delta'].dt.total_seconds()
            running_data['distance_float'] = running_data['distance'].astype(float)
            valid_times = total_seconds != 0
            running_data.loc[valid_times, 'pace'] = (total_seconds[valid_times] / 60) / running_data.loc[valid_times, 'distance_float']
        return running_data

    def unique_running_data(self) -> pd.DataFrame:
        running_data = self.running_data()
        unique_running_data = pd.DataFrame()
        unique_running_data['distance'] = running_data['distance'].unique()
        # delete NaN values
        unique_running_data = unique_running_data.dropna()
        unique_running_data['count'] = unique_running_data['distance'].apply(
            lambda x: len(running_data.loc[running_data['distance'] == x])
        )
        # add the min pace for each distance
        for distance in unique_running_data['distance'] :
                unique_running_data.loc[unique_running_data['distance'] == distance, 'min_pace'] = \
                    running_data.loc[running_data['distance'] == distance, 'pace'].min()
        return unique_running_data
  
    def plot_pace_trend(self, distance: str = '3') -> Tuple[plt.Figure, plt.Axes]:
        run_data = self.running_data()
        run_data = run_data.loc[run_data['distance'] == distance]
        fig, ax = plt.subplots()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
        ax.plot(run_data['date'], run_data['pace'], 'r-', marker='o')
        ax.set_xlabel('Date')
        ax.set_ylabel('Total time (min)')
        ax.set_title('Total time spent running for 3km')
        ax.tick_params(axis='x', rotation=45)
        return fig, ax

#%%
if __name__ == "__main__":
    # Load and clean the data
    loader = DataLoader('Sports')
    # loader.update_data(r"C:\Users\User\Documents\Version2\Data.xlsx", 'Sports')

    data = loader.read_data()
    cleaned_data = loader.clean_data(data)

    # Perform run analysis
    run_analysis = RunAnalysis(cleaned_data)
    unique_running_data = run_analysis.unique_running_data()
    print(unique_running_data)   


# %%
