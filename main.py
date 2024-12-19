""" This script is used to analyze the sports data of a person. 
    The data is stored in an Excel file and contains the following columns:
    - group: the group to which the exercise belongs
    - training_time: the time spent on the exercise
    - date: the date of the exercise
    - exercise: the type of exercise
    - variation: the variation of the exercise
    - weight: the weight used for the exercise
    - reps: the number of repetitions
    - total_time: the total time spent on the exercise
    - distance: the distance covered
    - speed: the speed
    - slope: the slope
    - notes: additional notes
    
    The script provides three classes: DataLoader, ExerciseAnalysis, and RunAnalysis. 
    DataLoader is used to load and clean the data, while ExerciseAnalysis is used to analyze the exercise data.
    """
#%%
import pandas as pd
import matplotlib.pyplot as plt
import logging
import matplotlib.dates as mdates
from typing import Tuple, List, Union
import os

logging.basicConfig(level=logging.INFO)

class DataLoader:
    def __init__(self, sheet_name: str) -> None:
        self.sheet_name = sheet_name

    def update_data(self, file_path, sheet_name: str) -> None:
        data = pd.read_excel(file_path, sheet_name=self.sheet_name, dtype=str)
        # Save the data in specific location
        # Check if the file is accessible
        if os.access(file_path, os.W_OK):
            data.to_excel(file_path, sheet_name='Sports', index=False)
        else:
            print(f"Cannot write to {file_path}. Check file permissions or if the file is open elsewhere.")


        

    def read_data(self) -> pd.DataFrame:
        data = pd.read_excel('data.xlsx', sheet_name=self.sheet_name, dtype=str)
        columns = ['group', 'training_time', 'date', 'exercise', \
                   'variation', 'weight', 'reps', 'total_time', \
                    'distance', 'speed', 'slope', 'notes']
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

    def total_weight_lifted_last_5(self) -> pd.DataFrame:
        total_weight_lifted = pd.DataFrame()
        total_weight_lifted['exercise'] = self.data['exercise'].unique()
        for exercise in self.data['exercise'].unique():
            exercise_data = self.weight_trend_data(exercise)
            total_weight_lifted.loc[total_weight_lifted['exercise'] == exercise, 'total_weight_lifted'] = \
                (exercise_data['weight'] * exercise_data['reps']).tail(5).sum()
        return total_weight_lifted
    
    def total_weight_lifted_preceding_5(self) -> pd.DataFrame:
        total_weight_lifted = pd.DataFrame()
        total_weight_lifted['exercise'] = self.data['exercise'].unique()
        for exercise in self.data['exercise'].unique():
            exercise_data = self.weight_trend_data(exercise)
            total_weight_lifted.loc[total_weight_lifted['exercise'] == exercise, 'total_weight_lifted'] = \
                (exercise_data['weight'] * exercise_data['reps']).tail(10).sum()
            total_weight_lifted.loc[total_weight_lifted['exercise'] == exercise, 'total_weight_lifted'] = \
                total_weight_lifted.loc[total_weight_lifted['exercise'] == exercise, 'total_weight_lifted'].values[0] - \
                self.total_weight_lifted_last_5().loc[self.total_weight_lifted_last_5()['exercise'] == exercise, 'total_weight_lifted'].values[0]
        return total_weight_lifted
    

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
        
        # Average weight column 
        for exercise in unique_exercises:
            exercise_data = self.weight_trend_data(exercise)
            unique_exercise_data.loc[unique_exercise_data['exercise'] == exercise, 'average_weight'] = \
                exercise_data['weight'].mean()
            
        # Average weight last 5 runs
        for exercise in unique_exercises:
            exercise_data = self.weight_trend_data(exercise)
            unique_exercise_data.loc[unique_exercise_data['exercise'] == exercise, 'average_weight_last_5_runs'] = \
                exercise_data['weight'].tail(5).mean()
            
        # growth percentage of the total weight lifted in the last 5 runs compared to the preceding 5 runs
        total_weight_lifted_last_5 = self.total_weight_lifted_last_5()
        total_weight_lifted_preceding_5 = self.total_weight_lifted_preceding_5()
        unique_exercise_data['growth_percentage'] = \
            (total_weight_lifted_last_5['total_weight_lifted']) / \
            total_weight_lifted_preceding_5['total_weight_lifted'] * 100

            
        unique_exercise_data.rename(columns={'exercise': 'Exercise', 'count': 'Count', 'max_weight': 'Max Weight', \
                                             'max_weight_reps': 'Max Weight Reps', 'average_weight': 'Average Weight', \
                                             'average_weight_last_5_runs': 'Average Weight Last 5 Runs','growth_percentage': 'Growth Percentage'}, inplace=True)
        return unique_exercise_data

    def group_exercise_data(self) -> pd.DataFrame:
        self.data['group'] = self.data['group'].fillna('No group')
        group_exercise_data = pd.DataFrame()
        # Find the unique groups in the data by splicing and exploding the 'group' column
        unique_groups = self.data['group'].str.split('+').explode()
        unique_groups = unique_groups.str.strip().unique()


        group_exercise_data['group'] = unique_groups
        for group in unique_groups:
            group_data = self.data.loc[self.data['group'] == group]
            group_exercise_data.loc[group_exercise_data['group'] == group, 'count'] = len(group_data)
            group_exercise_data.loc[group_exercise_data['group'] == group, 'average_weight'] = \
                group_data['weight'].apply(lambda x: sum(x) / len(x)).mean()
            group_exercise_data.loc[group_exercise_data['group'] == group, 'average_weight_last_5'] = \
                group_data['weight'].apply(lambda x: sum(x) / len(x)).tail(5).mean()
            group_exercise_data.loc[group_exercise_data['group'] == group, 'growth_percentage'] = \
                (group_exercise_data.loc[group_exercise_data['group'] == group, 'average_weight_last_5'].values[0] / \
                    group_exercise_data.loc[group_exercise_data['group'] == group, 'average_weight'].values[0]) * 100
            
        # Round the growth percentage to 2 decimal places
        group_exercise_data['growth_percentage'] = group_exercise_data['growth_percentage'].round(2)

        # Rename the columns
        group_exercise_data.rename(columns={'group': 'Group', 'count': 'Count', 'average_weight': 'Average Weight', \
                                            'average_weight_last_5': 'Average Weight Last 5', 'growth_percentage': 'Growth Percentage'}, inplace=True)
        
        return group_exercise_data
    
    
    def plot_weight_trend(self, exercise: str) -> Tuple[plt.Figure, plt.Axes]:
        exercise_data = self.weight_trend_data(exercise)
        fig, ax = plt.subplots()
        ax.scatter(exercise_data['date'], exercise_data['weight'], s=exercise_data['reps']*10, \
                   c=exercise_data['reps'], cmap='rainbow', alpha=0.5)
        ax.set_xlabel('Date')
        ax.set_ylabel('Weight (kg)')
        colorbar = plt.colorbar(ax.collections[0])
        colorbar.set_label('Reps')
        ax.set_title(f'Weight trend of the exercise {exercise}')

        # Set the x-ticks and x-tick labels with a rotation
        xticks = ax.get_xticks()
        ax.set_xticks(xticks)  # Explicitly set the x-ticks to match the labels
        ax.set_xticklabels(ax.get_xticks(), rotation=45)  # Now set the labels with rotation
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
        return fig, ax
        
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
            lambda x: int(x.split(':')[0]) * 60 + int(x.split(':')[1]) if pd.notnull(x) else 0
        )

        # Convert 'total_time_delta' to a timedelta object
        running_data['total_time_delta'] = pd.to_timedelta(running_data['total_time_delta'], unit='s')


        # Calculate speed and distance based on available data
        for k, v in running_data.loc[:, ['date', 'total_time_delta', 'distance', 'speed']].iterrows():
            if v['total_time_delta'] != pd.Timedelta(seconds=0) and pd.notnull(v['distance']):
                running_data.loc[k, 'speed'] = float(v['distance']) / (float(v['total_time_delta'].total_seconds()) / 3600)
            elif v['total_time_delta'] != pd.Timedelta(seconds=0) and pd.notnull(v['speed']):
                pass # speed is already calculated
            #     # Ensure 'v['speed']' is treated as a float
            #     speed_as_float = float(v['speed'])
            #     running_data.loc[k, 'distance'] = speed_as_float * (v['total_time_delta'].seconds / 3600)   
            elif pd.notnull(v['distance']) and pd.notnull(v['speed']):
                running_data.loc[k, 'total_time_delta'] = pd.to_timedelta(seconds=(v['distance'] / v['speed']) * 3600, unit='s')
            else:
                logging.warning(f"Row {k} has missing values for 'total_time_delta', 'distance', and 'speed'")

        # Calculate pace for each row
        total_seconds = running_data['total_time_delta'].dt.total_seconds()
        running_data['distance_float'] = running_data['distance'].astype(float)
        valid_times = total_seconds != 0
        running_data.loc[valid_times, 'pace'] = \
            (total_seconds[valid_times] / 60) / running_data.loc[valid_times, 'distance_float']
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
                # Add average pace
                unique_running_data.loc[unique_running_data['distance'] == distance, 'average_pace'] = \
                    running_data.loc[running_data['distance'] == distance, 'pace'].mean()
                # Add average pace last 5 runs
                unique_running_data.loc[unique_running_data['distance'] == distance, 'average_pace_last_5_runs'] = \
                    running_data.loc[running_data['distance'] == distance, 'pace'].tail(5).mean()
                # Percentage change in average pace
                unique_running_data.loc[unique_running_data['distance'] == distance, 'percentage_change'] = \
                    (unique_running_data.loc[unique_running_data['distance'] == distance, 'average_pace'].values[0] / \
                    unique_running_data.loc[unique_running_data['distance'] == distance, 'average_pace_last_5_runs'].values[0]) * 100
                
        # Round percentage change to 2 decimal places
        unique_running_data['percentage_change'] = unique_running_data['percentage_change'].round(2)



        # Convert pace from seconds to mm:ss
        def pace_seconds_to_mm_ss(column_name: str) -> None:
            unique_running_data[column_name] = unique_running_data[column_name].apply(
            lambda x: f"{int(x)}:{int((x - int(x)) * 60):02d}"
            ) 
        # Min pace format to mm:ss
        pace_seconds_to_mm_ss('min_pace')
        # Average pace format to mm:ss
        pace_seconds_to_mm_ss('average_pace')
        # Average pace last 5 runs format to mm:ss
        pace_seconds_to_mm_ss('average_pace_last_5_runs')

        unique_running_data.rename(columns={'distance': 'Distance (km)', 'count': 'Count', 'min_pace': 'Min Pace', \
                                            'average_pace': 'Average Pace', 'average_pace_last_5_runs': 'Average Pace last 5 runs'}, inplace=True)
        return unique_running_data

    def plot_pace_trend(self, distance: Union[str, List[str]] = '3') -> Tuple[plt.Figure, plt.Axes]:
        if isinstance(distance, str):
            distance = [distance]
        run_data = self.running_data()
        run_data = run_data.loc[run_data['distance'].isin(distance)]
        fig, ax = plt.subplots()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
        for d in distance:
            ax.plot(run_data.loc[run_data['distance'] == d, 'date'], run_data.loc[
                run_data['distance'] == d, 'pace'], '-', marker='o', label=f'{d} km')
        ax.set_xlabel('Date')
        ax.set_ylabel('Pace (min per km)')
        ax.set_title(f'Pace trend for different distances')
        ax.tick_params(axis='x', rotation=45)
        ax.legend()
        return fig, ax

#%%
if __name__ == "__main__":
    # Load and clean the data
    loader = DataLoader('Sports')
    loader.update_data(r"C:\Users\User\Documenten\Version2\Data.xlsx", 'Sports')
    data = loader.read_data()
    cleaned_data = loader.clean_data(data)


# %%
