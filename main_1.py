#%%
import pandas as pd
import matplotlib.pyplot as plt
import logging
import matplotlib.dates as mdates
from typing import Tuple, List

plt.style.use('bmh')
logging.basicConfig(level=logging.INFO)

class DataLoader:
    def __init__(self, file_path: str, sheet_name: str) -> None:
        self.file_path = file_path
        self.sheet_name = sheet_name

    def read_data(self) -> pd.DataFrame:
        data = pd.read_excel(self.file_path, sheet_name=self.sheet_name, dtype=str)
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
        plt.scatter(exercise_data['date'], exercise_data['weight'], s=exercise_data['reps']*10, c=exercise_data['reps'], cmap='rainbow', alpha=0.5)
        plt.xlabel('Date')
        plt.ylabel('Weight (kg)')
        plt.colorbar(label='Reps')
        plt.title(f'Weight trend of the exercise {exercise}')
        plt.xticks(rotation=45)
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

    def plot_time_trend_run(self, distance: str = '3') -> Tuple[plt.Figure, plt.Axes]:
        run_data = self.data.loc[self.data['exercise'] == 'Run']
        run_data = run_data.loc[run_data['distance'] == distance]
        run_data['total_time'] = run_data['total_time'].apply(lambda x: int(x.split(':')[0]) + int(x.split(':')[1])/60)
        fig, ax = plt.subplots()
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d'))
        plt.plot(run_data['date'], run_data['total_time'], 'r-', marker='o')
        plt.xlabel('Date')
        plt.ylabel('Total time (min)')
        plt.title('Total time spent running for 3km')
        plt.xticks(rotation=45)
        return fig, ax

    def unique_running_data(self) -> pd.DataFrame:
        running_data = self.data.loc[self.data['exercise'] == 'Run']
        #convert 'total_time' from mm:ss to minutes
        running_data['total_time'] = running_data['total_time'].apply(lambda x: int(x.split(':')[0]) + int(x.split(':')[1])/60)
        running_data['total_time'] = running_data['total_time'].astype(float)  # Ensure 'total_time' is float

        unique_running_data = pd.DataFrame()
        unique_running_data['distance'] = running_data['distance'].unique()
        unique_running_data['count'] = unique_running_data['distance'].apply(
            lambda x: len(running_data.loc[running_data['distance'] == x]))
        return unique_running_data
#%%
if __name__ == "__main__":
    loader = DataLoader(r"C:\Users\User\Documents\Version2\Data.xlsx", 'Sports')
    data = loader.read_data()
    cleaned_data = loader.clean_data(data)


    #print distance,speed and total_time for each row
    cleaned_data['distance'] = cleaned_data['distance'].astype(float)
    cleaned_data['speed'] = cleaned_data['speed'].astype(float)
    cleaned_data['total_time'] = cleaned_data['total_time'].astype(str)

    print(cleaned_data[['distance', 'speed', 'total_time']])

#%%
    # Ensure the 'total_time' column is converted from mm:ss to hours
    cleaned_data['total_time'] = cleaned_data['total_time'].apply(lambda x: int(x.split(':')[0]) + int(x.split(':')[1])/60 if isinstance(x, str) else x)

    # Fill the NaN values in speed, distance, and total_time based on the other two values
    cleaned_data['speed'] = cleaned_data.apply(
        lambda row: int(row['distance']) / row['total_time'] if pd.isna(row['speed']) and pd.notna(row['distance']) and pd.notna(row['total_time']) else row['speed'],
        axis=1
    )
    cleaned_data['distance'] = cleaned_data.apply(
        lambda row: row['speed'] * row['total_time'] if pd.isna(row['distance']) and pd.notna(row['speed']) and pd.notna(row['total_time']) else row['distance'],
        axis=1
    )
    cleaned_data['total_time'] = cleaned_data.apply(
        lambda row: row['distance'] / row['speed'] if pd.isna(row['total_time']) and pd.notna(row['distance']) and pd.notna(row['speed']) else row['total_time'],
        axis=1
    )

    exercise_analysis = ExerciseAnalysis(cleaned_data)
    unique_exercise_data = exercise_analysis.unique_exercise_data()

    run_analysis = RunAnalysis(cleaned_data)
    fig, ax = run_analysis.plot_time_trend_run()
    unique_running_data = run_analysis.unique_running_data()
    print(unique_running_data)
# %%
    fig, ax = exercise_analysis.plot_weight_trend('Squat', show=True)
    print(unique_exercise_data)
# %%
